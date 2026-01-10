"""
Module containing cryptography service tests.
"""

import pytest

from fast_clean.services.cryptography import CryptographyServiceProtocol


@pytest.mark.parametrize(
    'cryptography_service',
    ['aes_gcm', 'aes_cbc'],
    indirect=True,
)
class TestCryptographyServices:
    """
    Cryptography service tests.
    """

    SECRET_VALUE = 'secret_value'

    @classmethod
    async def test_encrypt_and_decrypt(
        cls,
        cryptography_service: CryptographyServiceProtocol,
    ) -> None:
        """
        Test the `encrypt` and `decrypt` methods.
        """
        encrypted_value = cryptography_service.encrypt(cls.SECRET_VALUE)
        assert cryptography_service.decrypt(encrypted_value) == cls.SECRET_VALUE
