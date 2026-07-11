"""Deterministic fallback explanation templates for all alert types.

These templates are used when LLM_EXPLANATION_PROVIDER=none or when an LLM
call times out or produces unsafe output. They are intentionally advisory and
must never contain accusatory language or financial execution instructions.
"""

from typing import Literal

AlertType = Literal["liquidity_shortage", "unusual_activity", "data_quality_degraded"]
Language = Literal["en", "bn", "banglish"]

_TEMPLATES: dict[AlertType, dict[Language, str]] = {
    "liquidity_shortage": {
        "en": (
            "{provider_name} e-money balance is approaching a shortage. "
            "Estimated runway is limited. Confidence: {confidence_pct}%. "
            "This is an advisory signal — not a confirmed shortage. "
            "Do not initiate a transfer or refill without approved operational coordination."
        ),
        "bn": (
            "{provider_name} ই-মানি ব্যালেন্স সংকটের দিকে এগিয়ে যাচ্ছে। "
            "আনুমানিক রানওয়ে সীমিত। আস্থা: {confidence_pct}%। "
            "এটি একটি পরামর্শমূলক সংকেত — নিশ্চিত সংকট নয়। "
            "অনুমোদিত অপারেশনাল সমন্বয় ছাড়া ট্রান্সফার বা রিফিল শুরু করবেন না।"
        ),
        "banglish": (
            "{provider_name} e-money balance shortage-er dike jacche. "
            "Estimated runway limited. Confidence: {confidence_pct}%. "
            "Eta advisory signal — nishot shortage na. "
            "Approved operational coordination chara transfer ba refill shuru korben na."
        ),
    },
    "unusual_activity": {
        "en": (
            "{provider_name} shows a transaction pattern that requires human review. "
            "Confidence: {confidence_pct}%. "
            "This is not proof of wrongdoing. "
            "Review the evidence fingerprint and legitimate event context before any action."
        ),
        "bn": (
            "{provider_name}-এ একটি লেনদেন প্যাটার্ন মানব পর্যালোচনার প্রয়োজন করে। "
            "আস্থা: {confidence_pct}%। "
            "এটি অনিয়মের প্রমাণ নয়। "
            "কোনো পদক্ষেপ নেওয়ার আগে প্রমাণের ফিঙ্গারপ্রিন্ট এবং বৈধ ঘটনার প্রসঙ্গ পর্যালোচনা করুন।"
        ),
        "banglish": (
            "{provider_name}-e ekta transaction pattern ache jeta human review dorkar. "
            "Confidence: {confidence_pct}%. "
            "Eta wrongdoing-er proof na. "
            "Kono action nebar age evidence fingerprint ebong legitimate context review korun."
        ),
    },
    "data_quality_degraded": {
        "en": (
            "{provider_name} feed quality is degraded. "
            "Confidence: {confidence_pct}%. "
            "Missing or conflicting data reduces forecast reliability. "
            "Do not treat unknown values as zero. Verify feed health before operational review."
        ),
        "bn": (
            "{provider_name} ফিড মান হ্রাস পেয়েছে। "
            "আস্থা: {confidence_pct}%। "
            "অনুপস্থিত বা বিরোধপূর্ণ ডেটা পূর্বাভাসের নির্ভরযোগ্যতা কমায়। "
            "অজানা মানকে শূন্য হিসেবে বিবেচনা করবেন না। অপারেশনাল পর্যালোচনার আগে ফিড স্বাস্থ্য যাচাই করুন।"
        ),
        "banglish": (
            "{provider_name} feed quality kharap hoye geche. "
            "Confidence: {confidence_pct}%. "
            "Missing ba conflicting data forecast-er reliability komay. "
            "Unknown value-ke zero mone korben na. Operational review-er age feed health verify korun."
        ),
    },
}


def render_template(
    alert_type: AlertType,
    language: Language,
    provider_name: str,
    confidence: float,
) -> str:
    template = _TEMPLATES.get(alert_type, {}).get(language)
    if template is None:
        template = _TEMPLATES[alert_type]["en"]
    return template.format(
        provider_name=provider_name,
        confidence_pct=round(confidence * 100),
    )
