import pytest
from injector import inject

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.infrastructure.adapters.outbound.httpx_client_adapter import HttpxClientAdapter
from src.infrastructure.dependency_injection.setup import create_injector, injector


class TestInjectorSetup:
    """Test suite for injector setup."""

    def test_create_injector_returns_configured_injector(self) -> None:
        """
        Verify that `create_injector` returns an injector configured to provide an `HttpxClientAdapter` instance for the `HttpClientPort` interface.
        """
        test_injector = create_injector()

        http_client = test_injector.get(HttpClientPort)  # type: ignore[type-abstract]

        assert isinstance(http_client, HttpxClientAdapter)

    def test_global_injector_is_configured(self) -> None:
        """
        Verify that the global injector provides an instance of HttpxClientAdapter for the HttpClientPort interface.
        """
        http_client = injector.get(HttpClientPort)  # type: ignore[type-abstract]

        assert isinstance(http_client, HttpxClientAdapter)

    def test_inject_decorator_works_with_global_injector(self) -> None:
        """Test that @inject decorator works with the global injector."""

        @inject
        def test_function(*, http_client: HttpClientPort) -> str:
            return f"Got client: {type(http_client).__name__}"

        result = injector.call_with_injection(test_function)

        assert result == "Got client: HttpxClientAdapter"

    def test_inject_with_explicit_parameter(self) -> None:
        """
        Test that providing an explicit parameter to an injected function overrides the default dependency injection.
        
        This test verifies that when a specific `HttpClientPort` instance is supplied as a keyword argument, it is used instead of the injected default, and its attributes can be accessed as expected.
        """
        custom_client = HttpxClientAdapter(timeout=15.0)

        @inject
        def test_function(*, http_client: HttpClientPort) -> str:
            # Cast to concrete type to access private attributes
            """
            Returns the timeout value of the provided HTTP client as a formatted string.
            
            Parameters:
            	http_client (HttpClientPort): The HTTP client instance to retrieve the timeout from. Must be an instance of HttpxClientAdapter.
            
            Returns:
            	str: A string representing the timeout value of the HTTP client.
            """
            from typing import cast

            concrete_client = cast(HttpxClientAdapter, http_client)
            return f"Timeout: {concrete_client._timeout}"

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
