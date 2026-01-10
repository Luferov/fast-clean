"""
Module containing cryptography commands for encrypting secret parameters.
"""

from typing import Annotated

import typer

from fast_clean.container import get_container
from fast_clean.services import CryptographicAlgorithmEnum, CryptographyServiceFactory
from fast_clean.utils import typer_async


@typer_async
async def encrypt(
    data: Annotated[str, typer.Argument(help='Data to encrypt.')],
    algorithm: Annotated[
        CryptographicAlgorithmEnum, typer.Option(help='Cryptographic algorithm')
    ] = CryptographicAlgorithmEnum.AES_GCM,
) -> None:
    """
    Encrypt data.
    """
    async with get_container() as container:
        cryptography_service_factory = await container.get(CryptographyServiceFactory)
        cryptography_service = await cryptography_service_factory.make(algorithm)
        print(cryptography_service.encrypt(data))


@typer_async
async def decrypt(
    data: Annotated[str, typer.Argument(help='Data to decrypt.')],
    algorithm: Annotated[
        CryptographicAlgorithmEnum, typer.Option(help='Cryptographic algorithm')
    ] = CryptographicAlgorithmEnum.AES_GCM,
) -> None:
    """
    Decrypt data.
    """
    async with get_container() as container:
        cryptography_service_factory = await container.get(CryptographyServiceFactory)
        cryptography_service = await cryptography_service_factory.make(algorithm)
        print(cryptography_service.decrypt(data))


def use_cryptography(app: typer.Typer) -> None:
    """
    Register cryptography commands for encrypting secret parameters.
    """

    app.command()(encrypt)
    app.command()(decrypt)
