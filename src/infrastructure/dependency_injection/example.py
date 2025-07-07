"""Example demonstrating the use of dependency injection with Pokémon GO API."""

from injector import inject

from src.application.constants.api_constants import POKEMON_GO_API_BASE_URL
from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.infrastructure.dependency_injection.setup import injector


class PokemonGoService:
    """Example service that uses dependency injection for Pokémon GO data."""

    @inject
    def __init__(self, *, http_client: HttpClientPort) -> None:
        """Initialize the service with injected dependencies.

        Args:
            http_client: HTTP client port for making API requests.
        """
        self.http_client = http_client

    def get_pokemon_stats(self) -> dict:
        """Get all Pokémon GO stats using the injected HTTP client.

        Returns:
            Dictionary containing Pokémon GO stats data.
        """
        full_url = f"{POKEMON_GO_API_BASE_URL}/pokemon_stats.json"
        with self.http_client:
            return self.http_client.get(url=full_url)

    def get_pokemon_max_cp(self) -> dict:
        """Get max CP data for all Pokémon in GO.

        Returns:
            Dictionary containing max CP data.
        """
        full_url = f"{POKEMON_GO_API_BASE_URL}/pokemon_max_cp.json"
        with self.http_client:
            return self.http_client.get(url=full_url)

    def get_released_pokemon(self) -> dict:
        """Get list of released Pokémon in GO.

        Returns:
            Dictionary containing released Pokémon data.
        """
        full_url = f"{POKEMON_GO_API_BASE_URL}/released_pokemon.json"
        with self.http_client:
            return self.http_client.get(url=full_url)


@inject
def example_function(*, http_client: HttpClientPort) -> str:
    """Example function demonstrating dependency injection.

    Args:
        http_client: HTTP client port injected automatically.

    Returns:
        String describing the injected client.
    """
    return f"Received HTTP client: {type(http_client).__name__}"


def main() -> None:
    """Main function demonstrating usage."""
    # Create service using dependency injection
    pokemon_go_service = injector.create_object(PokemonGoService)

    # Use the service to get Pokémon GO specific data
    try:
        print("Fetching Pokémon GO stats...")
        stats_data = pokemon_go_service.get_pokemon_stats()
        print(f"Number of Pokémon with stats: {len(stats_data)}")

        print("\nFetching max CP data...")
        max_cp_data = pokemon_go_service.get_pokemon_max_cp()
        print(f"Number of Pokémon with max CP data: {len(max_cp_data)}")

        print("\nFetching released Pokémon...")
        released_data = pokemon_go_service.get_released_pokemon()
        print(f"Number of released Pokémon: {len(released_data)}")

        # Show some example data
        if stats_data and len(stats_data) > 0:
            example_pokemon = stats_data[0]
            print(f"\nExample Pokémon stats: {example_pokemon}")

    except Exception as e:
        print(f"Error fetching Pokémon GO data: {e}")

    # Call function with dependency injection
    result = injector.call_with_injection(example_function)
    print(f"\n{result}")


if __name__ == "__main__":
    main()
