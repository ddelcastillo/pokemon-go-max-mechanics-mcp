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
        """
        Provides a singleton implementation of the Pokemon data port using the given API adapter.
        
        Returns:
            PokemonDataPort[PokemonDict]: The provided adapter as the implementation for dictionary-based Pokemon data access.
        """
        return adapter
