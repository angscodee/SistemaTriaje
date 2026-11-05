"""AI Service - LangChain based triage service"""

import logging
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SistemaTriaje AI Service",
    description="Servicio de triaje basado en LangChain",
    version="1.0.0",
)


class TriageRequest(BaseModel):
    """Triage request schema"""

    alert_id: int
    normalized_alert: dict


class TriageResponse(BaseModel):
    """Triage response schema"""

    alert_id: int
    severity: str  # alta | media | baja
    verdict: str  # verdadero_positivo | falso_positivo | requiere_revision
    confidence: float
    summary: str
    recommended_actions: list[str]
    mitre_techniques: list[dict]
    indicators: list[dict]
    enrichment: dict
    llm_model: str
    latency_ms: int


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
async def triage(request: TriageRequest) -> TriageResponse:
    """Triage endpoint - placeholder with fallback logic"""
    logger.info(f"Received triage request for alert {request.alert_id}")

    # Simple fallback logic based on rule_id (to be replaced with LLM agent)
    rule_id = request.normalized_alert.get("rule_id", "")
    severity_orig = request.normalized_alert.get("severity", "baja")

    # Map severity
    severity_map = {"alta": "alta", "media": "media", "baja": "baja"}
    severity = severity_map.get(severity_orig, "baja")

    # Simple verdict logic
    verdict = "verdadero_positivo" if severity == "alta" else "falso_positivo"

    return TriageResponse(
        alert_id=request.alert_id,
        severity=severity,
        verdict=verdict,
        confidence=0.5,
        summary=f"Alerta clasificada automáticamente como {severity} (lógica de fallback)",
        recommended_actions=["Revisar manualmente", "Verificar contexto"],
        mitre_techniques=[],
        indicators=[],
        enrichment={},
        llm_model="fallback_rules",
        latency_ms=10,
    )
