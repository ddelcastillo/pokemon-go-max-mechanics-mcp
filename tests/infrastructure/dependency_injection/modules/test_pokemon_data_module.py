from injector import Injector

from src.domain.ports.outbound.pokemon_data_port import PokemonDataPort, PokemonDict
from src.infrastructure.adapters.outbound.pokemon_go_api_adapter import (
    PokemonGoApiAdapter,
)
from src.infrastructure.dependency_injection.modules.http_client import HttpClientModule
from src.infrastructure.dependency_injection.modules.pokemon_data_module import (
    PokemonDataModule,
)


def test_provide_pokemon_data_port_returns_adapter() -> None:
    """Test that the provide_pokemon_data_port method returns an instance of PokemonGoApiAdapter."""
    injector = Injector(modules=[HttpClientModule(), PokemonDataModule()])
    port = injector.get(PokemonDataPort[PokemonDict])  # type: ignore[type-abstract]
    assert isinstance(port, PokemonGoApiAdapter)
