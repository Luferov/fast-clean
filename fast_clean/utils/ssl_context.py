"""
Модуль для создания SSL контекста.
"""

import ssl
from typing import TypeAlias

from pydantic import BaseModel

StrOrBytesPath: TypeAlias = str | bytes  # stable


class CertificateSchema(BaseModel):
    """
    Схема необходимых файлов для создания SSL контекста.
    """

    ca_file: StrOrBytesPath
    cert_file: StrOrBytesPath
    key_file: StrOrBytesPath
    password: str | None = None


def make_ssl_context(params: CertificateSchema, check_hostname: bool = False) -> ssl.SSLContext:
    """
    Создаем SSL контекст.
    """
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=params.ca_file)
    ssl_context.load_cert_chain(certfile=params.cert_file, keyfile=params.key_file, password=params.password)
    ssl_context.check_hostname = check_hostname
    return ssl_context
