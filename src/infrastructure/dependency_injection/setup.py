from injector import Injector

from src.infrastructure.dependency_injection.modules.http_client import HttpClientModule
from src.infrastructure.dependency_injection.modules.image_service import (
    ImageServiceModule,
)
from src.infrastructure.dependency_injection.modules.pokemon_go_api_service import (
    PokemonGoApiServiceModule,
)


def create_injector() -> Injector:
    """Create and configure the main injector instance.

    Returns:
        Configured injector instance with all modules.
    """
    return Injector(modules=[HttpClientModule(), ImageServiceModule(), PokemonGoApiServiceModule()])


# Global injector instance
injector: Injector = create_injector()
