"""Tests for the Pokemon GO API adapter."""

from typing import Any
from unittest.mock import Mock

from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.domain.ports.outbound.pokemon_data_port import PokemonDict
from src.infrastructure.adapters.outbound.pokemon_go_api_adapter import (
    PokemonGoApiAdapter,
)


class TestPokemonGoApiAdapter:
    """Test suite for PokemonGoApiAdapter."""

    def setup_method(self) -> None:
        """
        Initializes a mock HTTP client and creates a `PokemonGoApiAdapter` instance for use in each test.
        """
        self.mock_http_client = Mock(spec=HttpClientPort)
        # Mock the context manager behavior
        self.mock_http_client.__enter__ = Mock(return_value=self.mock_http_client)
        self.mock_http_client.__exit__ = Mock(return_value=None)

        self.adapter = PokemonGoApiAdapter(http_client=self.mock_http_client)

    def test_fetch_pokemon_data_success(self) -> None:
        """
        Test that fetch_pokemon_data returns correct data when the API responds successfully with valid Pokémon information.
        """
        # Mock pokedex response - raw API response
        pokedex_data: PokemonDict = {
            "dexNr": 25,
            "names": {"English": "Pikachu"},
            "stats": {"stamina": 111, "attack": 112, "defense": 96},
        }

        # Configure mock response - single API call
        self.mock_http_client.get.return_value = pokedex_data

        # Call the method
        result = self.adapter.fetch_pokemon_data(pokemon_name="Pikachu")

        # Verify the result - should be the raw API response
        assert result == pokedex_data
        assert result["dexNr"] == 25
        assert result["names"]["English"] == "Pikachu"
        assert result["stats"]["stamina"] == 111

        # Verify only one API call was made
        assert self.mock_http_client.get.call_count == 1

    def test_fetch_pokemon_data_not_found(self) -> None:
        """
        Test that fetch_pokemon_data raises a ValueError when the API indicates the Pokémon is not found.
        
        Verifies that an exception from the HTTP client results in a ValueError with the expected error message.
        """
        # Mock HTTP client to raise an exception (Pokemon not found)
        self.mock_http_client.get.side_effect = Exception("HTTP 404: Not Found")

        # Call the method and expect ValueError
        try:
            self.adapter.fetch_pokemon_data(pokemon_name="NonExistentPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Error fetching Pokemon data from API: Status code unknown" in str(e)

    def test_fetch_pokemon_data_invalid_response(self) -> None:
        """
        Test that fetch_pokemon_data raises a ValueError when the API response is not a dictionary.
        """
        # Mock invalid response (not a dict)
        self.mock_http_client.get.return_value = "invalid response"

        # Call the method and expect ValueError
        try:
            self.adapter.fetch_pokemon_data(pokemon_name="TestPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Expected dictionary response" in str(e)

    def test_fetch_pokemon_data_missing_required_fields(self) -> None:
        """
        Test that fetching Pokemon data with a response missing required fields raises a ValueError.
        
        Verifies that if the API response lacks mandatory fields such as 'dexNr' and 'names', the adapter raises a ValueError indicating an invalid response format.
        """
        # Mock response missing required fields
        pokedex_data = {"id": "TEST_POKEMON"}  # Missing dexNr and names

        self.mock_http_client.get.return_value = pokedex_data

        # Call the method and expect ValueError
        try:
            self.adapter.fetch_pokemon_data(pokemon_name="TestPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Invalid response format" in str(e)

    def test_fetch_pokemon_data_empty_response(self) -> None:
        """Test Pokemon data fetch with empty response."""
        # Mock empty response
        self.mock_http_client.get.return_value = {}

        # Call the method and expect ValueError
        try:
            self.adapter.fetch_pokemon_data(pokemon_name="TestPokemon")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Pokemon 'TESTPOKEMON' not found" in str(e)

    def test_fetch_pokemon_data_uppercase_conversion(self) -> None:
        """
        Verify that the adapter converts the Pokémon name to uppercase before making the API call and returns the correct data.
        """
        # Mock successful response
        pokedex_data: PokemonDict = {
            "dexNr": 1,
            "names": {"English": "Bulbasaur"},
        }
        self.mock_http_client.get.return_value = pokedex_data

        # Call with lowercase name
        result = self.adapter.fetch_pokemon_data(pokemon_name="bulbasaur")

        # Verify the result
        assert result == pokedex_data

        # Verify the API was called with uppercase name
        expected_url = "https://pokemon-go-api.github.io/pokemon-go-api/api/pokedex/name/BULBASAUR.json"
        self.mock_http_client.get.assert_called_once_with(url=expected_url)

    def test_fetch_pokemon_data_complete_response(self) -> None:
        """
        Tests that fetch_pokemon_data returns the complete API response unchanged when all expected fields are present for a Pokémon.
        """
        # Mock complete pokedex response
        pokedex_data: PokemonDict = {
            "dexNr": 150,
            "names": {"English": "Mewtwo", "German": "Mewtu"},
            "stats": {"stamina": 214, "attack": 300, "defense": 182},
            "types": [{"type": "Psychic"}],
            "generation": 1,
        }

        self.mock_http_client.get.return_value = pokedex_data

        # Call the method
        result = self.adapter.fetch_pokemon_data(pokemon_name="Mewtwo")

        # Verify the complete response is returned unchanged
        assert result == pokedex_data
        assert result["dexNr"] == 150
        assert result["names"]["English"] == "Mewtwo"
        assert result["names"]["German"] == "Mewtu"
        assert result["stats"]["stamina"] == 214
        assert result["types"][0]["type"] == "Psychic"
        assert result["generation"] == 1
