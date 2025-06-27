import pytest
from injector import inject

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.infrastructure.adapters.outbound.httpx_client_adapter import HttpxClientAdapter
from src.infrastructure.dependency_injection.setup import create_injector, injector


class TestInjectorSetup:
    """Test suite for injector setup."""

    def test_create_injector_returns_configured_injector(self) -> None:
        """Test that create_injector returns a properly configured injector."""
        test_injector = create_injector()

        http_client = test_injector.get(HttpClientPort)

        assert isinstance(http_client, HttpxClientAdapter)

    def test_global_injector_is_configured(self) -> None:
        """Test that the global injector instance is properly configured."""
        http_client = injector.get(HttpClientPort)

        assert isinstance(http_client, HttpxClientAdapter)

    def test_inject_decorator_works_with_global_injector(self) -> None:
        """Test that @inject decorator works with the global injector."""

        @inject
        def test_function(*, http_client: HttpClientPort) -> str:
            return f"Got client: {type(http_client).__name__}"

        result = injector.call_with_injection(test_function)

        assert result == "Got client: HttpxClientAdapter"

    def test_inject_with_explicit_parameter(self) -> None:
        """Test that explicit parameters override injection."""
        custom_client = HttpxClientAdapter(timeout=15.0)

        @inject
        def test_function(*, http_client: HttpClientPort) -> str:
            return f"Timeout: {http_client._timeout}"

        result = injector.call_with_injection(test_function, kwargs={"http_client": custom_client})

        assert result == "Timeout: 15.0"

    def test_dependency_injection_in_class_constructor(self) -> None:
        """Test dependency injection in class constructors."""

        class TestService:
            @inject
            def __init__(self, *, http_client: HttpClientPort) -> None:
                self.http_client = http_client

            def get_client_type(self) -> str:
                return type(self.http_client).__name__

        service = injector.create_object(TestService)

        assert service.get_client_type() == "HttpxClientAdapter"
        assert isinstance(service.http_client, HttpxClientAdapter)
