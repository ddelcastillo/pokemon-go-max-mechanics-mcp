"""Pokemon GO API adapter for external Pokemon data retrieval."""

from typing import Final

from injector import inject

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.domain.ports.outbound.pokemon_data_port import PokemonDataPort, PokemonDict
from src.infrastructure.constants.api_constants import POKEMON_GO_API_BASE_URL


class PokemonGoApiAdapter(PokemonDataPort[PokemonDict]):
    """Infrastructure adapter for fetching Pokemon data from Pokemon GO API.

    This adapter implements the PokemonDataPort interface and handles all
    HTTP communication with the external Pokemon GO API. It returns Pokemon
    data as dictionaries containing structured information about each Pokemon.
    """

    _POKEMON_POKEDEX_URL_BY_NAME_TEMPLATE: Final[str] = f"{POKEMON_GO_API_BASE_URL}/pokedex/name/{{name}}.json"

    @inject
    def __init__(self, *, http_client: HttpClientPort) -> None:
        """Initialize the Pokemon GO API adapter.

        Args:
            http_client: The HTTP client to use for API requests.
        """
        self._http_client: HttpClientPort = http_client

    def fetch_pokemon_data(self, *, pokemon_name: str) -> PokemonDict:
        """Fetch Pokemon data from Pokemon GO API.

        Args:
            pokemon_name: The name of the Pokemon to fetch data for.

        Returns:
            Dictionary containing Pokemon data.

        Raises:
            ValueError: If Pokemon is not found or if there's an error fetching data.
        """
        with self._http_client as client:
            return self._fetch_pokemon_data_from_api(client=client, pokemon_name=pokemon_name)

    def _fetch_pokemon_data_from_api(self, *, client: HttpClientPort, pokemon_name: str) -> PokemonDict:
        """Fetch Pokemon data from Pokemon GO API.

        Args:
            client: HTTP client instance.
            pokemon_name: Name of the Pokemon to search for.

        Returns:
            Dictionary containing Pokemon data.

        Raises:
            ValueError: If API response is invalid or Pokemon is not found.
        """
        pokemon_name = pokemon_name.upper()
        pokedex_url = self._POKEMON_POKEDEX_URL_BY_NAME_TEMPLATE.format(name=pokemon_name)

        try:
            pokedex_data = client.get(url=pokedex_url)
        except Exception as e:
            raise ValueError(
                f"Error fetching Pokemon data from API: Status code "
                f"{getattr(e, 'status_code', getattr(e, 'code', 'unknown'))}"
            ) from e

        if not isinstance(pokedex_data, dict):
            raise ValueError(f"Expected dictionary response from pokedex API, got {type(pokedex_data)}")

        if not pokedex_data:
            raise ValueError(f"Pokemon '{pokemon_name}' not found in Pokemon GO.")

        if "dexNr" not in pokedex_data or "names" not in pokedex_data:
            raise ValueError(f"Invalid response format from pokedex API for '{pokemon_name}'")
        # TODO: modify to use Pokemon entity object!
        return pokedex_data
