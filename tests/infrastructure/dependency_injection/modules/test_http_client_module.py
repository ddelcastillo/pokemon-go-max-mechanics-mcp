from injector import Injector

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.infrastructure.adapters.outbound.httpx_client_adapter import HttpxClientAdapter
from src.infrastructure.dependency_injection.modules.http_client import HttpClientModule


def test_provide_http_client_returns_adapter() -> None:
    """Test that the HttpClientModule provides an instance of HttpxClientAdapter."""
    injector = Injector(modules=[HttpClientModule()])
    client = injector.get(HttpClientPort)  # type: ignore[type-abstract]
    assert isinstance(client, HttpxClientAdapter)


def test_http_client_is_singleton() -> None:
    """Test that the HttpClientModule provides the same instance when requested multiple times."""
    injector = Injector(modules=[HttpClientModule()])
    client1 = injector.get(HttpClientPort)  # type: ignore[type-abstract]
    client2 = injector.get(HttpClientPort)  # type: ignore[type-abstract]
    assert client1 is client2
