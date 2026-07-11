"""Explanation module. Deterministic fallback templates with optional LLM integration."""

from app.explanations.provider import ExplanationRequest, ExplanationResult, explain
from app.explanations.templates import render_template

__all__ = ["ExplanationRequest", "ExplanationResult", "explain", "render_template"]
