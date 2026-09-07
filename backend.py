from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path
import re
from typing import Optional
import httpx

app = FastAPI(title="Supra Hospital AI Assistant")

BASE_DIR = Path(__file__).resolve().parent
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-5"
LOCAL_PREVIEW_ENABLED = os.getenv("SUPRA_LOCAL_PREVIEW", "true").casefold() not in {"0", "false", "no"}


class CredentialConfigurationError(Exception):
    """Raised when live AI cannot run because its credential is unavailable."""

# These terms make keyword retrieval less noisy while retaining clinical terms
# such as TKR, DVT, NSAID, and sepsis.
STOP_WORDS = frozenset({
    "a", "an", "and", "are", "at", "be", "before", "can", "could", "do",
    "for", "from", "give", "how", "i", "in", "is", "it", "me", "my", "of",
    "on", "or", "our", "patient", "patients", "please", "should", "the", "to",
    "was", "we", "what", "when", "with", "would", "you", "your",
})
GENERIC_TERMS = frozenset({"care", "management", "medication", "medicine", "pain", "protocol", "surgery"})
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    # The UI is served by this app. Keeping `null` also supports opening
    # frontend.html directly during local development.
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "null"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Load knowledge base
with (BASE_DIR / "knowledge-base.json").open("r", encoding="utf-8") as f:
    KNOWLEDGE_BASE = json.load(f)

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    user_role: str = "Doctor"
    department: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    response: str
    relevant_protocols: list
    relevant_alerts: list
    confidence: str
    reasoning: str
    mode: str = "assistant"
    answer_generated: bool = True
    provider_notice: Optional[str] = None

def _tokens(value: object) -> set[str]:
    """Return normalized, meaningful keywords from a knowledge-base value."""
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    words = TOKEN_PATTERN.findall(str(value).lower())
    return {
        word[:-1] if word.endswith("s") and len(word) > 4 else word
        for word in words
        if len(word) > 1 and word not in STOP_WORDS
    }


def _record_text(record: dict) -> str:
    """Collect searchable text without depending on every optional field."""
    fields = (
        "title", "content", "department", "name", "condition",
        "critical_info", "special_notes", "allergies",
    )
    return " ".join(str(record[field]) for field in fields if record.get(field))


def _has_specific_match(overlap: set[str]) -> bool:
    """Avoid showing a protocol merely because it shares a broad word like pain."""
    return bool(overlap - GENERIC_TERMS)


def search_knowledge_base(query: str, department: Optional[str] = None):
    """Rank protocols and patient alerts by meaningful query keywords.

    The previous exact-substring lookup could not match natural-language
    questions such as the supplied TKR, DVT, Rajan, or Padma test queries.
    """
    query_lower = query.casefold()
    query_terms = _tokens(query)

    relevant_alerts = []
    alert_context_terms: set[str] = set()
    for alert in KNOWLEDGE_BASE["patient_alerts"]:
        alert_terms = _tokens(_record_text(alert))
        name = str(alert.get("name", "")).casefold()
        overlap = query_terms & alert_terms
        if (name and name in query_lower) or _has_specific_match(overlap):
            relevant_alerts.append(alert)
            # A named patient can bring clinically relevant protocol keywords
            # (for example Padma's diabetes and fasting notes) into the search.
            alert_context_terms.update(alert_terms)

    selected_department = (department or "").casefold().strip()
    ranked_protocols = []
    for protocol in KNOWLEDGE_BASE["protocols"]:
        protocol_department = str(protocol.get("department", "")).casefold()

        protocol_terms = _tokens(_record_text(protocol))
        direct_overlap = query_terms & protocol_terms
        alert_overlap = alert_context_terms & protocol_terms
        combined_overlap = direct_overlap | alert_overlap

        if not _has_specific_match(combined_overlap):
            continue

        # Direct query matches always win over an optional department choice.
        # A user asking about post-TKR pain should still see the orthopaedic
        # protocol if a previously selected department was General Medicine.
        score = len(direct_overlap) * 3 + len(alert_overlap)
        if selected_department and selected_department in protocol_department:
            score += 1
        ranked_protocols.append((score, protocol))

    ranked_protocols.sort(key=lambda item: item[0], reverse=True)
    relevant_protocols = [protocol for _, protocol in ranked_protocols[:5]]

    return relevant_protocols, relevant_alerts

def build_context_prompt(query: str, protocols: list, alerts: list, user_role: str):
    """Build a detailed context-aware prompt for Claude"""
    context = f"""You are a specialized AI Assistant for Supra Multi-Specialty Hospital, Hyderabad.

HOSPITAL CONTEXT:
- 200+ beds across 7 departments
- 45 doctors
- Established protocols and procedures

CRITICAL INSTRUCTIONS:
1. ALWAYS prioritize Supra Hospital's specific protocols over generic medical knowledge
2. If a patient alert exists, ALWAYS highlight it prominently
3. For medication decisions, check the formulary and drug interactions
4. Be EXTREMELY cautious with drug interactions (especially Warfarin-NSAID)
5. For post-surgical patients, always mention DVT prophylaxis requirements
6. Never contradict hospital protocols
7. If something goes against Supra's protocol, explicitly state "CAUTION: This differs from Supra Protocol"

RELEVANT SUPRA PROTOCOLS FOR THIS QUERY:
"""
    
    for protocol in protocols:
        context += f"\n- {protocol['title']} (Criticality: {protocol.get('criticality', 'MEDIUM')})"
        context += f"\n  Details: {protocol['content']}"
        if protocol.get('incident'):
            context += f"\n  ⚠️ BASED ON PAST INCIDENT"
    
    if alerts:
        context += "\n\nPATIENT ALERTS (CRITICAL):\n"
        for alert in alerts:
            context += f"\n- Patient: {alert['name']}"
            context += f"\n  Severity: {alert.get('severity', 'UNKNOWN')}"
            context += f"\n  ⚠️ {alert.get('critical_info', alert['condition'])}"
    
    context += f"\n\nUSER ROLE: {user_role}"
    context += f"\n\nQUERY: {query}"
    context += "\n\nProvide a hospital-specific answer that a doctor at Supra would trust."
    
    return context


