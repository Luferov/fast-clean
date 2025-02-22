"""
Пакет, содержащий сервис криптографии для шифрования секретных параметров.
"""

from typing import Protocol, Self

from .aes import AesCbcCryptographyService, AesGcmCryptographyService
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


class CryptographyServiceFactoryProtocol(Protocol):
    """
    Протокол фабрики сервисов криптографии для шифрования секретных параметров.
    """

    async def make(self: Self, algorithm: CryptographicAlgorithmEnum) -> CryptographyServiceProtocol:
        """
        Создаем сервис криптографии для шифрования секретных параметров.
        """
        ...


class CryptographyServiceFactoryImpl:
    """
    Реализация фабрики сервисов криптографии для шифрования секретных параметров.
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
            case CryptographicAlgorithmEnum.AES_CBC:
                return AesCbcCryptographyService(self.secret_key)
