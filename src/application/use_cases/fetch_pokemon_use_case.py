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
        """
        Initialize the FetchPokemonUseCase with a data port for retrieving Pokemon data.
        
        Parameters:
            pokemon_data_port: An interface for fetching Pokemon data as dictionaries.
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
        """
        Starts an asynchronous operation to fetch Pokemon data in a background thread.
        
        The method initiates a daemon thread that retrieves data for the specified Pokemon name using the injected data port. Callback functions are invoked for operation start, success, error, and completion events, provided the operation is not cancelled. A cancellation check function can be supplied to prevent unnecessary callback invocations if the operation is cancelled.
        
        Parameters:
            pokemon_name (str): The name of the Pokemon to fetch data for.
            on_success (Callable[[PokemonDict], None]): Called with the Pokemon data dictionary if retrieval succeeds.
            on_error (Callable[[str], None]): Called with an error message if retrieval fails.
            on_started (Callable[[], None], optional): Called when the fetch operation begins.
            on_finished (Callable[[], None], optional): Called when the operation completes, unless cancelled.
            cancellation_check (Callable[[], bool], optional): Returns True if the operation should be cancelled.
        
        Returns:
            threading.Thread: The thread executing the fetch operation.
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
        """
        Executes the Pokemon data fetch operation in a background thread, invoking appropriate callbacks for start, success, error, and completion, while respecting cancellation requests.
        
        Parameters:
            pokemon_name (str): Name of the Pokemon to fetch.
            on_success (Callable[[PokemonDict], None]): Called with the Pokemon data if retrieval succeeds.
            on_error (Callable[[str], None]): Called with an error message if retrieval fails.
            on_started (Callable[[], None]): Called when the operation begins.
            on_finished (Callable[[], None]): Called when the operation completes, unless cancelled.
            cancellation_check (Callable[[], bool]): Returns True if the operation should be cancelled.
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