def build_local_preview(protocols: list, alerts: list) -> str:
    """Create a deterministic reference view when the live model is unavailable.

    This intentionally does not synthesize a diagnosis or treatment plan. It
    only directs the user to the protocol and alert records returned below.
    """
    match_summary = []
    if alerts:
        match_summary.append(f"{len(alerts)} patient alert record(s)")
    if protocols:
        match_summary.append(f"{len(protocols)} hospital protocol record(s)")

    matches = " and ".join(match_summary) if match_summary else "no matching local records"
    return (
        "AI-generated guidance is unavailable. The records below are direct local "
        "protocol and safety-alert matches only; no patient-specific answer has been generated.\n\n"
        f"The local search found {matches}. Verify the current hospital policy and EHR before acting."
    )

async def call_claude_api(prompt: str) -> str:
    """Call Claude and turn upstream failures into useful API errors."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise CredentialConfigurationError(
            "AI-generated guidance is unavailable because ANTHROPIC_API_KEY is not configured."
        )

    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="The AI service timed out. Please try again.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not reach the AI service. Check the server's network connection and try again.",
        ) from exc

    if response.is_error:
        try:
            error_message = response.json().get("error", {}).get("message")
        except ValueError:
            error_message = None
        if response.status_code in {401, 403}:
            raise CredentialConfigurationError(
                "Anthropic rejected the configured API key. Set a valid ANTHROPIC_API_KEY and restart the server."
            )
        detail = error_message or f"The AI service returned HTTP {response.status_code}."
        raise HTTPException(status_code=502, detail=detail)

    try:
        data = response.json()
        return data["content"][0]["text"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response.",
        ) from exc

@app.get("/", include_in_schema=False)
async def root():
    """Serve the web UI so the app runs from one local URL."""
    return FileResponse(BASE_DIR / "frontend.html")


@app.get("/health")
async def health_check():
    return {
        "service": "Supra Hospital AI Assistant",
        "status": "running",
        "endpoints": ["/query", "/protocols", "/alerts", "/formulary"]
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a medical query using hospital context"""
    
    # Search knowledge base
    protocols, alerts = search_knowledge_base(request.query, request.department)
    
    # Build context-aware prompt
    context_prompt = build_context_prompt(
        request.query,
        protocols,
        alerts,
        request.user_role
    )
    
    # Get a live response when possible. The local preview keeps the prototype
    # demonstrable without pretending to generate clinical guidance offline.
    mode = "assistant"
    answer_generated = True
    provider_notice = None
    try:
        assistant_response = await call_claude_api(context_prompt)
    except CredentialConfigurationError as exc:
        if not LOCAL_PREVIEW_ENABLED:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        mode = "protocol_preview"
        answer_generated = False
        provider_notice = str(exc)
        assistant_response = build_local_preview(protocols, alerts)
    
    # Determine confidence and reasoning
    confidence = "NOT_APPLICABLE" if mode == "protocol_preview" else ("HIGH" if (protocols or alerts) else "MEDIUM")
    reasoning = f"Found {len(protocols)} relevant protocols and {len(alerts)} patient alerts"
    if mode == "protocol_preview":
        reasoning += "; AI-generated guidance unavailable, returning direct local records only"
    
    return QueryResponse(
        query=request.query,
        response=assistant_response,
        relevant_protocols=[
            {
                "title": p['title'],
                "criticality": p.get('criticality', 'MEDIUM'),
                "excerpt": p['content'][:200] + "..."
            }
            for p in protocols
        ],
        relevant_alerts=[
            {
                "patient": a['name'],
                "severity": a.get('severity', 'UNKNOWN'),
                "critical_info": a.get('critical_info', a['condition'])
            }
            for a in alerts
        ],
        confidence=confidence,
        reasoning=reasoning,
        mode=mode,
        answer_generated=answer_generated,
        provider_notice=provider_notice,
    )

@app.get("/protocols")
async def get_protocols(department: Optional[str] = None):
    """Get all protocols, optionally filtered by department"""
    protocols = KNOWLEDGE_BASE['protocols']
    if department:
        protocols = [p for p in protocols if department in p.get('department', '')]
    return {"protocols": protocols, "count": len(protocols)}

@app.get("/alerts")
async def get_alerts():
    """Get all patient alerts"""
    return {"alerts": KNOWLEDGE_BASE['patient_alerts'], "count": len(KNOWLEDGE_BASE['patient_alerts'])}

@app.get("/formulary")
async def get_formulary():
    """Get hospital formulary"""
    return KNOWLEDGE_BASE['formulary']

@app.get("/hospital-info")
async def get_hospital_info():
    """Get hospital information"""
    return KNOWLEDGE_BASE['hospital']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
