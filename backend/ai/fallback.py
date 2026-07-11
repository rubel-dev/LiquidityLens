"""Template-based fallback Bengali/English messages — used when OpenAI is unavailable."""


def liquidity_alert_bn_fallback(provider: str, eta_minutes: int, balance: float) -> str:
    return (
        f"বর্তমান লেনদেনের ধারা অনুযায়ী আনুমানিক {eta_minutes} মিনিটের মধ্যে "
        f"আপনার {provider.upper()} ই-মানি ব্যালেন্স শেষ হয়ে যেতে পারে। "
        f"বর্তমান ব্যালেন্স: ৳{balance:,.0f}। "
        f"নিরাপদভাবে সেবা চালু রাখতে আপনার ফিল্ড অফিসারের সাথে যোগাযোগ করুন।"
    )


def anomaly_alert_bn_fallback(provider: str) -> str:
    return (
        f"গত ১৫ মিনিটে {provider.upper()} লেনদেনে অস্বাভাবিক কার্যক্রম শনাক্ত হয়েছে। "
        f"এটি ঈদ-পূর্ব স্বাভাবিক চাহিদাও হতে পারে। "
        f"বড় কোনো পদক্ষেপ নেওয়ার আগে লেনদেনগুলো মানব পর্যালোচনা করা প্রয়োজন।"
    )


def anomaly_narrative_en_fallback(provider: str) -> str:
    return (
        f"Unusual transaction patterns detected on {provider.upper()} in the last 15 minutes, "
        f"including elevated volume and concentrated account activity. "
        f"This may reflect Eid demand or a salary-day spike — human review is required before any action."
    )
