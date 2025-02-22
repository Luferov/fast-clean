"""
Модуль, содержащий команды криптографии для шифрования секретных параметров.
"""

from typing import Annotated

import typer

from fast_clean.depends import get_container
from fast_clean.services import CryptographicAlgorithmEnum, CryptographyServiceFactoryProtocol
from fast_clean.utils import typer_async


@typer_async
async def encrypt(
    data: Annotated[str, typer.Argument(help='Данные для шифровки.')],
    algorithm: Annotated[
        CryptographicAlgorithmEnum, typer.Option(help='Криптографический алгоритм')
    ] = CryptographicAlgorithmEnum.AES_GCM,
) -> None:
    """
    Зашифровываем данные.
    """
    container = get_container()
    cryptography_service_factory: CryptographyServiceFactoryProtocol = await container.get_by_type(
        CryptographyServiceFactoryProtocol
    )
    cryptography_service = await cryptography_service_factory.make(algorithm)
    print(cryptography_service.encrypt(data))


@typer_async
async def decrypt(
    data: Annotated[str, typer.Argument(help='Данные для расшифровки.')],
    algorithm: Annotated[
        CryptographicAlgorithmEnum, typer.Option(help='Криптографический алгоритм')
    ] = CryptographicAlgorithmEnum.AES_GCM,
) -> None:
    """
    Расшифровываем данные.
    """
    container = get_container()
    cryptography_service_factory: CryptographyServiceFactoryProtocol = await container.get_by_type(
        CryptographyServiceFactoryProtocol
    )
    cryptography_service = await cryptography_service_factory.make(algorithm)
    print(cryptography_service.decrypt(data))


def use_cryptography(app: typer.Typer) -> None:
    """
    Регистрируем команды криптографии для шифрования секретных параметров.
    """

    app.command()(encrypt)
    app.command()(decrypt)
