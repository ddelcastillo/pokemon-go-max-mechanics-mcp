"""Pokemon data port interface."""

from abc import ABC, abstractmethod
from typing import Any

type PokemonDict = dict[str, Any]


class PokemonDataPort[T](ABC):
    """Port interface for Pokemon data retrieval operations.

    This port defines the contract for fetching Pokemon data from external sources.
    Infrastructure adapters must implement this interface to provide concrete
    implementations for Pokemon data retrieval.

    Type Parameters:
        T: The type of data returned by the fetch operation.
           Use PokemonDict as a type alias for the common dict[str, Any] case.
    """

    @abstractmethod
    def fetch_pokemon_data(self, *, pokemon_name: str) -> T:
        """
        Retrieve data for a specified Pokemon by its name.
        
        Parameters:
            pokemon_name (str): The name of the Pokemon to retrieve.
        
        Returns:
            T: Data associated with the specified Pokemon.
        
        Raises:
            ValueError: If the Pokemon is not found or if an error occurs during data retrieval.
        """
        pass
