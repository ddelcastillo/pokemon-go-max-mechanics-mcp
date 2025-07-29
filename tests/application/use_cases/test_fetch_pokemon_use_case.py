from unittest.mock import Mock

from src.application.use_cases.fetch_pokemon_use_case import FetchPokemonUseCase
from src.domain.ports.outbound.pokemon_data_port import PokemonDataPort, PokemonDict


class TestFetchPokemonUseCase:
    """Test suite for FetchPokemonUseCase."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_pokemon_data_port: Mock = Mock(spec=PokemonDataPort[PokemonDict])
        self.use_case: FetchPokemonUseCase = FetchPokemonUseCase(pokemon_data_port=self.mock_pokemon_data_port)
        self.success_callback: Mock = Mock()
        self.error_callback: Mock = Mock()
        self.started_callback: Mock = Mock()
        self.finished_callback: Mock = Mock()

    def test_fetch_pokemon_data_async_success(self) -> None:
        """Test successful async Pokemon data fetch."""
        pokemon_data: PokemonDict = {
            "id": 25,
            "name": "Pikachu",
            "stats": {"base_attack": 112, "base_defense": 96, "base_stamina": 111},
        }
        self.mock_pokemon_data_port.fetch_pokemon_data.return_value = pokemon_data

        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="Pikachu",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )
        thread.join(timeout=2.0)

        self.mock_pokemon_data_port.fetch_pokemon_data.assert_called_once_with(pokemon_name="Pikachu")
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_called_once_with(pokemon_data)  # Called with the correct data.
        self.error_callback.assert_not_called()

    def test_fetch_pokemon_data_async_error(self) -> None:
        """Test async Pokemon data fetch with error."""
        self.mock_pokemon_data_port.fetch_pokemon_data.side_effect = ValueError("Pokemon not found")

        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="NonExistentPokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )
        thread.join(timeout=2.0)

        self.mock_pokemon_data_port.fetch_pokemon_data.assert_called_once_with(pokemon_name="NonExistentPokemon")
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_not_called()
        self.error_callback.assert_called_once()

        error_message = self.error_callback.call_args[0][0]
        assert "Error searching for NonExistentPokemon" in error_message
        assert "Pokemon not found" in error_message

    def test_fetch_pokemon_data_async_cancellation(self) -> None:
        """Test async Pokemon data fetch with cancellation."""
        pokemon_data = {
            "id": 25,
            "name": "Pikachu",
            "stats": {"base_attack": 112, "base_defense": 96, "base_stamina": 111},
        }
        self.mock_pokemon_data_port.fetch_pokemon_data.return_value = pokemon_data
        cancelled = True

        def cancellation_check() -> bool:
            return cancelled

        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="Pikachu",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
            cancellation_check=cancellation_check,
        )

        thread.join(timeout=2.0)

        self.started_callback.assert_called_once()

        self.mock_pokemon_data_port.fetch_pokemon_data.assert_not_called()
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_not_called()
        self.error_callback.assert_not_called()

    def test_fetch_pokemon_data_async_empty_data(self) -> None:
        """Test async Pokemon data fetch with empty data."""
        self.mock_pokemon_data_port.fetch_pokemon_data.return_value = {}

        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="TestPokemon",
            on_success=self.success_callback,
            on_error=self.error_callback,
            on_started=self.started_callback,
            on_finished=self.finished_callback,
        )
        thread.join(timeout=2.0)

        self.mock_pokemon_data_port.fetch_pokemon_data.assert_called_once_with(pokemon_name="TestPokemon")
        self.started_callback.assert_called_once()
        self.finished_callback.assert_called_once()
        self.success_callback.assert_not_called()  # Empty data is falsy, so success callback should not be called.
        self.error_callback.assert_not_called()

    def test_fetch_pokemon_data_async_returns_thread(self) -> None:
        """Test that async fetch returns a thread."""
        thread = self.use_case.fetch_pokemon_data_async(
            pokemon_name="Pikachu",
            on_success=self.success_callback,
            on_error=self.error_callback,
        )

        assert hasattr(thread, "join")
        assert hasattr(thread, "is_alive")

        thread.join(timeout=2.0)
