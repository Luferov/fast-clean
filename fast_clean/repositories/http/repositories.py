from typing import Any, Self

import httpx

from fast_clean.settings import CoreServiceSettingsSchema


class HttpRepository[TParams: CoreServiceSettingsSchema]:
    def __init__(self, params: TParams) -> None:
        self.params = params
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        if self.client is None:
            self.client = self.make_client()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: Any | None
    ) -> None:
        if self.client:
            await self.client.aclose()
        self.client = None
        return None

    def make_client(self: Self) -> httpx.AsyncClient:
        transport = httpx.AsyncHTTPTransport(retries=self.params.retries, verify=self.params.verify)
        return httpx.AsyncClient(
            base_url=str(self.params.host),
            transport=transport,
            auth=self.params.auth.auth if self.params.auth else None,
        )
