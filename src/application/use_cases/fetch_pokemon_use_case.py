"""Use case for fetching Pokemon data."""

import threading
from collections.abc import Callable

from injector import inject

from src.domain.ports.outbound.pokemon_data_port import PokemonDataPort, PokemonDict


class FetchPokemonUseCase:
    """Use case for fetching Pokemon data asynchronously.

    This use case orchestrates the Pokemon data fetching process,
    handling threading, callbacks, and error management.
    It works with any type of Pokemon data through the PokemonDataPort.
    """

    @inject
    def __init__(self, *, pokemon_data_port: PokemonDataPort[PokemonDict]) -> None:
        """Initialize the fetch Pokemon use case.

        Args:
            pokemon_data_port: The port for Pokemon data retrieval that returns
                dictionary-based Pokemon data.
        """
        self._pokemon_data_port: PokemonDataPort[PokemonDict] = pokemon_data_port

    def fetch_pokemon_data_async(
        self,
        *,
        pokemon_name: str,
        on_success: Callable[[PokemonDict], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None] = lambda: None,
        on_finished: Callable[[], None] = lambda: None,
        cancellation_check: Callable[[], bool] = lambda: False,
    ) -> threading.Thread:
        """Fetch Pokemon data asynchronously.

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
        on_success: Callable[[PokemonDict], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None],
        on_finished: Callable[[], None],
        cancellation_check: Callable[[], bool],
    ) -> None:
        """Fetch Pokemon data in background thread.

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
            if (
                pokemon_data := self._pokemon_data_port.fetch_pokemon_data(pokemon_name=pokemon_name)
            ) and not cancellation_check():
                on_success(pokemon_data)
        except Exception as e:
            if not cancellation_check():
                on_error(f"Error searching for {pokemon_name}: {e!s}")
        finally:
            if not cancellation_check():
                on_finished()
