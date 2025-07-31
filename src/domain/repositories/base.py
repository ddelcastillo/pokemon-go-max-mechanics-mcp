from abc import ABC, abstractmethod


class BaseRepository[T](ABC):
    @abstractmethod
    def bulk_create(self, *, entities: list[T]) -> None:
        """Bulk create entities."""
        raise NotImplementedError
