# Medbridge AI Health Coach — Architecture Document

## Overview

The Medbridge AI Health Coach is a webhook-driven backend service that keeps patients engaged with their Home Exercise Programs (HEPs) between clinical visits. It uses a LangGraph-based state machine agent with deterministic phase routing and a non-negotiable safety guard layer.

**Stack:** Python 3.11+ | FastAPI | LangGraph | SQLAlchemy 1.4 | PostgreSQL | psycopg2-binary

**Key Principle:** Phase transitions are APPLICATION LOGIC, not LLM decisions. The LLM handles conversation. Python handles state transitions.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Server                       │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Patient API  │  │ Webhook API  │  │  Health API   │  │
│  │             │  │              │  │               │  │
│  │ POST /patients/:id/sessions  │  │ GET /health   │  │
│  │ GET  /patients/:id/summary   │  │               │  │
│  │             │  │ POST /webhooks/schedule        │  │
│  │             │  │ POST /webhooks/clinician-alert │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘  │
│         │                │                              │
│  ┌──────▼────────────────▼──────┐                       │
│  │       LangGraph Agent        │                       │
│  │                              │                       │
│  │  RouterGraph (deterministic) │                       │
│  │    ├── OnboardingGraph       │                       │
│  │    ├── ActiveGraph           │                       │
│  │    ├── ReEngagingGraph       │                       │
│  │    └── DormantGraph          │                       │
│  │                              │                       │
│  │  SafetyGuard (ALL outputs)   │                       │
│  │                              │                       │
│  │  Tools:                      │                       │
│  │    set_goal                  │                       │
│  │    set_reminder              │                       │
│  │    get_program_summary       │                       │
│  │    get_adherence_summary     │                       │
│  │    alert_clinician           │                       │
│  └──────────────┬───────────────┘                       │
│                 │                                       │
│  ┌──────────────▼───────────────┐                       │
│  │     SQLAlchemy 1.4 ORM       │                       │
│  │     (session.query style)    │                       │
│  └──────────────┬───────────────┘                       │
│                 │                                       │
└─────────────────┼───────────────────────────────────────┘
                  │
         ┌────────▼────────┐
         │   PostgreSQL    │
         └─────────────────┘
```

---

## Data Models

### Patient
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| external_id | String | External patient identifier |
| name | String | Patient display name |
| email | String (nullable) | Patient email |
| phase | Enum | PENDING, ONBOARDING, ACTIVE, RE_ENGAGING, DORMANT |
| goal | String (nullable) | Patient's coaching goal |
| consent_verified | Boolean | Must be True before any interaction |
| unanswered_count | Integer | Consecutive unanswered check-ins (0-3+) |
| last_interaction | DateTime (nullable) | Last patient interaction timestamp |
| program_summary | JSON (nullable) | Cached HEP program data |
| created_at | DateTime | Record creation |
| updated_at | DateTime | Last update |

### Session
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| patient_id | UUID (FK) | References Patient |
| phase | String | Phase at time of session |
| messages | JSON | Conversation messages array |
| created_at | DateTime | Session start |
| updated_at | DateTime | Last message time |

### PhaseTransitionLog
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| patient_id | UUID (FK) | References Patient |
| from_phase | String | Previous phase |
| to_phase | String | New phase |
| reason | String | Transition reason |
| created_at | DateTime | Transition timestamp |

### ClinicianAlert
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| patient_id | UUID (FK) | References Patient |
| alert_type | String | mental_health_crisis, clinical_concern, etc. |
| message | Text | Triggering message content |
| resolved | Boolean | Whether alert has been addressed |
| created_at | DateTime | Alert timestamp |

---

## API Contracts

### GET /health
Health check endpoint.
```json
Response 200:
{
  "status": "healthy",
  "service": "medbridge-health-coach",
  "version": "1.0.0"
}
```

### POST /patients/{patient_id}/sessions
Start or continue a coaching session.
```json
Request:
{
  "message": "Hi, I'd like to start my exercises"
}

Response 200:
{
  "session_id": "uuid",
  "patient_id": "uuid",
  "phase": "ONBOARDING",
  "response": "Welcome! I'm your health coach...",
  "safety_flagged": false
}
```

### GET /patients/{patient_id}/summary
Get patient engagement summary for clinicians.
```json
Response 200:
{
  "patient_id": "uuid",
  "name": "Jane Doe",
  "current_phase": "ACTIVE",
  "goal": "Complete daily stretching routine",
  "total_sessions": 12,
  "unanswered_count": 0,
  "last_interaction": "2026-03-14T10:00:00Z",
  "phase_history": [
    {"from": "PENDING", "to": "ONBOARDING", "at": "2026-03-01T..."},
    {"from": "ONBOARDING", "to": "ACTIVE", "at": "2026-03-03T..."}
  ],
  "alerts": []
}
```

### POST /webhooks/schedule
Time-based check-in trigger (called by external scheduler).
```json
Request:
{
  "patient_id": "uuid",
  "trigger_type": "scheduled_checkin"
}

