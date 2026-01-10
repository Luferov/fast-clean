"""
Module containing cryptography service enums for encrypting secret parameters.
"""

from enum import StrEnum, auto


class CryptographicAlgorithmEnum(StrEnum):
    """
    Cryptographic algorithm.
    """

    AES_GCM = auto()
    """
    AES algorithm in GCM mode.
    """
    AES_CBC = auto()
    """
    AES algorithm in CBC mode.
    """
