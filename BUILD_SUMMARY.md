# Build Summary - Medbridge AI Health Coach

## Project Status: COMPLETE

## What Was Built

### Backend (FastAPI + LangGraph)
- FastAPI application with lifespan pattern (not deprecated @app.on_event)
- LangGraph-based deterministic state machine with 5 phases: PENDING, ONBOARDING, ACTIVE, RE_ENGAGING, DORMANT
- Non-negotiable safety guard: keyword-based mental health crisis detection and clinical content redirect
- SQLAlchemy 1.4 ORM with session.query() style (not 2.0 select())
- PostgreSQL via psycopg2-binary with postgresql:// prefix
- Full CRUD for patients, coaching sessions, and webhook endpoints
- Agent tools: set_goal, set_reminder, get_program_summary, get_adherence_summary, alert_clinician

### Frontend (React)
- Clinical dashboard with patient search and phase statistics
- New Patient creation form with consent verification
- Patient detail page with engagement summary, phase timeline, and safety alerts
- Real-time chat session interface with safety flag indicators
- API client connecting to backend on port 3007
- CORS middleware configured for frontend-backend communication

### Tests (pytest)
- 82 tests, 0 failures
- Coverage: health check, patient CRUD, sessions, webhooks, safety guard, state machine routing
- Parametrized tests for all mental health and clinical trigger keywords
- Integration tests for full phase transition workflows

## Technical Decisions
- SQLAlchemy 1.4 style (session.query) as required
- psycopg2-binary with postgresql:// prefix
- FastAPI lifespan pattern
- Safety guard uses keyword matching (not LLM) for reliability and zero latency
- Phase transitions are deterministic application logic, never LLM decisions
- SQLite used for test isolation

## Port Configuration
- API: 3007
- Frontend: 3000
- Database: medbridge_coach

## Makefile Targets
- `make dev` - Start backend API on port 3007
- `make dev-frontend` - Start React frontend on port 3000
- `make test` - Run 82 tests
- `make seed` - Seed sample patient data
- `make build` - Install all dependencies
- `make clean` - Remove caches and build artifacts
