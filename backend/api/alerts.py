from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from pydantic import BaseModel
from core.database import get_db
from models.alert import Alert
from models.case import Case

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class NoteBody(BaseModel):
    note: str
    author: str = "Field Officer"


class ResolveBody(BaseModel):
    note: str
    author: str = "Risk Analyst"


@router.get("")
async def list_alerts(
    status: str | None = None,
    provider: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Alert).order_by(Alert.created_at.desc())
    if status:
        q = q.where(Alert.status == status)
    if provider:
        q = q.where(Alert.provider == provider)
    if severity:
        q = q.where(Alert.severity == severity)
    result = await db.execute(q)
    alerts = result.scalars().all()
    return [_serialize(a) for a in alerts]


@router.get("/{alert_id}")
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _serialize(alert)


@router.post("/{alert_id}/acknowledge")
async def acknowledge(alert_id: str, body: NoteBody, db: AsyncSession = Depends(get_db)):
    alert = await _get_or_404(alert_id, db)
    alert.status = "acknowledged"
    alert.updated_at = datetime.now(timezone.utc)

    case = await _get_case(alert_id, db)
    if case:
        case.acknowledged_at = datetime.now(timezone.utc)
        _append_note(case, body.author, f"Acknowledged. {body.note}")

    await db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}


@router.post("/{alert_id}/escalate")
async def escalate(alert_id: str, body: NoteBody, db: AsyncSession = Depends(get_db)):
    alert = await _get_or_404(alert_id, db)
    alert.status = "escalated"
    alert.updated_at = datetime.now(timezone.utc)

    case = await _get_case(alert_id, db)
    if case:
        case.escalated_at = datetime.now(timezone.utc)
        case.assigned_role = "risk_analyst"
        case.assigned_to = "Risk Analyst"
        _append_note(case, body.author, f"Escalated to Risk Analyst. {body.note}")

    await db.commit()
    return {"status": "escalated", "alert_id": alert_id}


@router.post("/{alert_id}/resolve")
async def resolve(alert_id: str, body: ResolveBody, db: AsyncSession = Depends(get_db)):
    alert = await _get_or_404(alert_id, db)
    alert.status = "resolved"
    alert.updated_at = datetime.now(timezone.utc)

    case = await _get_case(alert_id, db)
    if case:
        case.resolved_at = datetime.now(timezone.utc)
        case.resolution_note = body.note
        _append_note(case, body.author, f"Resolved: {body.note}")

    await db.commit()
    return {"status": "resolved", "alert_id": alert_id}


@router.post("/{alert_id}/false-positive")
async def mark_false_positive(alert_id: str, body: NoteBody, db: AsyncSession = Depends(get_db)):
    alert = await _get_or_404(alert_id, db)
    alert.status = "resolved"
    alert.updated_at = datetime.now(timezone.utc)

    case = await _get_case(alert_id, db)
    if case:
        case.false_positive = True
        case.resolved_at = datetime.now(timezone.utc)
        case.resolution_note = f"False positive: {body.note}"
        _append_note(case, body.author, f"Marked false positive: {body.note}")

    await db.commit()
    return {"status": "false_positive_marked", "alert_id": alert_id}


# ── helpers ──────────────────────────────────────────────────────────────────

def _serialize(a: Alert) -> dict:
    return {
        "id": str(a.id),
        "agent_id": str(a.agent_id),
        "provider": a.provider,
        "type": a.type,
        "severity": a.severity,
        "message_en": a.message_en,
        "message_bn": a.message_bn,
        "evidence": a.evidence,
        "confidence": float(a.confidence) if a.confidence else None,
        "uncertainty": a.uncertainty,
        "eta_minutes": a.eta_minutes,
        "owner_role": a.owner_role,
        "owner_name": a.owner_name,
        "status": a.status,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
    }


async def _get_or_404(alert_id: str, db: AsyncSession) -> Alert:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


async def _get_case(alert_id: str, db: AsyncSession) -> Case | None:
    result = await db.execute(select(Case).where(Case.alert_id == alert_id))
    return result.scalar_one_or_none()


def _append_note(case: Case, author: str, text: str):
    notes = list(case.notes or [])
    notes.append({"author": author, "text": text, "timestamp": datetime.now(timezone.utc).isoformat()})
    case.notes = notes
