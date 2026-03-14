# Medbridge AI Health Coach

An AI-powered health coaching agent that keeps patients engaged with their Home Exercise Programs (HEPs) between clinical visits. Built with FastAPI, LangGraph state machine, and a non-negotiable safety guard layer.

## Architecture

- **Backend**: Python + FastAPI + LangGraph deterministic state machine
- **Frontend**: React clinical dashboard
- **Database**: PostgreSQL (SQLAlchemy 1.4)
- **Safety**: Keyword-based safety guard on every agent response (mental health crisis detection, clinical content redirect)

### Phase State Machine
```
PENDING --> ONBOARDING --> ACTIVE --> RE_ENGAGING --> DORMANT
                            ^            |              |
                            |____________|              |
                            |___________________________|
```

Phase transitions are **application logic**, not LLM decisions. The router is deterministic.

## Quick Start

```bash
# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
make build

# Seed sample data
make seed

# Run the API server (port 3007)
make dev

# Run the frontend (port 3000)
make dev-frontend

# Run tests
make test
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/patients` | Create patient |
| GET | `/patients/{id}` | Get patient |
| PATCH | `/patients/{id}` | Update patient |
| POST | `/patients/{id}/sessions` | Chat with coach |
| GET | `/patients/{id}/summary` | Clinician summary |
| POST | `/webhooks/schedule` | Trigger check-in |
| POST | `/webhooks/clinician-alert` | Escalation alert |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Claude API key |
| `JWT_SECRET` | JWT signing secret |
| `PORT` | API server port (default: 3007) |

## Safety Guard

Every agent response passes through the safety guard before delivery:
- **Mental health triggers** (suicidal, self-harm, crisis) -> 988 Lifeline reference + clinician alert
- **Clinical content** (symptoms, medication, diagnosis) -> redirect to care team
- No bypass path exists in the architecture

## Tests

82 tests covering:
- Health check endpoint
- Patient CRUD and summary
- Coaching sessions and phase transitions
- Webhook endpoints
- Safety guard (all trigger categories)
- Deterministic state machine routing
