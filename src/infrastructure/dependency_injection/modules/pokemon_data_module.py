"""Dependency injection module for Pokemon data components."""

from injector import Module, provider, singleton

from src.domain.ports.outbound.pokemon_data_port import PokemonDataPort, PokemonDict
from src.infrastructure.adapters.outbound.pokemon_go_api_adapter import (
    PokemonGoApiAdapter,
)


class PokemonDataModule(Module):
    """Module for Pokemon data dependency injection."""

    @provider
    @singleton
    def provide_pokemon_data_port(self, adapter: PokemonGoApiAdapter) -> PokemonDataPort[PokemonDict]:
        """Provide the Pokemon data port implementation.

        Args:
            adapter: The Pokemon GO API adapter that returns dictionary-based data.

        Returns:
            The Pokemon data port implementation configured for dictionary data.
        """
        return adapter
