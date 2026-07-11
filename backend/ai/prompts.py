"""All OpenAI prompt templates — centralized for easy tuning."""


def liquidity_alert_bn(provider: str, eta_minutes: int, balance: float, rate: float, recommended_topup: float | None) -> str:
    topup_line = f"নিরাপদভাবে সেবা চালু রাখতে কমপক্ষে ৳{recommended_topup:,.0f} অতিরিক্ত ব্যবস্থা করার পরামর্শ দেওয়া হচ্ছে।" if recommended_topup else ""
    return f"""You are a mobile financial service assistant generating alerts for agents in Bangladesh.

Write a SHORT Bengali (বাংলা script, NOT romanized) alert — maximum 4 sentences.
Rules:
- Use simple, clear language an agent can read quickly.
- Use advisory language: "পারে", "পরামর্শ", "প্রয়োজন" — never commands or accusations.
- End with one safe recommended next step.
- Do NOT mention fraud or make accusations.

Data:
- Provider: {provider.upper()}
- Current balance: ৳{balance:,.0f}
- Estimated time to shortage: {eta_minutes} minutes
- Outflow rate: ৳{rate:,.0f}/minute
{f'- Suggested top-up: ৳{recommended_topup:,.0f}' if recommended_topup else ''}

Write only the Bengali alert text. No English. No explanation."""


def anomaly_alert_bn(provider: str, pattern: str, evidence_summary: str, confidence: float) -> str:
    return f"""You are a mobile financial service assistant generating alerts for field officers in Bangladesh.

Write a SHORT Bengali (বাংলা script) alert about unusual transaction activity — maximum 4 sentences.
Rules:
- Mention at least ONE possible legitimate reason (Eid demand, salary day, high-demand period).
- Use words like "অস্বাভাবিক", "পর্যালোচনা প্রয়োজন" — never "জালিয়াতি" (fraud) or accusations.
- Confidence level: {int(confidence * 100)}% — reflect appropriate uncertainty.
- End with: human review required before any action.

Data:
- Provider: {provider.upper()}
- Pattern detected: {pattern}
- Evidence: {evidence_summary}

Write only the Bengali alert text. No English. No explanation."""


def anomaly_narrative_en(provider: str, evidence: dict) -> str:
    return f"""You are a risk analyst assistant for a mobile financial service.

Write a 2-sentence English explanation of the following unusual transaction pattern for a field officer.
- First sentence: describe what was observed (facts only, no accusations).
- Second sentence: suggest 1-2 possible legitimate reasons, then note that human review is required.
- Do NOT use the word "fraud". Use "unusual", "requires review", "may indicate".

Provider: {provider.upper()}
Evidence: {evidence}

Write only the 2-sentence explanation."""


def whatif_summary_en(provider: str, original_eta: int, new_eta: int, demand_multiplier: float) -> str:
    return f"""You are a liquidity planning assistant.

Write ONE advisory sentence summarizing the impact of increased demand.
- Original estimated time to shortage: {original_eta} minutes
- New estimated time with {demand_multiplier}× demand: {new_eta} minutes
- Provider: {provider.upper()}
- Use careful, advisory language. No alarmism.

Write only the one-sentence advisory."""
