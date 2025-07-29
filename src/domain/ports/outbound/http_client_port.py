from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Self


class HttpClientPort(ABC):
    """Abstract port for HTTP client operations.

    This port defines the interface for making HTTP requests to external APIs.
    Supports both synchronous and asynchronous operations.
    """

    @abstractmethod
    def __enter__(self) -> Self:  # pragma: no cover
        """Sync context manager entry."""
        pass

    @abstractmethod
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Sync context manager exit."""
        pass

    @abstractmethod
    async def __aenter__(self) -> Self:  # pragma: no cover
        """Async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Async context manager exit."""
        pass

    @abstractmethod
    def get(
        self,
        *,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:  # pragma: no cover
        """Execute a synchronous GET request to the specified URL.

        Args:
            url: The URL to send the GET request to.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters to include in the request.
            timeout: Optional timeout in seconds for the request.

        Returns:
            Dictionary containing the JSON response data.

        Raises:
            HttpClientError: When the HTTP request fails or returns an error status.
        """
        pass

    @abstractmethod
    async def get_async(
        self,
        *,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:  # pragma: no cover
        """Execute an asynchronous GET request to the specified URL.

        Args:
            url: The URL to send the GET request to.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters to include in the request.
            timeout: Optional timeout in seconds for the request.

        Returns:
            Dictionary containing the JSON response data.

        Raises:
            HttpClientError: When the HTTP request fails or returns an error status.
        """
        pass

    @abstractmethod
    def get_binary(
        self,
        *,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> bytes:  # pragma: no cover
        """Execute a synchronous GET request to download binary data from the specified URL.

        Args:
            url: The URL to send the GET request to.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters to include in the request.
            timeout: Optional timeout in seconds for the request.

        Returns:
            Binary data from the response.

        Raises:
            HttpClientError: When the HTTP request fails or returns an error status.
        """
        pass
