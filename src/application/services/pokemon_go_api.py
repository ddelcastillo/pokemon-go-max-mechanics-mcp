"""Pokemon GO API service for fetching Pokemon data."""

import threading
from collections.abc import Callable
from typing import Any, Final

from injector import inject

from src.application.constants.api_constants import POKEMON_GO_API_BASE_URL
from src.domain.ports.outbound.http_client_port import HttpClientPort


class PokemonGoApiService:
    """Service for fetching Pokemon GO data from the API."""

    _POKEMON_POKEDEX_URL_BY_NAME_TEMPLATE: Final[str] = f"{POKEMON_GO_API_BASE_URL}/pokedex/name/{{name}}.json"
    _POKEMON_STATS_URL_TEMPLATE: Final[str] = f"{POKEMON_GO_API_BASE_URL}/pokemon_go_api/pokemon_go_api.json"

    # Local dictionary of Pokemon data that we know about
    _LOCAL_POKEMON_DATA: Final[dict[str, dict[str, Any]]] = {
        "bulbasaur": {"id": 1, "name": "Bulbasaur", "type": ["grass", "poison"]},
        "ivysaur": {"id": 2, "name": "Ivysaur", "type": ["grass", "poison"]},
        "venusaur": {"id": 3, "name": "Venusaur", "type": ["grass", "poison"]},
        # Add more Pokemon as needed
    }

    @inject
    def __init__(self, *, http_client: HttpClientPort) -> None:
        """Initialize the Pokemon GO API service.

        Args:
            http_client: The HTTP client to use for API requests.
        """
        self._http_client: HttpClientPort = http_client

    def fetch_pokemon_data_async(
        self,
        *,
        pokemon_name: str,
        on_success: Callable[[dict[str, Any]], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None] = lambda: None,
        on_finished: Callable[[], None] = lambda: None,
        cancellation_check: Callable[[], bool] = lambda: False,
    ) -> threading.Thread:
        """Fetch Pokemon GO data asynchronously.

        Args:
            pokemon_name: The name of the Pokemon to fetch data for.
            on_success: Callback called with Pokemon data dictionary on success.
            on_error: Callback called with error message on failure.
            on_started: Callback called when data fetching starts.
            on_finished: Callback called when operation completes (success or failure).
            cancellation_check: Function that returns True if operation should be cancelled.

        Returns:
            The thread handling the data fetch operation.
        """
        thread = threading.Thread(
            target=self._fetch_pokemon_data_thread,
            args=(pokemon_name, on_success, on_error, on_started, on_finished, cancellation_check),
            daemon=True,
        )
        thread.start()
        return thread

    def _fetch_pokemon_data_thread(
        self,
        pokemon_name: str,
        on_success: Callable[[dict[str, Any]], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None],
        on_finished: Callable[[], None],
        cancellation_check: Callable[[], bool],
    ) -> None:
        """Fetch Pokemon GO data in background thread.

        Args:
            pokemon_name: The name of the Pokemon to search for.
            on_success: Callback for successful data retrieval.
            on_error: Callback for error handling.
            on_started: Callback when operation starts.
            on_finished: Callback when operation completes.
            cancellation_check: Function to check if operation should be cancelled.
        """
        try:
            on_started()

            if cancellation_check():
                return

            with self._http_client as client:
                pokemon_data = self._fetch_pokemon_data(client=client, pokemon_name=pokemon_name)
                if pokemon_data and not cancellation_check():
                    on_success(pokemon_data)
        except Exception as e:
            if not cancellation_check():
                on_error(f"Error searching for {pokemon_name}: {e!s}")
        finally:
            if not cancellation_check():
                on_finished()

    def _fetch_pokemon_data(self, *, client: HttpClientPort, pokemon_name: str) -> dict[str, Any]:
        """Fetch Pokemon data from local dictionary or Pokemon GO API.

        Args:
            client: HTTP client instance.
            pokemon_name: Name of the Pokemon to search for.

        Returns:
            Dictionary containing Pokemon data.

        Raises:
            ValueError: If Pokemon is not found in both local dictionary and API.
        """
        pokemon_name_lower = pokemon_name.lower()

        # Check if Pokemon is in local dictionary first
        if pokemon_name_lower in self._LOCAL_POKEMON_DATA:
            return self._fetch_pokemon_data_from_local_dict(client=client, pokemon_name=pokemon_name_lower)
        else:
            # Try to fetch from API
            return self._fetch_pokemon_data_from_api(client=client, pokemon_name=pokemon_name)

    def _fetch_pokemon_data_from_local_dict(self, *, client: HttpClientPort, pokemon_name: str) -> dict[str, Any]:
        """Fetch Pokemon data from local dictionary and try to get stats from API.

        Args:
            client: HTTP client instance.
            pokemon_name: Name of the Pokemon (must be in local dictionary).

        Returns:
            Dictionary containing Pokemon data with stats.
        """
        # Get basic data from local dictionary
        pokemon_data = self._LOCAL_POKEMON_DATA[pokemon_name].copy()

        # Try to fetch stats from API
        try:
            stats_data = client.get(url=self._POKEMON_STATS_URL_TEMPLATE)
            if isinstance(stats_data, list):
                # Find stats for this Pokemon ID
                pokemon_id = pokemon_data["id"]
                for stat_entry in stats_data:
                    if stat_entry.get("id") == pokemon_id:
                        pokemon_data["stats"] = {
                            "base_attack": stat_entry["base_attack"],
                            "base_defense": stat_entry["base_defense"],
                            "base_stamina": stat_entry["base_stamina"],
                        }
                        break
                else:
                    # Stats not found for this Pokemon
                    pokemon_data["stats"] = "N/A"
            else:
                pokemon_data["stats"] = "N/A"
        except Exception:
            # If stats fetch fails, still return basic data
            pokemon_data["stats"] = "N/A"

        return pokemon_data

    def _fetch_pokemon_data_from_api(self, *, client: HttpClientPort, pokemon_name: str) -> dict[str, Any]:
        """Fetch Pokemon data from Pokemon GO API.

        Args:
            client: HTTP client instance.
            pokemon_name: Name of the Pokemon to search for.

        Returns:
            Dictionary containing Pokemon data.

        Raises:
            ValueError: If API response is invalid or Pokemon is not found.
        """
        pokemon_name_lower = pokemon_name.lower()
        pokedex_url = self._POKEMON_POKEDEX_URL_BY_NAME_TEMPLATE.format(name=pokemon_name_lower)

        # Fetch from pokedex API
        try:
            pokedex_data = client.get(url=pokedex_url)
        except Exception as e:
            # For network errors, preserve the original exception message
            raise ValueError(f"{e!s}") from e

        if not isinstance(pokedex_data, dict):
            raise ValueError(f"Expected dictionary response from pokedex API, got {type(pokedex_data)}")

        if not pokedex_data:
            raise ValueError(f"Pokemon '{pokemon_name}' not found in Pokemon GO.")

        # Validate required fields
        if "dexNr" not in pokedex_data or "names" not in pokedex_data:
            raise ValueError(f"Invalid response format from pokedex API for '{pokemon_name}'")

        # Convert pokedex data to our format
        pokemon_data = {
            "id": pokedex_data["dexNr"],
            "name": pokedex_data["names"].get("English", pokemon_name.title()),
        }

        # Try to fetch stats from API
        try:
            stats_data = client.get(url=self._POKEMON_STATS_URL_TEMPLATE)
            if isinstance(stats_data, list):
                # Find stats for this Pokemon ID
                pokemon_id = pokemon_data["id"]
                for stat_entry in stats_data:
                    if stat_entry.get("id") == pokemon_id:
                        pokemon_data["stats"] = {
                            "base_attack": stat_entry["base_attack"],
                            "base_defense": stat_entry["base_defense"],
                            "base_stamina": stat_entry["base_stamina"],
                        }
                        break
                else:
                    # Stats not found for this Pokemon
                    pokemon_data["stats"] = "N/A"
            else:
                pokemon_data["stats"] = "N/A"
        except Exception:
            # If stats fetch fails, still return basic data
            pokemon_data["stats"] = "N/A"

        return pokemon_data
