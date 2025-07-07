"""Dependency injection module for Pokemon GO API service."""

from injector import Binder, Module, singleton

from src.application.services.pokemon_go_api import PokemonGoApiService


class PokemonGoApiServiceModule(Module):
    """Module for configuring Pokemon GO API service dependencies."""

    def configure(self, binder: Binder) -> None:
        """Configure Pokemon GO API service bindings.

        Args:
            binder: The injector binder to configure.
        """
        binder.bind(PokemonGoApiService, to=PokemonGoApiService, scope=singleton)
