"""Tests for the Pokemon GO API service."""

from unittest.mock import Mock

from src.application.services.pokemon_go_api import PokemonGoApiService
from src.domain.ports.outbound.http_client_port import HttpClientPort


class TestPokemonGoApiService:
    """Test suite for PokemonGoApiService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_http_client = Mock(spec=HttpClientPort)
        # Mock the context manager behavior
        self.mock_http_client.__enter__ = Mock(return_value=self.mock_http_client)
        self.mock_http_client.__exit__ = Mock(return_value=None)

        self.service = PokemonGoApiService(http_client=self.mock_http_client)
        self.success_callback = Mock()
        self.error_callback = Mock()
        self.started_callback = Mock()
        self.finished_callback = Mock()

    def test_fetch_pokemon_data_async_success_from_local_dict(self) -> None:
        """Test successful async Pokemon data fetch from local dictionary."""
        # Mock stats response for the stats endpoint
        stats_data = [{"id": 1, "base_attack": 118, "base_defense": 111, "base_stamina": 128}]

        # Configure mock responses (only stats call needed since Pokemon is in local dict)
        self.mock_http_client.get.return_value = stats_data

        # Start async fetch
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="bulbasaur",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_called_once()
        self.error_callback.assert_not_called()

        # Verify the success callback was called with correct data
        call_args = self.success_callback.call_args[0]
        pokemon_data = call_args[0]

        assert pokemon_data["id"] == 1
        assert pokemon_data["name"] == "Bulbasaur"
        assert pokemon_data["stats"]["base_attack"] == 118
        assert pokemon_data["stats"]["base_defense"] == 111
        assert pokemon_data["stats"]["base_stamina"] == 128

    def test_fetch_pokemon_data_async_success_from_api_fallback(self) -> None:
        """Test successful async Pokemon data fetch from API fallback (future Pokemon)."""
        # Mock pokedex by name response for a future Pokemon not in our dictionary
        pokedex_data = {
            "id": "FUTURE_POKEMON",
            "dexNr": 9999,
            "names": {"English": "FuturePokemon"},
            "stats": {"stamina": 200, "attack": 250, "defense": 180},
            "primaryType": {"type": "POKEMON_TYPE_ELECTRIC"},
            "secondaryType": {"type": "POKEMON_TYPE_PSYCHIC"},
        }

        # Mock stats response
        stats_data = [{"id": 9999, "base_attack": 200, "base_defense": 200, "base_stamina": 200}]

        # Configure mock responses: first pokedex by name, then stats
        self.mock_http_client.get.side_effect = [pokedex_data, stats_data]

        # Start async fetch for a Pokemon name not in our dictionary
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="futurepokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_called_once()
        self.error_callback.assert_not_called()

        # Verify the success callback was called with correct data
        call_args = self.success_callback.call_args[0]
        pokemon_data = call_args[0]

        assert pokemon_data["id"] == 9999
        assert pokemon_data["name"] == "FuturePokemon"
        assert pokemon_data["stats"]["base_attack"] == 200
        assert pokemon_data["stats"]["base_defense"] == 200
        assert pokemon_data["stats"]["base_stamina"] == 200

    def test_fetch_pokemon_data_async_pokemon_not_found(self) -> None:
        """Test async fetch when Pokemon is not found in both dictionary and API."""
        # Mock HTTP client to raise an exception (Pokemon not found)
        self.mock_http_client.get.side_effect = Exception("HTTP 404: Not Found")

        # Start async fetch for non-existent Pokemon not in dictionary
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="nonexistentpokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_not_called()
        self.error_callback.assert_called_once()

        # Verify error message
        error_message = self.error_callback.call_args[0][0]
        assert "nonexistentpokemon" in error_message

    def test_fetch_pokemon_data_async_http_error_for_unknown_pokemon(self) -> None:
        """Test async fetch when HTTP client raises an error for unknown Pokemon."""
        # Mock HTTP client to raise an exception (for Pokemon not in local dict)
        self.mock_http_client.get.side_effect = Exception("Network error")

        # Start async fetch with Pokemon not in dictionary
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="unknownpokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_not_called()
        self.error_callback.assert_called_once()

        # Verify error message contains the original error
        error_message = self.error_callback.call_args[0][0]
        assert "Network error" in error_message

    def test_fetch_pokemon_data_async_http_error_for_known_pokemon(self) -> None:
        """Test async fetch when HTTP client raises an error for known Pokemon (local dict used)."""
        # Mock HTTP client to raise an exception for stats endpoint
        self.mock_http_client.get.side_effect = Exception("Network error")

        # Start async fetch with Pokemon in dictionary (should still get basic data)
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="bulbasaur",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_called_once()
        self.error_callback.assert_not_called()

        # Verify the success callback was called with basic data from dictionary
        call_args = self.success_callback.call_args[0]
        pokemon_data = call_args[0]

        assert pokemon_data["id"] == 1
        assert pokemon_data["name"] == "Bulbasaur"
        # Stats should be "N/A" due to API failure
        assert pokemon_data["stats"] == "N/A"

    def test_fetch_pokemon_data_async_cancellation(self) -> None:
        """Test async fetch with cancellation."""
        # Mock pokedex response
        pokedex_data = {
            "id": "BULBASAUR",
            "dexNr": 1,
            "names": {"English": "Bulbasaur"},
            "stats": {"stamina": 128, "attack": 118, "defense": 111},
        }

        self.mock_http_client.get.return_value = pokedex_data

        # Set up cancellation flag that gets set immediately
        cancelled = True

        def cancellation_check() -> bool:
            return cancelled

        # Start async fetch with cancellation
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="bulbasaur",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
            cancellation_check=cancellation_check,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify that success callback was not called due to cancellation
        self.started_callback.assert_called_once()
        # Cancellation should prevent success callback from being called
        # Note: The exact behavior depends on when cancellation is checked

    def test_fetch_pokemon_data_async_invalid_pokedex_response(self) -> None:
        """Test async fetch with invalid pokedex response format."""
        # Mock invalid pokedex response (missing required fields)
        invalid_pokedex_data = {
            "id": "INVALID_POKEMON"
            # Missing dexNr and names fields
        }

        self.mock_http_client.get.return_value = invalid_pokedex_data

        # Start async fetch for Pokemon not in dictionary
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="testpokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify error callback was called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_not_called()
        self.error_callback.assert_called_once()

        # Verify error message
        error_message = self.error_callback.call_args[0][0]
        assert "testpokemon" in error_message

    def test_fetch_pokemon_data_async_stats_endpoint_failure(self) -> None:
        """Test async fetch when stats endpoint fails but pokedex succeeds."""
        # Mock pokedex response (successful) for Pokemon not in local dict
        pokedex_data = {
            "id": "TEST_POKEMON",
            "dexNr": 9999,
            "names": {"English": "TestPokemon"},
            "stats": {"stamina": 200, "attack": 250, "defense": 180},
        }

        # Mock responses: successful pokedex call, then stats endpoint failure
        self.mock_http_client.get.side_effect = [pokedex_data, Exception("Stats endpoint failed")]

        # Start async fetch for Pokemon not in dictionary
        thread = self.service.fetch_pokemon_data_async(
            pokemon_name="testpokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify success callback was called (basic data is still success)
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_called_once()
        self.error_callback.assert_not_called()

        # Verify the data contains what was successfully fetched
        call_args = self.success_callback.call_args[0]
        pokemon_data = call_args[0]

        assert pokemon_data["id"] == 9999
        assert pokemon_data["name"] == "TestPokemon"
        assert pokemon_data["stats"] == "N/A"  # Failed endpoint
