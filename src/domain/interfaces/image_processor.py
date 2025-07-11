"""Image processor interface for handling image operations."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from threading import Thread
from typing import Protocol, runtime_checkable


@runtime_checkable
class ProcessedImage(Protocol):
    """Protocol for processed images that can be displayed in UI components.

    This protocol masks the underlying image implementation (like PIL.ImageTk.PhotoImage)
    to avoid leaking infrastructure concerns into the domain and application layers.
    """


class ImageProcessor(ABC):
    """Abstract interface for image processing operations."""

    @abstractmethod
    def fetch_image_sync(self, *, image_data: bytes) -> ProcessedImage:
        """Fetch and process an image synchronously."""
        raise NotImplementedError

    @abstractmethod
    def fetch_image_async(
        self,
        *,
        image_data: bytes,
        on_success: Callable[[ProcessedImage], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None] = lambda: None,
        on_finished: Callable[[], None] = lambda: None,
        cancellation_check: Callable[[], bool] = lambda: False,
    ) -> Thread:
        """Fetch and process an image asynchronously.

        Args:
            image_data: The data of the image to fetch.
            on_success: Callback called with processed_image on success.
            on_error: Callback called with error message on failure.
            on_started: Callback called when image fetching starts.
            on_finished: Callback called when operation completes (success or failure).
            cancellation_check: Function that returns True if operation should be cancelled.

        Returns:
            The thread handling the image fetch operation.
        """
        raise NotImplementedError
