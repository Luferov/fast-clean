"""
Пакет, содержащий сервис криптографии для шифрования секретных параметров.
"""

from typing import Protocol, Self

from .aes import AesCbcCryptographyService as AesCbcCryptographyService
from .aes import AesGcmCryptographyService
from .enums import CryptographicAlgorithmEnum


class CryptographyServiceProtocol(Protocol):
    """
    Протокол сервиса криптографии для шифрования секретных параметров.
    """

    def encrypt(self: Self, data: str) -> str:
        """
        Зашифровываем данные.
        """
        ...

    def decrypt(self: Self, encrypted_data: str) -> str:
        """
        Расшифровываем данные.
        """
        ...


class CryptographyServiceFactory:
    """
    Фабрика сервисов криптографии для шифрования секретных параметров.
    """

    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key

    async def make(self: Self, algorithm: CryptographicAlgorithmEnum) -> CryptographyServiceProtocol:
        """
        Создаем сервис криптографии для шифрования секретных параметров.
        """
        match algorithm:
            case CryptographicAlgorithmEnum.AES_GCM:
                return AesGcmCryptographyService(self.secret_key)
            case _:
                 raise NotImplementedError(algorithm)
