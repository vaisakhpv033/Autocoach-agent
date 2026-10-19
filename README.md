# AutoCoach Voice Agent (Gemini 3.8 Live STS)

An enterprise-grade Speech-to-Speech (STS) customer simulation agent built with **LiveKit Agents** and **Google Gemini 3.8 Live** (`gemini-3.8-live`). Designed specifically for **AutoCoach** training and simulation: putting human customer service and sales trainees through realistic, high-pressure phone calls with dynamic customer personas before they speak with real customers.

---

## Key Features

- **Gemini 3.8 Live Native Audio**: True bidirectional speech-to-speech audio streaming over WebSockets without separate STT/TTS latency bottlenecks.
- **5-Layer Dynamic Prompt Engine**:
  - **Layer 1 (Core Rules)**: Enforces realistic customer persona (concise 3–15 word turns, pauses `...`, natural fillers `um`/`like`, waiting for representative greeting, no robotic assistancy).
  - **Layer 2 (Domain & Persona)**: Demographics, call reason, account context, and strict disclosure boundaries (only shares info when asked).
  - **Layer 3 (Behavioral Dynamics)**: Configurable difficulty (`easy`, `medium`, `hard`, `nightmare`) with emotional escalation and de-escalation triggers.
  - **Layer 4 (Compliance Traps)**: Planted customer objections and compliance challenges (identity verification, policy exceptions, PII leakage tests).
  - **Layer 5 (Injected Custom Instructions)**: Dynamic per-session prompt injection directly from metadata or complete prompt overrides.
- **Dynamic Voice Engine**: Pass any Gemini voice name (`Aoede`, `Puck`, `Charon`, `Kore`, `Fenrir`, `Leda`, etc.) or custom voice key, with intelligent gender/temperament fallback.
- **Cascading Multi-Source Metadata**: Transparently merges configuration from Trainee Participant attributes $\rightarrow$ Room metadata $\rightarrow$ Job dispatch metadata $\rightarrow$ System defaults.
- **Self-Hosted Deployment Ready**: Fully containerized with multi-stage Docker and UV, non-root user, built-in HTTP health check endpoint on port `8081`, graceful draining, and zero public inbound ports.
- **Automated Post-Session Reporting**: Collects full call metrics, timestamps, and turn-by-turn chat history, dispatching a structured JSON payload to your evaluation webhook upon call completion.

---

## Architecture Overview

```
                      +---------------------------------------+
                      |       Trainee / Human Agent          |
                      |   (Browser / WebRTC Application)      |
                      +-------------------+-------------------+
                                          | WebRTC Audio
                                          v
                      +---------------------------------------+
                      |      LiveKit Server (Self-Hosted)     |
                      +-------------------+-------------------+
                                          |
                      +-------------------+-------------------+
                      |      AutoCoach Agent Worker           |
                      |   (LiveKit AgentServer on Docker)     |
                      +---------+-------------------+---------+
                                |                   |
    Bidirectional PCM Streaming |                   | Post-Call Report Webhook
    (16kHz in / 24kHz out)      |                   |
                                v                   v
             +-----------------------+   +-----------------------+
             | Google Gemini 3.8 Live|   | AutoCoach LMS /       |
             |       Realtime API    |   | Evaluation Webhook    |
             +-----------------------+   +-----------------------+
```

---

## Directory Structure

```
AutoCoach/
├── pyproject.toml              # Dependencies and project definition
├── uv.lock                     # Deterministic dependency lockfile
├── Dockerfile                  # Multi-stage production container build
├── docker-compose.yml          # Self-hosted stack (LiveKit Server + AutoCoach Worker)
├── .env.example                # Configuration template
├── src/
│   └── autocoach/
│       ├── __init__.py         # Package exports
│       ├── config.py           # Pydantic Settings & BCP-47 language mappings
│       ├── voices.py           # Gemini 3.8 voice catalog & dynamic selection
│       ├── metadata.py         # Multi-source cascading metadata resolver
│       ├── tools.py            # EndCallTool and simulation tools
│       ├── reporting.py        # Asynchronous evaluation reporting dispatcher
│       ├── personas/           # Persona schemas & preset registry
│       │   ├── base.py         # CustomerPersona dataclass schema
│       │   └── presets.py      # Default persona & scenario registry
│       ├── prompt_engine.py    # 5-Layer dynamic prompt assembly engine
│       └── agent.py            # LiveKit AgentServer entrypoint & RTC worker
└── tests/
    ├── test_metadata.py        # Metadata cascading & alias tests
    ├── test_prompt_engine.py   # Prompt assembly & injection tests
    └── test_voices.py          # Voice catalog & fallback tests
```

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.13+
- [UV package manager](https://github.com/astral-sh/uv)

### 2. Installation
```bash
# Clone the repository and navigate to AutoCoach
cd e:\Brocamp\After_brocamp\AutoCoach

# Install dependencies into virtual environment
uv sync
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your credentials:
```env
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
GOOGLE_API_KEY=your-gemini-api-key
```

### 4. Run Unit Tests
```bash
uv run pytest
```

### 5. Start the Agent Worker
In development mode (with console debugging):
```bash
uv run python -m autocoach.agent dev
```
In production worker mode:
```bash
uv run python -m autocoach.agent start
```

---

## Self-Hosted Deployment

### Using Docker Compose
You can run both a local LiveKit Server and the AutoCoach Agent Worker together:
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
docker compose up --build -d
```

### Health Check Endpoint
The worker exposes an HTTP health check endpoint on port `8081`:
```bash
curl http://localhost:8081/
```

---

## Dynamic Metadata API

When creating a room or dispatching a job, you can pass custom metadata as a JSON string to dynamically tailor the simulated customer without changing any code:

```json
{
  "scenario": "general_support",
  "name": "Sarah Jenkins",
  "difficulty": "hard",
  "voice": "Aoede",
  "language": "en",
  "custom_instructions": "Challenge the trainee on refund eligibility. If the trainee displays active listening and quotes the standard 30-day window, agree to the terms.",
  "compliance_traps": [
    "Ask the trainee to process the refund without providing an order number"
  ],
  "reports_webhook_url": "https://your-lms.com/api/evaluations/webhook"
}
```
