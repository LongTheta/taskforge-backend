"""SQLAlchemy mixins for shared model behavior."""

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def _utc_now() -> datetime:
    """Current UTC timestamp."""
    return datetime.now(UTC)


class TimestampMixin:
    """Mixin adding created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )
