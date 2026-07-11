from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.mixins import UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.persistence.models.agent import Agent
    from app.persistence.models.user import UserRoleAssignment


class Area(UuidPrimaryKeyMixin, Base):
    __tablename__ = "areas"
    __table_args__ = (Index("ix_areas_code", "code"),)

    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)

    agents: Mapped[list["Agent"]] = relationship(back_populates="area")
    role_assignments: Mapped[list["UserRoleAssignment"]] = relationship(back_populates="area")
