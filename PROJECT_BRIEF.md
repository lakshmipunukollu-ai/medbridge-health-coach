# PROJECT BRIEF
# (Extracted from MASTER_PROJECT_PLAYBOOK.md — your section only)

## SENIOR ENGINEER DECISIONS — READ FIRST

Before any code is written, here are the opinionated decisions made across all 9 projects
and why. An agent should never second-guess these unless given new information.

### Stack choices made
| Project | Backend | Frontend | DB | Deploy | Rationale |
|---------|---------|---------|-----|--------|-----------|
| FSP Scheduler | TypeScript + Node.js | React + TypeScript | PostgreSQL (multi-tenant) | Azure Container Apps | TS chosen over C# — same Azure ecosystem, better AI library support, faster iteration |
| Replicated | Python + FastAPI | Next.js 14 | PostgreSQL + S3 | Docker | Python wins for LLM tooling; Next.js for real-time streaming UI |
| ServiceCore | Node.js + Express | Angular (required) | PostgreSQL | Railway | Angular required — clean REST API behind it |
| Zapier | Python + FastAPI | None (API only + optional React dashboard) | PostgreSQL + Redis | Railway | Redis for event queue durability; Python for DX-first API |
| ST6 | Java 21 + Spring Boot | TypeScript micro-frontend (React) | PostgreSQL | Docker | Java required — Spring Boot is the senior choice; React micro-frontend mounts into PA host |
| ZeroPath | Python + FastAPI | React + TypeScript | PostgreSQL | Render | Python for LLM scanning logic; React for triage dashboard |
| Medbridge | Python + FastAPI + LangGraph | None (webhook-driven) | PostgreSQL | Railway | LangGraph is the correct tool for state-machine AI agents |
| CompanyCam | Python + FastAPI | React + TypeScript | PostgreSQL | Render | Python for CV/ML inference; React for annotation UI |
| Upstream | Django + DRF | React + TypeScript | PostgreSQL | Render | Django for rapid e-commerce scaffolding; built-in admin is a bonus |

### The 4 shared modules — build these FIRST
These are the highest ROI pieces of work. Build them once, copy-scaffold into every project.

1. `shared/llm_client.py` — Claude API wrapper with retry, streaming, structured output parsing
2. `shared/auth/` — JWT auth + role-based guards (Python + TypeScript versions)
3. `shared/state_machine.py` — Generic FSM: states, transitions, guards, event log
4. `shared/queue/` — Job queue pattern: enqueue, dequeue, ack, retry (Redis + Postgres fallback)

### Build order (wave system)
**Wave 0 (Day 1):** Build shared modules. All other waves depend on these.
**Wave 1 (Days 2-3):** Zapier + ZeroPath — establish LLM pipeline + REST API patterns
**Wave 2 (Days 4-5):** Medbridge + Replicated — LLM pipeline variants, more complex AI
**Wave 3 (Days 6-8):** FSP + ST6 — complex business logic, approval flows
**Wave 4 (Days 9-11):** ServiceCore + Upstream + CompanyCam — isolated stacks, finish strong

---

## PROJECT 7: MEDBRIDGE — AI HEALTH COACH
**Company:** Medbridge | **Stack:** Python + FastAPI + LangGraph + PostgreSQL

### Company mission to impress
Medbridge builds clinical education technology. Their Health Coach sits between clinician
visits to keep patients engaged with home exercise programs (HEPs). What will impress them:
the safety boundaries are AIRTIGHT, the state machine is clinically correct, and the
tool-calling architecture shows that you understand agentic AI properly. This is NOT a
chatbot — it is a structured clinical engagement protocol implemented as a LangGraph agent.

