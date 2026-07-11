import uuid

from app.persistence.models.audit import AuditEvent
from app.persistence.models.provider import Provider
from app.validation.schemas import ValidationFinding


def validation_audit_event(
    *,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    provider: Provider | None,
    correlation_id: str | None,
    findings: tuple[ValidationFinding, ...],
    metadata: dict[str, object] | None = None,
) -> AuditEvent:
    safe_metadata: dict[str, object] = {
        "finding_categories": [item.category.value for item in findings],
        "finding_count": len(findings),
        "source": "provider_ingestion_validation",
    }
    if metadata:
        safe_metadata.update(metadata)
    return AuditEvent(
        provider_id=None if provider is None else provider.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        correlation_id=correlation_id,
        metadata_json=safe_metadata,
    )
