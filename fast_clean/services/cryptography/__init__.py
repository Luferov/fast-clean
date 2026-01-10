"""
Package containing the cryptography service for encrypting secret parameters.
"""

from typing import Protocol, Self

from .aes import AesCbcCryptographyService as AesCbcCryptographyService
from .aes import AesGcmCryptographyService
from .enums import CryptographicAlgorithmEnum


class CryptographyServiceProtocol(Protocol):
    """
    Cryptography service protocol for encrypting secret parameters.
    """

    def encrypt(self: Self, data: str) -> str:
        """
        Encrypt data.
        """
        ...

    def decrypt(self: Self, encrypted_data: str) -> str:
        """
        Decrypt data.
        """
        ...


class CryptographyServiceFactory:
    """
    Cryptography services factory for encrypting secret parameters.
    """

    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key

    async def make(self: Self, algorithm: CryptographicAlgorithmEnum) -> CryptographyServiceProtocol:
        """
        Create a cryptography service for encrypting secret parameters.
        """
        match algorithm:
            case CryptographicAlgorithmEnum.AES_GCM:
                return AesGcmCryptographyService(self.secret_key)
            case _:
                raise NotImplementedError(algorithm)