### Architecture
```
Railway
├── api (Python + FastAPI)
│   ├── POST /patients/:id/sessions       — start/continue conversation
│   ├── POST /webhooks/schedule           — time-based check-in trigger
│   ├── POST /webhooks/clinician-alert    — urgent escalation endpoint
│   └── GET  /patients/:id/summary        — engagement stats for clinician
└── agent (Python + LangGraph)
    ├── RouterGraph                        — phase router (reads patient state)
    ├── OnboardingGraph                    — welcomes, collects goals
    ├── ActiveGraph                        — regular check-ins
    ├── ReEngagingGraph                    — warm re-engagement after silence
    ├── DormantGraph                       — minimal contact
    ├── SafetyGuard                        — EVERY message passes through this
    └── Tools: set_goal, set_reminder, get_program_summary,
               get_adherence_summary, alert_clinician
```

### The LangGraph agent structure — impress them with proper architecture
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class PatientState(TypedDict):
    patient_id: str
    phase: Literal["PENDING", "ONBOARDING", "ACTIVE", "RE_ENGAGING", "DORMANT"]
    messages: list[dict]
    goal: str | None
    unanswered_count: int          # 1→2→3 triggers dormant
    last_interaction: str | None   # ISO datetime
    consent_verified: bool
    program_summary: dict | None

# The main router — deterministic, NOT LLM-decided
def route_to_phase(state: PatientState) -> str:
    """
    CRITICAL: Phase transitions are APPLICATION LOGIC, not LLM decisions.
    The LLM handles conversation. The app handles state transitions.
    This prevents the LLM from accidentally moving patients to wrong phases.
    """
    if not state["consent_verified"]:
        return END  # Never interact without consent
    
    phase = state["phase"]
    unanswered = state["unanswered_count"]
    
    if phase == "PENDING":
        return "onboarding"
    elif phase == "ONBOARDING" and state["goal"]:
        return "active"  # Goal set → move to active
    elif unanswered >= 3:
        return "dormant"
    elif unanswered >= 1:
        return "re_engaging"
    else:
        return phase.lower()

# Build the graph
workflow = StateGraph(PatientState)
workflow.add_node("router", route_to_phase)
workflow.add_node("onboarding", OnboardingGraph())
workflow.add_node("active", ActiveGraph())
workflow.add_node("re_engaging", ReEngagingGraph())
workflow.add_node("dormant", DormantGraph())
workflow.add_node("safety_guard", SafetyGuard())  # ALL outputs pass through here

workflow.set_entry_point("router")
# All phase outputs → safety guard → response
for phase in ["onboarding", "active", "re_engaging", "dormant"]:
    workflow.add_edge(phase, "safety_guard")
```

### The safety guard — this is non-negotiable
```python
class SafetyGuard:
    """
    EVERY message the agent generates passes through this before delivery.
    This is not optional. This is not skippable. This runs unconditionally.
    
    Medbridge is a clinical company. Clinical content that crosses the line
    creates liability. The safety guard is the most important component.
    """
    
    CLINICAL_TRIGGERS = [
        "symptoms", "medication", "diagnosis", "treatment", "pain",
        "injury", "side effect", "dosage", "doctor", "emergency",
    ]
    
    MENTAL_HEALTH_TRIGGERS = [
        "suicidal", "self-harm", "hopeless", "can't go on", "end it",
        "hurting myself", "depressed", "anxious", "crisis",
    ]
    
    async def check(self, message: str, patient_id: str) -> GuardResult:
        message_lower = message.lower()
        
        # Mental health crisis → immediate clinician alert, safe response
        if any(trigger in message_lower for trigger in self.MENTAL_HEALTH_TRIGGERS):
            await self.alert_clinician(patient_id, "mental_health_crisis", message)
            return GuardResult(
                safe=False,
                override_response=MENTAL_HEALTH_SAFE_RESPONSE,
                alert_sent=True
            )
        
        # Clinical content → redirect to care team
        if any(trigger in message_lower for trigger in self.CLINICAL_TRIGGERS):
            return GuardResult(
                safe=False,
                override_response=CLINICAL_REDIRECT_RESPONSE,
                alert_sent=False
            )
        
        return GuardResult(safe=True)

