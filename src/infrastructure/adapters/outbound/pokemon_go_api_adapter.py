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
        """
        Initialize the adapter with an HTTP client for making API requests to the Pokemon GO API.
        """
        self._http_client: HttpClientPort = http_client

    def fetch_pokemon_data(self, *, pokemon_name: str) -> PokemonDict:
        """
        Retrieve data for a specified Pokemon from the Pokemon GO API.
        
        Parameters:
            pokemon_name (str): The name of the Pokemon to retrieve.
        
        Returns:
            PokemonDict: A dictionary containing the Pokemon's data.
        
        Raises:
            ValueError: If the Pokemon is not found or if an error occurs during data retrieval.
        """
        with self._http_client as client:
            return self._fetch_pokemon_data_from_api(client=client, pokemon_name=pokemon_name)

    def _fetch_pokemon_data_from_api(self, *, client: HttpClientPort, pokemon_name: str) -> PokemonDict:
        """
        Retrieve and validate Pokemon data from the Pokemon GO API by name.
        
        Attempts to fetch the specified Pokemon's data using the provided HTTP client. Validates that the response is a non-empty dictionary containing the required keys `"dexNr"` and `"names"`. Raises a `ValueError` if the API response is invalid, the Pokemon is not found, or an error occurs during the request.
        
        Parameters:
            client (HttpClientPort): The HTTP client used to perform the API request.
            pokemon_name (str): The name of the Pokemon to retrieve.
        
        Returns:
            PokemonDict: A dictionary containing the Pokemon's data.
        
        Raises:
            ValueError: If the API response is invalid, the Pokemon is not found, or an error occurs during the request.
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
