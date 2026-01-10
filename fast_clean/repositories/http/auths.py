from typing import Generator

import httpx


class BearerTokenAuth(httpx.Auth):
    """
    Bearer Token authentication.
    """

    def __init__(self, bearer_token: str) -> None:
        self._auth_header = self._build_auth_header(bearer_token)

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers['Authorization'] = self._auth_header
        yield request

    def _build_auth_header(self, bearer_token: str) -> str:
        return f'Bearer {bearer_token}'
