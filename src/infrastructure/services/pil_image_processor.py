"""PIL image processor service for image processing operations."""

import threading
from collections.abc import Callable
from io import BytesIO
from typing import Final

from PIL import Image, ImageTk

from src.domain.interfaces.image_processor import ImageProcessor, ProcessedImage


class PILImageProcessor(ImageProcessor):
    """Concrete implementation of image processing using PIL (Python Imaging Library)."""

    _RGBA_MODE: Final[str] = "RGBA"

    def fetch_image_sync(self, *, image_data: bytes) -> ProcessedImage:
        """Fetch and process an image synchronously.

        Args:
            image_data: The data of the image to fetch.

        Returns:
            The processed image.
        """
        return self._download_and_process_image(image_data=image_data)

    def fetch_image_async(
        self,
        *,
        image_data: bytes,
        on_success: Callable[[ProcessedImage], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None] = lambda: None,
        on_finished: Callable[[], None] = lambda: None,
        cancellation_check: Callable[[], bool] = lambda: False,
    ) -> threading.Thread:
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
        thread = threading.Thread(
            target=self._fetch_image_thread,
            args=(image_data, on_success, on_error, on_started, on_finished, cancellation_check),
            daemon=True,
        )
        thread.start()
        return thread

    def _fetch_image_thread(
        self,
        image_data: bytes,
        on_success: Callable[[ProcessedImage], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None],
        on_finished: Callable[[], None],
        cancellation_check: Callable[[], bool],
    ) -> None:
        """Fetch image in background thread.

        Args:
            image_data: The data of the image to fetch.
            on_success: Callback for successful image processing.
            on_error: Callback for error handling.
            on_started: Callback when operation starts.
            on_finished: Callback when operation completes.
            cancellation_check: Function to check if operation should be cancelled.
        """
        try:
            on_started()
            if not cancellation_check():
                processed_image = self._download_and_process_image(image_data=image_data)
                on_success(processed_image)

        except Exception as e:
            if not cancellation_check():
                on_error(f"Error loading image: {e!s}")
        finally:
            if not cancellation_check():
                on_finished()

    def _download_and_process_image(self, *, image_data: bytes) -> ProcessedImage:
        """Download and process image from URL.

        Args:
            image_data: The data of the image to fetch.

        Returns:
            Processed image ready for display, or None if cancelled/failed.
        """
        try:
            pil_image = Image.open(fp=BytesIO(initial_bytes=image_data))
            converted_image = pil_image.convert(self._RGBA_MODE) if pil_image.mode != self._RGBA_MODE else pil_image
            return ImageTk.PhotoImage(converted_image)  # type: ignore[no-untyped-call,return-value]

        except Exception as e:
            raise ValueError(f"Failed to load image: {e!s}") from e
