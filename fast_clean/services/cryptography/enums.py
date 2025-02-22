"""
Модуль, содержащий перечисления сервиса криптографии для шифрования секретных параметров.
"""

from enum import StrEnum, auto


class CryptographicAlgorithmEnum(StrEnum):
    """
    Криптографический алгоритм.
    """

    AES_GCM = auto()
    """
    Алгоритм AES в режиме GCM.
    """
    AES_CBC = auto()
    """
    Алгоритм AES в режиме CBC.
    """
