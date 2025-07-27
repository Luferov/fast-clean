"""
Модуль, содержащий модели.
"""

import datetime as dt

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class CreatedAtMixin:
    """
    Миксин, содержащий дату и время создания записи.
    """

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
    )


class UpdatedAtMixin:
    """
    Миксин, содержащий дату и время обновления записи.
    """

    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
        onupdate=lambda: dt.datetime.now(dt.UTC),
    )


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    """
    Миксин, содержащий дату и время создания и обновления записи.
    """
