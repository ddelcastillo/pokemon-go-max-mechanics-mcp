"""Tests for the fetch Pokemon use case."""

from unittest.mock import Mock

from src.application.use_cases.fetch_pokemon_use_case import FetchPokemonUseCase
from src.domain.ports.outbound.pokemon_data_port import PokemonDataPort, PokemonDict


class TestFetchPokemonUseCase:
    """Test suite for FetchPokemonUseCase."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_pokemon_data_port = Mock(spec=PokemonDataPort[PokemonDict])
        self.use_case = FetchPokemonUseCase(pokemon_data_port=self.mock_pokemon_data_port)

        # Mock callbacks
        self.success_callback = Mock()
        self.error_callback = Mock()
        self.started_callback = Mock()
        self.finished_callback = Mock()

    def test_fetch_pokemon_data_async_success(self) -> None:
        """Test successful async Pokemon data fetch."""
        # Mock Pokemon data
        pokemon_data: PokemonDict = {
            "id": 25,
            "name": "Pikachu",
            "stats": {"base_attack": 112, "base_defense": 96, "base_stamina": 111},
        }

        # Configure mock port to return the data
        self.mock_pokemon_data_port.fetch_pokemon_data.return_value = pokemon_data

        # Start async fetch
        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="Pikachu",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify port was called with correct parameter
        self.mock_pokemon_data_port.fetch_pokemon_data.assert_called_once_with(pokemon_name="Pikachu")

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_called_once_with(pokemon_data)
        self.error_callback.assert_not_called()

    def test_fetch_pokemon_data_async_error(self) -> None:
        """Test async Pokemon data fetch with error."""
        # Configure mock port to raise an exception
        self.mock_pokemon_data_port.fetch_pokemon_data.side_effect = ValueError("Pokemon not found")

        # Start async fetch
        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="NonExistentPokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify port was called
        self.mock_pokemon_data_port.fetch_pokemon_data.assert_called_once_with(pokemon_name="NonExistentPokemon")

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_not_called()
        self.error_callback.assert_called_once()

        # Verify error message
        error_message = self.error_callback.call_args[0][0]
        assert "Error searching for NonExistentPokemon" in error_message
        assert "Pokemon not found" in error_message

    def test_fetch_pokemon_data_async_cancellation(self) -> None:
        """Test async Pokemon data fetch with cancellation."""
        # Mock Pokemon data
        pokemon_data = {
            "id": 25,
            "name": "Pikachu",
            "stats": {"base_attack": 112, "base_defense": 96, "base_stamina": 111},
        }

        # Configure mock port to return the data
        self.mock_pokemon_data_port.fetch_pokemon_data.return_value = pokemon_data

        # Set up cancellation flag that gets set immediately
        cancelled = True

        def cancellation_check() -> bool:
            return cancelled

        # Start async fetch with cancellation
        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="Pikachu",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
            cancellation_check=cancellation_check,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify that started callback was called
        self.started_callback.assert_called_once()

        # Due to cancellation, the port might not be called and callbacks should not be called
        # The exact behavior depends on when cancellation is checked

    def test_fetch_pokemon_data_async_empty_data(self) -> None:
        """Test async Pokemon data fetch with empty data."""
        # Configure mock port to return empty data
        self.mock_pokemon_data_port.fetch_pokemon_data.return_value = {}

        # Start async fetch
        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="TestPokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )

        # Wait for thread to complete
        thread.join(timeout=2.0)

        # Verify port was called
        self.mock_pokemon_data_port.fetch_pokemon_data.assert_called_once_with(pokemon_name="TestPokemon")

        # Verify callbacks were called
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        # Empty data is falsy, so success callback should not be called
        self.success_callback.assert_not_called()
        self.error_callback.assert_not_called()

    def test_fetch_pokemon_data_async_returns_thread(self) -> None:
        """Test that async fetch returns a thread."""
        # Mock Pokemon data
        pokemon_data = {"id": 25, "name": "Pikachu"}
        self.mock_pokemon_data_port.fetch_pokemon_data.return_value = pokemon_data

        # Start async fetch
        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="Pikachu",
            on_success=self.success_callback,
            on_error=self.error_callback,
        )

        # Verify it returns a thread
        assert hasattr(thread, "join")
        assert hasattr(thread, "is_alive")

        # Clean up
        thread.join(timeout=2.0)
