from unittest.mock import Mock

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.domain.ports.outbound.pokemon_data_port import PokemonDict
from src.infrastructure.adapters.outbound.pokemon_go_api_adapter import (
    PokemonGoApiAdapter,
)


class TestPokemonGoApiAdapter:
    """Test suite for PokemonGoApiAdapter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_http_client = Mock(spec=HttpClientPort)
        self.mock_http_client.__enter__ = Mock(return_value=self.mock_http_client)
        self.mock_http_client.__exit__ = Mock(return_value=None)

        self.adapter = PokemonGoApiAdapter(http_client=self.mock_http_client)

    def test_fetch_pokemon_data_success(self) -> None:
        """Test successful Pokemon data fetch from API."""
        pokedex_data: PokemonDict = {
            "dexNr": 25,
            "names": {"English": "Pikachu"},
            "stats": {"stamina": 111, "attack": 112, "defense": 96},
        }

        self.mock_http_client.get.return_value = pokedex_data

        result = self.adapter.fetch_pokemon_data(pokemon_name="Pikachu")

        assert result == pokedex_data
        assert result["dexNr"] == 25
        assert result["names"]["English"] == "Pikachu"
        assert result["stats"]["stamina"] == 111

        assert self.mock_http_client.get.call_count == 1

    def test_fetch_pokemon_data_not_found(self) -> None:
        """Test Pokemon data fetch when Pokemon is not found."""
        self.mock_http_client.get.side_effect = Exception("HTTP 404: Not Found")

        try:
            self.adapter.fetch_pokemon_data(pokemon_name="NonExistentPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Error fetching Pokemon data from API: Status code unknown" in str(e)

    def test_fetch_pokemon_data_invalid_response(self) -> None:
        """Test Pokemon data fetch with invalid response format."""
        self.mock_http_client.get.return_value = "invalid response"

        try:
            self.adapter.fetch_pokemon_data(pokemon_name="TestPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Expected dictionary response" in str(e)

    def test_fetch_pokemon_data_missing_required_fields(self) -> None:
        """Test Pokemon data fetch with missing required fields."""
        pokedex_data = {"id": "TEST_POKEMON"}

        self.mock_http_client.get.return_value = pokedex_data

        try:
            self.adapter.fetch_pokemon_data(pokemon_name="TestPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Invalid response format" in str(e)

    def test_fetch_pokemon_data_empty_response(self) -> None:
        """Test Pokemon data fetch with empty response."""
        self.mock_http_client.get.return_value = {}

        try:
            self.adapter.fetch_pokemon_data(pokemon_name="TestPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Pokemon 'TESTPOKEMON' not found" in str(e)

    def test_fetch_pokemon_data_uppercase_conversion(self) -> None:
        """Test that Pokemon names are converted to uppercase for API calls."""
        pokedex_data: PokemonDict = {
            "dexNr": 1,
            "names": {"English": "Bulbasaur"},
        }
        self.mock_http_client.get.return_value = pokedex_data

        result = self.adapter.fetch_pokemon_data(pokemon_name="bulbasaur")

        assert result == pokedex_data

        expected_url = "https://pokemon-go-api.github.io/pokemon-go-api/api/pokedex/name/BULBASAUR.json"
        self.mock_http_client.get.assert_called_once_with(url=expected_url)

    def test_fetch_pokemon_data_complete_response(self) -> None:
        """Test Pokemon data fetch with complete API response."""
        pokedex_data: PokemonDict = {
            "dexNr": 150,
            "names": {"English": "Mewtwo", "German": "Mewtu"},
            "stats": {"stamina": 214, "attack": 300, "defense": 182},
            "types": [{"type": "Psychic"}],
            "generation": 1,
        }

        self.mock_http_client.get.return_value = pokedex_data

        result = self.adapter.fetch_pokemon_data(pokemon_name="Mewtwo")

        assert result == pokedex_data
        assert result["dexNr"] == 150
        assert result["names"]["English"] == "Mewtwo"
        assert result["names"]["German"] == "Mewtu"
        assert result["stats"]["stamina"] == 214
        assert result["types"][0]["type"] == "Psychic"
        assert result["generation"] == 1
