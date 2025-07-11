import pytest
from injector import Injector

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.infrastructure.adapters.outbound.httpx_client_adapter import HttpxClientAdapter
from src.infrastructure.dependency_injection.modules.http_client import HttpClientModule


class TestHttpClientModule:
    """Test suite for HttpClientModule."""

    def test_module_binds_http_client_port(self) -> None:
        """Test that the module properly binds HttpClientPort."""
        injector = Injector(modules=[HttpClientModule()])

        http_client = injector.get(HttpClientPort)  # type: ignore[type-abstract]

        assert isinstance(http_client, HttpxClientAdapter)

    def test_singleton_scope(self) -> None:
        """Test that HttpClientPort is bound as singleton."""
        injector = Injector(modules=[HttpClientModule()])

        http_client1 = injector.get(HttpClientPort)  # type: ignore[type-abstract]
        http_client2 = injector.get(HttpClientPort)  # type: ignore[type-abstract]

        assert http_client1 is http_client2
