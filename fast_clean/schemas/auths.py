import abc
from typing import Literal

import httpx
from pydantic import BaseModel


class AuthProtocol(BaseModel, abc.ABC):
    """
    Base authentication schema for service access settings.
    """

    type: str

    @property
    @abc.abstractmethod
    def auth(self) -> httpx.Auth:
        """
        Authentication
        """


class BasicAuthSchema(AuthProtocol):
    """
    Basic Auth authentication schema.
    """

    type: Literal['basic_auth']  # type: ignore
    username: str
    password: str

    @property
    def auth(self) -> httpx.Auth:
        return httpx.BasicAuth(self.username, self.password)


class BearerTokenAuthSchema(AuthProtocol):
    """
    Bearer Token authentication schema.
    """

    type: Literal['bearer_token']  # type: ignore
    bearer_token: str

    @property
    def auth(self) -> httpx.Auth:
        from fast_clean.repositories.http.auths import BearerTokenAuth

        return BearerTokenAuth(self.bearer_token)
