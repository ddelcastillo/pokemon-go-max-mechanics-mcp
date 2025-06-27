import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch

from src.domain.errors.http import HttpClientError
from src.infrastructure.adapters.outbound.httpx_client_adapter import HttpxClientAdapter


class TestHttpxClientAdapter:
    """Test suite for HttpxClientAdapter."""

    def test_sync_get_success(self) -> None:
        """Test successful synchronous GET request."""
        mock_response_data = {"id": 1, "name": "Test name"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            adapter = HttpxClientAdapter()

            with adapter:
                result = adapter.get(url="https://example.com")

            assert result == mock_response_data
            mock_client.get.assert_called_once_with(url="https://example.com", headers=None, params=None, timeout=30.0)

    @pytest.mark.asyncio
    async def test_async_get_success(self) -> None:
        """Test successful asynchronous GET request."""
        mock_response_data = {"id": 1, "name": "Test name"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Create a regular Mock for the response since httpx.Response methods are sync
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            adapter = HttpxClientAdapter()

            async with adapter:
                result = await adapter.get_async(url="https://example.com")

            assert result == mock_response_data
            mock_client.get.assert_called_once_with(url="https://example.com", headers=None, params=None, timeout=30.0)

    def test_sync_get_binary_success(self) -> None:
        """Test successful synchronous binary GET request."""
        mock_binary_data = b"fake image data"

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_response = Mock()
            mock_response.content = mock_binary_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            adapter = HttpxClientAdapter()

            with adapter:
                result = adapter.get_binary(url="https://example.com/image.png")

            assert result == mock_binary_data
            mock_client.get.assert_called_once_with(
                url="https://example.com/image.png", headers=None, params=None, timeout=30.0
            )

    def test_sync_get_binary_with_parameters(self) -> None:
        """Test synchronous binary GET request with headers, params, and custom timeout."""
        mock_binary_data = b"test binary content"
        headers = {"User-Agent": "Test Bot"}
        params = {"size": "large"}
        timeout = 20.0

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_response = Mock()
            mock_response.content = mock_binary_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            adapter = HttpxClientAdapter()

            with adapter:
                result = adapter.get_binary(
                    url="https://api.example.com/download", headers=headers, params=params, timeout=timeout
                )

            assert result == mock_binary_data
            mock_client.get.assert_called_once_with(
                url="https://api.example.com/download", headers=headers, params=params, timeout=timeout
            )

    def test_sync_get_binary_http_error(self) -> None:
        """Test synchronous binary GET request that returns HTTP error status."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Image Not Found"

            http_error = httpx.HTTPStatusError(message="404 Not Found", request=Mock(), response=mock_response)
            mock_response.raise_for_status.side_effect = http_error
            mock_client.get.return_value = mock_response

            adapter = HttpxClientAdapter()

            with adapter:
                with pytest.raises(HttpClientError) as exc_info:
                    adapter.get_binary(url="https://example.com/nonexistent.png")

            assert exc_info.value.status_code == 404
            assert "404" in str(exc_info.value)

    def test_sync_get_binary_request_error(self) -> None:
        """Test synchronous binary GET request that fails due to network error."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            request_error = httpx.RequestError("Connection failed")
            mock_client.get.side_effect = request_error

            adapter = HttpxClientAdapter()

            with adapter:
                with pytest.raises(HttpClientError) as exc_info:
                    adapter.get_binary(url="https://example.com/image.png")

            assert "Request error occurred" in str(exc_info.value)

    def test_sync_get_binary_without_context_manager(self) -> None:
        """Test that synchronous binary GET request fails when client is not initialized."""
        adapter = HttpxClientAdapter()

        with pytest.raises(HttpClientError) as exc_info:
            adapter.get_binary(url="https://example.com/image.png")

        assert "Sync client not initialized" in str(exc_info.value)

    def test_sync_get_with_parameters(self) -> None:
        """Test synchronous GET request with headers, params, and custom timeout."""
        mock_response_data = {"data": "test"}
        headers = {"Authorization": "Bearer token"}
        params = {"limit": 10}
        timeout = 15.0

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            adapter = HttpxClientAdapter()

            with adapter:
                result = adapter.get(
                    url="https://api.example.com/data", headers=headers, params=params, timeout=timeout
                )

            assert result == mock_response_data
            mock_client.get.assert_called_once_with(
                url="https://api.example.com/data", headers=headers, params=params, timeout=timeout
            )

    def test_sync_get_http_error(self) -> None:
        """Test synchronous GET request that returns HTTP error status."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"

            http_error = httpx.HTTPStatusError(message="404 Not Found", request=Mock(), response=mock_response)
            mock_response.raise_for_status.side_effect = http_error
            mock_client.get.return_value = mock_response

            adapter = HttpxClientAdapter()

            with adapter:
                with pytest.raises(HttpClientError) as exc_info:
                    adapter.get(url="https://api.example.com/nonexistent")

            assert exc_info.value.status_code == 404
            assert "404" in str(exc_info.value)

    def test_sync_get_request_error(self) -> None:
        """Test synchronous GET request that fails due to network error."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            request_error = httpx.RequestError("Connection failed")
            mock_client.get.side_effect = request_error

            adapter = HttpxClientAdapter()

            with adapter:
                with pytest.raises(HttpClientError) as exc_info:
                    adapter.get(url="https://api.example.com/test")

            assert "Request error occurred" in str(exc_info.value)

    def test_sync_get_without_context_manager(self) -> None:
        """Test that synchronous GET request fails when client is not initialized."""
        adapter = HttpxClientAdapter()

        with pytest.raises(HttpClientError) as exc_info:
            adapter.get(url="https://api.example.com/test")

        assert "Sync client not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_get_without_context_manager(self) -> None:
        """Test that asynchronous GET request fails when client is not initialized."""
        adapter = HttpxClientAdapter()

        with pytest.raises(HttpClientError) as exc_info:
            await adapter.get_async(url="https://api.example.com/test")

        assert "Async client not initialized" in str(exc_info.value)

    def test_adapter_initialization_without_base_url(self) -> None:
        """Test that the adapter initializes without base_url coupling."""
        adapter = HttpxClientAdapter(timeout=15.0)

        assert adapter._timeout == 15.0
        assert not hasattr(adapter, "_base_url")

    def test_adapter_default_timeout(self) -> None:
        """Test that the adapter uses default timeout when not specified."""
        adapter = HttpxClientAdapter()

        assert adapter._timeout == 30.0
