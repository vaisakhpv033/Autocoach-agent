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

## Production Deployment with Docker Compose

When using **LiveKit Cloud**, you only need to run the **AutoCoach Agent Worker** container. The worker makes an outbound WebSocket connection to LiveKit Cloud, meaning **zero public inbound ports** or local SFU containers are required.

### 1. Build and Run Container
Ensure your [.env](file:///e:/Brocamp/After_brocamp/AutoCoach/AutoCoach/.env) contains your `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, and `GOOGLE_API_KEY`, then run:
```bash
docker compose up --build -d
```

### 2. View Logs
```bash
docker compose logs -f autocoach-agent
```

### 3. Health Check Probe
The worker exposes an internal HTTP health check probe on port `8085` (bound to localhost `127.0.0.1:8085` to avoid port collisions):
```bash
curl http://127.0.0.1:8085/
# Returns: OK

curl http://127.0.0.1:8085/worker
# Returns JSON worker metrics: active jobs, load, etc.
```

---

## Built-in Dental Training Scenarios

AutoCoach includes comprehensive, out-of-the-box dental front desk & patient coordinator training presets derived directly from clinic Standard Operating Procedures (SOPs):

| Scenario Key | Description | Key Challenges & Objectives Tested |
| :--- | :--- | :--- |
| `dental_scheduling` *(Default)* | All-rounder new patient scheduling | Exam + cleaning, existing X-ray policy (6 months, 48 hrs prior), $1 reservation hold. |
| `dental_price_shopper` | Inquiring about root canal & crown pricing | Prohibits phone price quotes without exam; explains swelling/abscess; explains prepayment policy. |
| `dental_frontdesk_compliance` | Caller demanding to speak with doctor | Prohibits putting caller on hold; explains doctor is with a patient; addresses $85 balance due. |
| `dental_clinical_objections` | Direct treatment & external X-rays | Enforces doctor's independent exam before treatment; explains 6-month validity for external X-rays. |
| `dental_emergency_triage` | Acute toothache trying to delay | Creates urgency (infections flare up on weekends); advises caller not to chew on affected side. |
| `dental_insurance_copay` | Perio maintenance vs routine cleaning copay | Explains clinical difference between prophylaxis (healthy gums) and perio maintenance (active infection). |

### Optional Dual-Sided Evaluation Rubrics
- **Zero Token Overhead**: Built-in rubrics are local data structures and are **never sent to Gemini 3.8 Live** during the call, consuming zero live tokens.
- **Post-Call Verification**: The session evaluation report automatically includes the scenario's SOP rubric (or custom rubric from metadata) so automated LLM evaluators or supervisors can immediately grade the call transcript.

---

## Language Modes (English, Spanish & Spanglish)

AutoCoach supports 3 primary language modes configured dynamically via metadata:

1. **Pure US English (`"language": "en-US"`)**:
   Standard American English dialogue.
   ```json
   {
     "language": "en-US",
     "scenario": "dental_scheduling"
   }
   ```

2. **Pure US Spanish (`"language": "es-US"` or `"spanish"`)**:
   The caller speaks entirely in Spanish, directly testing the clinic's Spanish caller SOP:
   ```json
   {
     "language": "es-US",
     "scenario": "dental_frontdesk_compliance"
   }
   ```
   *Expected Trainee SOP Response*: *"Lo siento muchísimo. Yo no hablo español. Please hold, let me transfer your call..."*

3. **Spanglish / Code-Mixing (`"language": "spanglish"` or `"code_mixing": true`)**:
   The caller naturally code-switches between US Spanish and American English, mimicking real-world bilingual patients:
   ```json
   {
     "language": "spanglish",
     "scenario": "dental_price_shopper"
   }
   ```
   *(Or alternatively: `{"language": "es-US", "code_mixing": true}`)*

---

## Dynamic Metadata API

When creating a room or dispatching a job, you can pass custom metadata as a JSON string to dynamically tailor the simulated customer without changing any code:

```json
{
  "scenario": "dental_price_shopper",
  "name": "Michael Reynolds",
  "difficulty": "hard",
  "voice": "Charon",
  "language": "spanglish",
  "custom_instructions": "Ask if the doctor can prescribe painkillers over the phone. If the trainee refuses politely, accept.",
  "compliance_traps": [
    "Refuse to provide a card for the $1 hold and ask if you can pay cash upon arrival"
  ],
  "reports_webhook_url": "https://your-lms.com/api/evaluations/webhook"
}
```



