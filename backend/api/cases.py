from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timezone
from core.database import get_db
from models.case import Case
from models.alert import Alert

router = APIRouter(prefix="/api/cases", tags=["cases"])


class NoteBody(BaseModel):
    text: str
    author: str = "Field Officer"


class AssignBody(BaseModel):
    assigned_to: str
    assigned_role: str
    note: str = ""


@router.get("")
async def list_cases(status: str | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Case).order_by(Case.created_at.desc())
    result = await db.execute(q)
    cases = result.scalars().all()
    return [_serialize(c) for c in cases]


@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return _serialize(case)


@router.post("/{case_id}/notes")
async def add_note(case_id: str, body: NoteBody, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    notes = list(case.notes or [])
    notes.append({
        "author": body.author,
        "text": body.text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    case.notes = notes
    await db.commit()
    return {"case_id": case_id, "notes": notes}


@router.patch("/{case_id}/assign")
async def assign_case(case_id: str, body: AssignBody, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.assigned_to = body.assigned_to
    case.assigned_role = body.assigned_role
    if body.note:
        notes = list(case.notes or [])
        notes.append({"author": "System", "text": f"Assigned to {body.assigned_to}. {body.note}", "timestamp": datetime.now(timezone.utc).isoformat()})
        case.notes = notes
    await db.commit()
    return _serialize(case)


def _serialize(c: Case) -> dict:
    return {
        "id": str(c.id),
        "alert_id": str(c.alert_id),
        "assigned_to": c.assigned_to,
        "assigned_role": c.assigned_role,
        "acknowledged_at": c.acknowledged_at.isoformat() if c.acknowledged_at else None,
        "escalated_at": c.escalated_at.isoformat() if c.escalated_at else None,
        "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
        "resolution_note": c.resolution_note,
        "false_positive": c.false_positive,
        "notes": c.notes or [],
        "created_at": c.created_at.isoformat(),
    }
