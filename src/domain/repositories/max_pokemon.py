from abc import abstractmethod

from src.domain.repositories.base import BaseRepository
from src.domain.value_objects.types import Type


class MaxPokemonRepository[T](BaseRepository[T]):
    @abstractmethod
    def get_by_id(self, *, id: int) -> T:
        """Get a Max Pokemon by its ID."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_by_name(self, *, name: str) -> T:
        """Get a Max Pokemon by its name."""
        raise NotImplementedError  # pragma: no cover

    def get_by_types(self, *, types: list[Type]) -> T:
        """Get a Max Pokemon by its types."""
        raise NotImplementedError  # pragma: no cover
