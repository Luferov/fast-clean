"""
Модуль, содержащий модели.
"""

import datetime as dt

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampMixin:
    """
    Миксин, содержащий дату и время создания и обновления модели.
    """

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
    )
    """
    Дата и время создания.
    """
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
        onupdate=lambda: dt.datetime.now(dt.UTC),
    )
    """
    Дата и время обновления.
    """
