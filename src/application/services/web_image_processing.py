"""Image service for handling image operations at the application layer."""

import threading
from collections.abc import Callable

from injector import inject

from src.domain.interfaces.image_processor import ImageProcessor, ProcessedImage
from src.domain.ports.outbound.http_client_port import HttpClientPort


class WebImageProcessingService:
    """Application service for handling image operations on the web.

    This service is responsible for fetching image data from URLs and processing it.
    It uses the ImageProcessor interface to process the image data.
    It uses the HttpClientPort to fetch the image data from URLs.
    """

    @inject
    def __init__(self, *, image_processor: ImageProcessor, http_client: HttpClientPort) -> None:
        """Initialize the WebImageProcessingService.

        Args:
            image_processor: The image processor interface for handling image operations.
            http_client: The HTTP client for fetching image data from URLs.
        """
        self.image_processor = image_processor
        self.http_client = http_client

    def fetch_image_async(
        self,
        *,
        image_url: str,
        on_success: Callable[[ProcessedImage], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None] = lambda: None,
        on_finished: Callable[[], None] = lambda: None,
        cancellation_check: Callable[[], bool] = lambda: False,
    ) -> threading.Thread:
        """Fetch and process an image asynchronously.

        Args:
            image_url: The URL of the image to fetch.
            on_success: Callback called with processed_image on success.
            on_error: Callback called with error message on failure.
            on_started: Callback called when image fetching starts.
            on_finished: Callback called when operation completes (success or failure).
            cancellation_check: Function that returns True if operation should be cancelled.

        Returns:
            The thread handling the image fetch operation.
        """
        # Create a wrapper thread that fetches the image data first, then processes it
        thread = threading.Thread(
            target=self._fetch_and_process_image_thread,
            args=(image_url, on_success, on_error, on_started, on_finished, cancellation_check),
            daemon=True,
        )
        thread.start()
        return thread

    def _fetch_and_process_image_thread(
        self,
        image_url: str,
        on_success: Callable[[ProcessedImage], None],
        on_error: Callable[[str], None],
        on_started: Callable[[], None],
        on_finished: Callable[[], None],
        cancellation_check: Callable[[], bool],
    ) -> None:
        """Fetch image data from URL and then process it.

        Args:
            image_url: The URL of the image to fetch.
            on_success: Callback for successful image processing.
            on_error: Callback for error handling.
            on_started: Callback when operation starts.
            on_finished: Callback when operation completes.
            cancellation_check: Function to check if operation should be cancelled.
        """
        try:
            on_started()
            if cancellation_check():
                return
            with self.http_client as client:
                if cancellation_check():
                    return
                image_data: bytes = client.get_binary(url=image_url)
                if cancellation_check():
                    return
            # We don't start the processor thread here, we call it sync since we're already in a background thread.
            if (processed_image := self._process_image_sync(image_data=image_data)) and not cancellation_check():
                on_success(processed_image)
        except Exception as e:
            if not cancellation_check():
                on_error(f"Error loading image from {image_url}: {e!s}")
        finally:
            if not cancellation_check():
                on_finished()

    def _process_image_sync(self, *, image_data: bytes) -> ProcessedImage:
        """Process image data synchronously.

        Args:
            image_data: The binary image data.

        Returns:
            The processed image.
        """
        return self.image_processor.fetch_image_sync(image_data=image_data)
