"""
Module containing models.
"""

import datetime as dt

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class CreatedAtMixin:
    """
    Mixin containing the record creation date and time.
    """

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
    )


class UpdatedAtMixin:
    """
    Mixin containing the record update date and time.
    """

    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
        onupdate=lambda: dt.datetime.now(dt.UTC),
    )


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    """
    Mixin containing the record creation and update date and time.
    """

    ...