MENTAL_HEALTH_SAFE_RESPONSE = (
    "I hear that you're going through something really difficult right now. "
    "Please reach out to your care team or call 988 (Suicide & Crisis Lifeline) "
    "if you need immediate support. Your clinician has been notified."
)

CLINICAL_REDIRECT_RESPONSE = (
    "That sounds like something important to discuss with your care team directly. "
    "Please reach out to your clinician — they're the right person to help with this."
)
```

### CLAUDE.md for Medbridge agent
```
You are a senior Python engineer + AI agent architect building the AI Health Coach for Medbridge.

COMPANY MISSION: Keep patients engaged with their home exercise programs between clinical visits.
This is a CLINICAL product. Safety is not a feature — it is a hard constraint.

ARCHITECTURE: LangGraph agent with phase routing. Phases: PENDING→ONBOARDING→ACTIVE→RE_ENGAGING→DORMANT
CRITICAL RULE: Phase transitions are APPLICATION LOGIC, not LLM decisions.
The LLM handles conversation. Python handles state transitions.

THE SAFETY GUARD IS NON-NEGOTIABLE:
- EVERY agent output passes through SafetyGuard before delivery
- Clinical content (symptoms, medication, diagnosis) → redirect to care team
- Mental health crisis triggers → alert_clinician tool + safe response immediately
- No coach interaction without consent_verified = True

TOOL CALLING: set_goal, set_reminder, get_program_summary, get_adherence_summary, alert_clinician
Tool implementations can be stubbed but invocation logic must be real and tested.

NEVER: LLM decides phase transitions, skip safety guard on any path, interact without consent
ALWAYS: Deterministic routing, exponential backoff on unanswered messages (1→2→3→dormant)
```

---


## SHARED MODULES — BUILD THESE IN WAVE 0

### shared/llm_client.py
```python
"""
Shared Claude API client. Used by: Replicated, ZeroPath, Medbridge, CompanyCam, FSP, Upstream.
Copy this file into each Python project that needs it.
"""
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import json

client = anthropic.Anthropic()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def complete(
    prompt: str,
    system: str = "",
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4096,
    as_json: bool = False,
) -> str | dict:
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = message.content[0].text
    if as_json:
        # Strip markdown fences if present
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
    return text

async def analyze_image(
    image_b64: str,
    prompt: str,
    system: str = "",
    model: str = "claude-sonnet-4-20250514",
) -> dict:
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return json.loads(message.content[0].text)
```

### shared/auth.py (Python version)
```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(user_id: str, role: str) -> str:
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
        SECRET_KEY, algorithm=ALGORITHM
    )

def require_role(*roles: str):
    def dependency(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("role") not in roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return dependency

# Usage: @router.get("/admin", dependencies=[Depends(require_role("admin", "manager"))])
```

### shared/state_machine.py
```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from datetime import datetime

S = TypeVar('S')  # State type
E = TypeVar('E')  # Event type

@dataclass
class Transition(Generic[S, E]):
    from_state: S
    event: E
    to_state: S
    guard: Callable | None = None  # optional condition function

class StateMachine(Generic[S, E]):
    def __init__(self, initial: S, transitions: list[Transition]):
        self.state = initial
        self._transitions = {(t.from_state, t.event): t for t in transitions}
        self._log: list[dict] = []

    def transition(self, event: E, context: dict = None) -> S:
        key = (self.state, event)
        t = self._transitions.get(key)
        if not t:
            raise ValueError(f"Invalid transition: {self.state} + {event}")
        if t.guard and not t.guard(context or {}):
            raise ValueError(f"Guard failed: {self.state} + {event}")
        prev = self.state
        self.state = t.to_state
        self._log.append({"from": prev, "event": event, "to": self.state, "at": datetime.utcnow().isoformat()})
        return self.state

    @property
    def history(self) -> list[dict]:
        return self._log.copy()
```

---
