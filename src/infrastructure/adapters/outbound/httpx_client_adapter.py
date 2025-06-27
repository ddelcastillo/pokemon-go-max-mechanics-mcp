from types import TracebackType
from typing import Any, Self

import httpx

from src.domain.errors.http import HttpClientError
from src.domain.ports.outbound.http_client_port import HttpClientPort


class HttpxClientAdapter(HttpClientPort):
    """Generic HTTP client adapter using httpx library.

    This adapter implements the HttpClientPort interface using the httpx library
    for making HTTP requests to any external APIs. It is not coupled to any specific API.
    Supports both synchronous and asynchronous operations.
    """

    def __init__(self, *, timeout: float = 30.0) -> None:
        """Initialize the httpx client adapter.

        Args:
            timeout: Default timeout in seconds for requests.
        """
        self._timeout = timeout
        self._async_client: httpx.AsyncClient | None = None
        self._sync_client: httpx.Client | None = None

    def __enter__(self) -> Self:
        """Sync context manager entry."""
        self._sync_client = httpx.Client(timeout=self._timeout)
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Sync context manager exit."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        self._async_client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Async context manager exit."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def get(
        self,
        *,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Execute a synchronous GET request to the specified URL.

        Args:
            url: The full URL to send the GET request to.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters to include in the request.
            timeout: Optional timeout in seconds for the request.

        Returns:
            Dictionary containing the JSON response data.

        Raises:
            HttpClientError: When the HTTP request fails or returns an error status.
        """
        if not self._sync_client:
            raise HttpClientError(message="Sync client not initialized. Use context manager.")

        try:
            response = self._sync_client.get(url=url, headers=headers, params=params, timeout=timeout or self._timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HttpClientError(
                message=f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise HttpClientError(message=f"Request error occurred: {e!s}") from e
        except ValueError as e:
            raise HttpClientError(message=f"Invalid JSON response: {e!s}") from e

    async def get_async(
        self,
        *,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Execute an asynchronous GET request to the specified URL.

        Args:
            url: The full URL to send the GET request to.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters to include in the request.
            timeout: Optional timeout in seconds for the request.

        Returns:
            Dictionary containing the JSON response data.

        Raises:
            HttpClientError: When the HTTP request fails or returns an error status.
        """
        if not self._async_client:
            raise HttpClientError(message="Async client not initialized. Use async context manager.")

        try:
            response = await self._async_client.get(
                url=url, headers=headers, params=params, timeout=timeout or self._timeout
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HttpClientError(
                message=f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise HttpClientError(message=f"Request error occurred: {e!s}") from e
        except ValueError as e:
            raise HttpClientError(message=f"Invalid JSON response: {e!s}") from e

    def get_binary(
        self,
        *,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> bytes:
        """Execute a synchronous GET request to download binary data from the specified URL.

        Args:
            url: The full URL to send the GET request to.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters to include in the request.
            timeout: Optional timeout in seconds for the request.

        Returns:
            Binary data from the response.

        Raises:
            HttpClientError: When the HTTP request fails or returns an error status.
        """
        if not self._sync_client:
            raise HttpClientError(message="Sync client not initialized. Use context manager.")

        try:
            response = self._sync_client.get(url=url, headers=headers, params=params, timeout=timeout or self._timeout)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            raise HttpClientError(
                message=f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise HttpClientError(message=f"Request error occurred: {e!s}") from e
