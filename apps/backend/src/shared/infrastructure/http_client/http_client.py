import httpx


class HTTPClient:
    """
    A simple HTTP Client to make requests
    """

    async def get(self, url: str, headers: dict | None = None) -> dict | str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return response.text

    async def post(
        self, url: str, data: dict | None = None, headers: dict | None = None
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()

    async def put(
        self, url: str, data: dict | None = None, headers: dict | None = None
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()

    async def delete(self, url: str, headers: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def patch(
        self, url: str, data: dict | None = None, headers: dict | None = None
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()


def get_http_client() -> HTTPClient:
    """
    Dependency injector for HTTPClient
    """
    return HTTPClient()
