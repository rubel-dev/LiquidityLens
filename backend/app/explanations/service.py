"""Explanation service — generates advisory text from deterministic engine results.

Fills templates with actual numbers (runway, shortage time, provider name,
confidence) in English and Bangla. No LLM is required or used.
"""

from decimal import Decimal

from app.anomaly.schemas import AnomalyFindingResult
from app.liquidity.schemas import ForecastResult, ForecastScope, RiskLevel


def explain_forecast(result: ForecastResult, provider_name: str) -> tuple[str, str]:
    """Return (english, bangla) advisory explanation for a liquidity forecast."""
    confidence_pct = round(float(result.confidence) * 100)
    runway = result.runway_minutes

    if result.scope == ForecastScope.SHARED_CASH:
        subject_en = "Shared physical cash"
        subject_bn = "ভাগ করা নগদ অর্থ"
    else:
        subject_en = f"{provider_name} e-money balance"
        subject_bn = f"{provider_name} ই-মানি ব্যালেন্স"

    if result.risk_level == RiskLevel.CRITICAL:
        if runway is not None:
            runway_str = _format_runway_en(runway)
            runway_str_bn = _format_runway_bn(runway)
            en = (
                f"{subject_en} has an estimated runway of {runway_str}. "
                f"Confidence: {confidence_pct}%. "
                "This is a critical advisory signal — human review and approved operational "
                "coordination are required immediately. "
                "Do not initiate an automatic transfer or refill."
            )
            bn = (
                f"{subject_bn}-এর আনুমানিক রানওয়ে {runway_str_bn}। "
                f"আস্থা: {confidence_pct}%। "
                "এটি একটি জরুরি পরামর্শমূলক সংকেত — অবিলম্বে মানব পর্যালোচনা এবং "
                "অনুমোদিত অপারেশনাল সমন্বয় প্রয়োজন। "
                "স্বয়ংক্রিয় ট্রান্সফার বা রিফিল শুরু করবেন না।"
            )
        else:
            en = (
                f"{subject_en} shows critical liquidity pressure but runway cannot be estimated. "
                f"Confidence: {confidence_pct}%. Human review required."
            )
            bn = (
                f"{subject_bn}-এ গুরুতর তারল্য চাপ দেখা যাচ্ছে তবে রানওয়ে অনুমান করা যাচ্ছে না। "
                f"আস্থা: {confidence_pct}%। মানব পর্যালোচনা প্রয়োজন।"
            )
    elif result.risk_level == RiskLevel.WARNING:
        runway_str = _format_runway_en(runway) if runway is not None else "unknown"
        runway_str_bn = _format_runway_bn(runway) if runway is not None else "অজানা"
        en = (
            f"{subject_en} estimated runway is {runway_str}. "
            f"Confidence: {confidence_pct}%. "
            "Review is recommended before the situation becomes critical. "
            "No automatic financial action should be taken."
        )
        bn = (
            f"{subject_bn}-এর আনুমানিক রানওয়ে {runway_str_bn}। "
            f"আস্থা: {confidence_pct}%। "
            "পরিস্থিতি গুরুতর হওয়ার আগে পর্যালোচনা করার পরামর্শ দেওয়া হচ্ছে। "
            "কোনো স্বয়ংক্রিয় আর্থিক পদক্ষেপ নেওয়া উচিত নয়।"
        )
    elif result.risk_level == RiskLevel.WATCH:
        en = (
            f"{subject_en} is within watch threshold. "
            f"Confidence: {confidence_pct}%. Monitor for further pressure."
        )
        bn = (
            f"{subject_bn} পর্যবেক্ষণ সীমার মধ্যে রয়েছে। "
            f"আস্থা: {confidence_pct}%। আরও চাপের জন্য পর্যবেক্ষণ করুন।"
        )
    else:
        en = (
            f"{subject_en} is within normal range. "
            f"Confidence: {confidence_pct}%. No review currently indicated."
        )
        bn = (
            f"{subject_bn} স্বাভাবিক সীমার মধ্যে রয়েছে। "
            f"আস্থা: {confidence_pct}%। বর্তমানে কোনো পর্যালোচনার প্রয়োজন নেই।"
        )

    if result.limitations:
        caveat_en = " Advisory only — " + "; ".join(result.limitations[:2]) + "."
        caveat_bn = " পরামর্শমূলক — " + "; ".join(_translate_limitation(l) for l in result.limitations[:2]) + "।"
        en += caveat_en
        bn += caveat_bn

    return en, bn


def explain_finding(result: AnomalyFindingResult, provider_name: str) -> tuple[str, str]:
    """Return (english, bangla) advisory explanation for an anomaly finding."""
    confidence_pct = round(float(result.confidence) * 100)
    en = (
        f"{provider_name} shows a {result.pattern.replace('_', ' ')} pattern "
        f"requiring human review. "
        f"Severity: {result.severity.value}. Confidence: {confidence_pct}%. "
        "This is not proof of wrongdoing. "
        "Review the evidence fingerprint and legitimate event context before any action."
    )
    bn = (
        f"{provider_name}-এ একটি {_translate_pattern(result.pattern)} প্যাটার্ন "
        f"মানব পর্যালোচনার প্রয়োজন করে। "
        f"তীব্রতা: {_translate_severity(result.severity.value)}। আস্থা: {confidence_pct}%। "
        "এটি অনিয়মের প্রমাণ নয়। "
        "কোনো পদক্ষেপ নেওয়ার আগে প্রমাণের ফিঙ্গারপ্রিন্ট এবং বৈধ ঘটনার প্রসঙ্গ পর্যালোচনা করুন।"
    )
    return en, bn


# ── helpers ───────────────────────────────────────────────────────────────────


def _format_runway_en(minutes: Decimal | float | None) -> str:
    if minutes is None:
        return "unknown"
    m = int(minutes)
    if m < 60:
        return f"{m} minutes"
    hours, remainder = divmod(m, 60)
    return f"{hours}h {remainder}m" if remainder else f"{hours} hours"


def _format_runway_bn(minutes: Decimal | float | None) -> str:
    if minutes is None:
        return "অজানা"
    m = int(minutes)
    if m < 60:
        return f"{m} মিনিট"
    hours, remainder = divmod(m, 60)
    return f"{hours} ঘণ্টা {remainder} মিনিট" if remainder else f"{hours} ঘণ্টা"


def _translate_severity(severity: str) -> str:
    return {"low": "নিম্ন", "medium": "মধ্যম", "high": "উচ্চ", "critical": "গুরুতর"}.get(
        severity, severity
    )


def _translate_pattern(pattern: str) -> str:
    return {
        "near_identical_cash_out_velocity": "কাছাকাছি অঙ্কের ক্যাশ-আউট বেগ",
        "repeated_amount": "পুনরাবৃত্তি পরিমাণ",
        "high_velocity": "উচ্চ বেগ",
    }.get(pattern, pattern.replace("_", " "))


def _translate_limitation(limitation: str) -> str:
    if "insufficient" in limitation or "no activity" in limitation:
        return "পর্যাপ্ত লেনদেন ইতিহাস নেই"
    if "missing" in limitation or "unknown" in limitation:
        return "অজানা তথ্য শূন্য হিসেবে ধরা হয়নি"
    if "confidence" in limitation:
        return "আস্থা সীমার নিচে"
    return limitation
