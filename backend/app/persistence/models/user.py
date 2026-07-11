import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin


class User(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "users"

    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    synthetic_user_ref: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    role_assignments: Mapped[list["UserRoleAssignment"]] = relationship(back_populates="user")


class Role(UuidPrimaryKeyMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint(
            "name in ('agent','ops','field','risk','manager','demo')",
            name="ck_roles_name",
        ),
    )

    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    assignments: Mapped[list["UserRoleAssignment"]] = relationship(back_populates="role")


class UserRoleAssignment(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "user_role_assignments"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            "provider_id",
            "area_id",
            name="uq_user_role_scope",
        ),
        Index("ix_user_role_provider", "user_id", "provider_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    provider_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=True)
    area_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("areas.id"), nullable=True)

    user: Mapped[User] = relationship(back_populates="role_assignments")
    role: Mapped[Role] = relationship(back_populates="assignments")
    provider: Mapped["Provider | None"] = relationship(back_populates="role_assignments")
    area: Mapped["Area | None"] = relationship(back_populates="role_assignments")

