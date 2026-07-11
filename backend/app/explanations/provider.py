"""Explanation provider with deterministic fallback.

The LLM boundary is enforced: this module cannot create or modify forecasts,
anomaly findings, severity, confidence, owner, or case state. It receives
structured evidence after deterministic engines finish and returns advisory text.
"""

from typing import Literal, TypedDict

from app.core.config import get_settings
from app.explanations.templates import AlertType, Language, render_template


class ExplanationRequest(TypedDict):
    language: Language
    alert_type: AlertType
    provider_code: str
    provider_display_name: str
    structured_evidence: dict[str, object]
    confidence_score: float
    uncertainty: list[str]
    safe_next_step: str


class ExplanationResult(TypedDict):
    text: str
    generated_by: Literal["llm", "deterministic_template"]
    provider_name: str
    timed_out: bool


def explain(request: ExplanationRequest) -> ExplanationResult:
    """Generate an advisory explanation. Always falls back to deterministic template."""
    settings = get_settings()
    provider_name = request["provider_display_name"] or request["provider_code"]
    text = render_template(
        alert_type=request["alert_type"],
        language=request.get("language", "en"),  # type: ignore[arg-type]
        provider_name=provider_name,
        confidence=request["confidence_score"],
    )

    if settings.llm_explanation_enabled and settings.llm_explanation_provider != "none":
        try:
            text = _call_llm(request)
            return ExplanationResult(
                text=text,
                generated_by="llm",
                provider_name=provider_name,
                timed_out=False,
            )
        except Exception:  # noqa: BLE001 — any failure triggers safe fallback
            pass

    return ExplanationResult(
        text=text,
        generated_by="deterministic_template",
        provider_name=provider_name,
        timed_out=False,
    )


def _call_llm(request: ExplanationRequest) -> str:  # pragma: no cover
    """LLM integration placeholder. Not used in MVP (provider=none)."""
    raise NotImplementedError("LLM integration is not enabled")
