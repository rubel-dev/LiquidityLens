from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.mixins import UuidPrimaryKeyMixin


class Provider(UuidPrimaryKeyMixin, Base):
    __tablename__ = "providers"
    __table_args__ = (Index("ix_providers_code", "code"),)

    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    boundary_note: Mapped[str] = mapped_column(String(255), nullable=False)

    accounts: Mapped[list["AgentProviderAccount"]] = relationship(back_populates="provider")
    feed_statuses: Mapped[list["ProviderFeedStatus"]] = relationship(back_populates="provider")
    role_assignments: Mapped[list["UserRoleAssignment"]] = relationship(back_populates="provider")

