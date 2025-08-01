from __future__ import annotations

from typing import TYPE_CHECKING

from injector import Module, provider, singleton

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.infrastructure.adapters.outbound.httpx_client_adapter import HttpxClientAdapter
from src.infrastructure.constants.api_constants import DEFAULT_HTTP_TIMEOUT

if TYPE_CHECKING:
    from injector import Binder


class HttpClientModule(Module):
    """Module for configuring HTTP client dependencies."""

    def configure(self, binder: Binder) -> None:  # pragma: no cover
        """Configure HTTP client bindings.

        Args:
            binder: The injector binder for setting up dependencies.
        """
        # Bind the abstract port to the provider method
        binder.bind(HttpClientPort, to=self.provide_http_client, scope=singleton)  # type: ignore[type-abstract]

    @provider
    @singleton
    def provide_http_client(self) -> HttpClientPort:  # pragma: no cover
        """Provide a configured HTTP client instance.

        Returns:
            A configured HttpClientPort implementation.
        """
        return HttpxClientAdapter(timeout=DEFAULT_HTTP_TIMEOUT)
