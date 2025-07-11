from injector import Injector

from src.infrastructure.dependency_injection.modules.http_client import HttpClientModule
from src.infrastructure.dependency_injection.modules.image_service import (
    ImageServiceModule,
)
from src.infrastructure.dependency_injection.modules.pokemon_data_module import (
    PokemonDataModule,
)


def create_injector() -> Injector:
    """
    Create and configure the application's main dependency injector.
    
    Returns:
        Injector: An Injector instance pre-configured with HTTP client, image service, and Pokémon data modules.
    """
    return Injector(modules=[HttpClientModule(), ImageServiceModule(), PokemonDataModule()])


# Global injector instance
injector: Injector = create_injector()