Response 200:
{
  "status": "processed",
  "patient_id": "uuid",
  "action_taken": "checkin_sent"
}
```

### POST /webhooks/clinician-alert
Urgent escalation endpoint.
```json
Request:
{
  "patient_id": "uuid",
  "alert_type": "mental_health_crisis",
  "message": "Patient triggered safety concern",
  "source": "safety_guard"
}

Response 200:
{
  "status": "received",
  "alert_id": "uuid"
}
```

### CRUD Endpoints
- **POST /patients** — Create a new patient
- **GET /patients/{patient_id}** — Get patient details
- **PATCH /patients/{patient_id}** — Update patient (e.g., consent)

---

## LangGraph Agent Design

### Phase State Machine
```
PENDING ──(consent_verified)──→ ONBOARDING
ONBOARDING ──(goal_set)──→ ACTIVE
ACTIVE ──(1 unanswered)──→ RE_ENGAGING
RE_ENGAGING ──(response)──→ ACTIVE
RE_ENGAGING ──(3 unanswered)──→ DORMANT
DORMANT ──(response)──→ RE_ENGAGING
```

### Routing Logic (Deterministic)
1. If `consent_verified == False` → END (no interaction)
2. If `phase == PENDING` → ONBOARDING
3. If `goal is set and phase == ONBOARDING` → ACTIVE
4. If `unanswered_count >= 3` → DORMANT
5. If `unanswered_count >= 1` → RE_ENGAGING
6. Otherwise → current phase handler

### Safety Guard (Non-negotiable)
Every agent response passes through SafetyGuard before delivery:
- Mental health triggers → immediate clinician alert + safe response
- Clinical content triggers → redirect to care team
- No bypass path exists

### Tools
| Tool | Description |
|------|-------------|
| set_goal | Sets the patient's coaching goal |
| set_reminder | Creates a reminder for the patient |
| get_program_summary | Retrieves HEP program details |
| get_adherence_summary | Gets exercise adherence stats |
| alert_clinician | Sends urgent alert to care team |

---

## Project Structure
```
medbridge-health-coach/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with lifespan
│   ├── config.py             # Settings from .env
│   ├── database.py           # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patient.py        # Patient model
│   │   ├── session.py        # Session model
│   │   ├── alert.py          # ClinicianAlert model
│   │   └── phase_log.py      # PhaseTransitionLog model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── patient.py        # Pydantic schemas
│   │   ├── session.py
│   │   └── webhook.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py         # GET /health
│   │   ├── patients.py       # Patient CRUD + sessions
│   │   └── webhooks.py       # Webhook endpoints
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── state.py          # PatientState TypedDict
│   │   ├── router.py         # Deterministic phase router
│   │   ├── graphs/
│   │   │   ├── __init__.py
│   │   │   ├── onboarding.py
│   │   │   ├── active.py
│   │   │   ├── re_engaging.py
│   │   │   └── dormant.py
│   │   ├── safety_guard.py   # SafetyGuard (non-negotiable)
│   │   ├── tools.py          # Agent tools
│   │   └── workflow.py       # Main LangGraph workflow
│   └── services/
│       ├── __init__.py
│       ├── patient_service.py
│       └── session_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_patients.py
│   ├── test_sessions.py
│   ├── test_webhooks.py
│   ├── test_safety_guard.py
│   └── test_state_machine.py
├── .env.example
├── Makefile
├── requirements.txt
└── ARCHITECTURE.md
```

---

## Design Decisions / Deviations

1. **SQLAlchemy 1.4 style** — Using `session.query(Model)` pattern as required, not 2.0 `select()` style.
2. **psycopg2-binary** — Using `postgresql://` connection prefix.
3. **FastAPI lifespan** — Using `@asynccontextmanager` lifespan pattern, not deprecated `@app.on_event`.
4. **No frontend** — This is a webhook-driven backend only. No React/UI components.
5. **LLM calls stubbed** — Tool invocation logic is real and tested, but actual Claude API calls are stubbed for testability and cost control. The architecture supports swapping in real calls.
6. **Safety guard is synchronous check** — The safety guard uses keyword matching (not LLM-based) for reliability and zero-latency safety checks. This is intentional: safety checks must never depend on an external service being available.

---

## Environment Variables (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/medbridge
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=your-secret-key
ENVIRONMENT=development
LOG_LEVEL=INFO
```
