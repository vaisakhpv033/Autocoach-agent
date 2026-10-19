"""AutoCoach Realtime Voice Agent Entrypoint.

Runs an enterprise-grade Speech-to-Speech (STS) LiveKit AgentServer using
Google Gemini 3.8 Live for simulated customer coaching and representative training.
"""

import logging
import os
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.plugins import google
from google.genai import types

from autocoach.config import settings
from autocoach.metadata import extract_session_metadata, SessionMetadata
from autocoach.voices import resolve_voice
from autocoach.prompt_engine import build_system_prompt
from autocoach.tools import build_simulation_tools
from autocoach.reporting import send_session_report

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
)
logger = logging.getLogger("autocoach.agent")

# Initialize AgentServer with self-hosted production configurations
server = AgentServer(
    host=settings.health_check_host,
    port=settings.health_check_port,
    shutdown_process_timeout=settings.shutdown_timeout_seconds,
    load_threshold=settings.worker_load_threshold,
)

# Registry to track per-job metadata for end-of-call reporting
_JOB_METADATA_STORE: dict[str, SessionMetadata] = {}


async def _on_session_end_func(ctx: JobContext) -> None:
    """Callback triggered when the RTC session concludes."""
    job_id = ctx.job.id if ctx.job else "unknown"
    logger.info(f"Session ending for job {job_id}")

    # Retrieve stored metadata or re-extract from context
    meta = _JOB_METADATA_STORE.pop(job_id, None)
    if not meta:
        meta = extract_session_metadata(ctx)

    try:
        await send_session_report(ctx, meta)
    except Exception as e:
        logger.error(f"Error executing on_session_end reporting: {e}", exc_info=True)


@server.rtc_session(agent_name=settings.agent_name, on_session_end=_on_session_end_func)
async def entrypoint(ctx: JobContext):
    """RTC session entrypoint dispatched by LiveKit Server for each room connection."""
    logger.info(f"Connecting to room '{ctx.room.name}' (job: {ctx.job.id if ctx.job else 'N/A'})...")
    await ctx.connect()

    # 1. Resolve cascading metadata from participant, room, job, and defaults
    meta = extract_session_metadata(ctx)
    if ctx.job and ctx.job.id:
        _JOB_METADATA_STORE[ctx.job.id] = meta

    # 2. Resolve Gemini 3.8 Live Voice
    selected_voice = resolve_voice(
        voice=meta.voice,
        gender=meta.gender,
        temperament=meta.temperament,
        default_fallback=settings.default_voice,
    )
    meta.voice = selected_voice  # record resolved voice in metadata for reporting

    # 3. Resolve BCP-47 Language Tag
    bcp47_language = settings.resolve_bcp47_language(meta.language)

    # 4. Compile 5-Layer System Prompt
    system_instructions = build_system_prompt(meta)

    logger.info(
        f"Starting Gemini 3.8 Live session: room='{ctx.room.name}', "
        f"scenario='{meta.scenario}', voice='{selected_voice}', "
        f"language='{bcp47_language}', difficulty='{meta.difficulty}'"
    )

    # 5. Build Tools (EndCallTool for call termination)
    simulation_tools = build_simulation_tools(delete_room=True)

    # 6. Initialize Simulated Customer Agent
    simulated_customer = Agent(
        instructions=system_instructions,
        tools=simulation_tools,
    )

    # 7. Configure Gemini 3.8 Live Realtime Model
    gemini_api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY", "")
    if not gemini_api_key:
        logger.warning(
            "GOOGLE_API_KEY is not set! The Gemini 3.8 Live connection will fail unless authenticated via Vertex AI."
        )

    llm = google.realtime.RealtimeModel(
        model=settings.gemini_model,
        voice=selected_voice,
        temperature=settings.gemini_temperature,
        api_key=gemini_api_key,
        modalities=[types.Modality.AUDIO],
        language=bcp47_language,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                disabled=False,
                silence_duration_ms=800,
            )
        ),
    )

    # 8. Start AgentSession
    session = AgentSession(llm=llm)

    await session.start(
        agent=simulated_customer,
        room=ctx.room,
    )


def main():
    """Main CLI entrypoint for the AutoCoach agent worker."""
    logger.info(f"Starting AutoCoach Agent Worker (agent_name: '{settings.agent_name}')...")
    cli.run_app(server)


if __name__ == "__main__":
    main()
