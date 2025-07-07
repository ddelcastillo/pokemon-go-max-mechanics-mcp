"""Tests for the Web Image Processing Service."""

import unittest
from unittest.mock import Mock

from src.application.services.web_image_processing import WebImageProcessingService
from src.domain.interfaces.image_processor import ImageProcessor
from src.domain.ports.outbound.http_client_port import HttpClientPort


class TestWebImageProcessingService(unittest.TestCase):
    """Test cases for WebImageProcessingService."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_image_processor = Mock(spec=ImageProcessor)
        # Create mock HTTP client that supports context manager protocol
        self.mock_http_client = Mock(spec=HttpClientPort)
        self.mock_http_client.__enter__ = Mock(return_value=self.mock_http_client)
        self.mock_http_client.__exit__ = Mock(return_value=None)
        self.service = WebImageProcessingService(
            image_processor=self.mock_image_processor, http_client=self.mock_http_client
        )

        # Mock callbacks (now expect only one parameter for on_success)
        self.mock_on_success = Mock()
        self.mock_on_error = Mock()
        self.mock_on_started = Mock()
        self.mock_on_finished = Mock()
        self.mock_cancellation_check = Mock(return_value=False)

        # Test data
        self.test_image_url = "https://example.com/image.png"
        self.test_image_data = b"fake_image_data"

    def test_initialization(self) -> None:
        """Test that the service initializes correctly."""
        service = WebImageProcessingService(
            image_processor=self.mock_image_processor, http_client=self.mock_http_client
        )

        self.assertIs(service.image_processor, self.mock_image_processor)
        self.assertIs(service.http_client, self.mock_http_client)

    def test_fetch_image_async_creates_thread(self) -> None:
        """Test that fetch_image_async creates and starts a thread."""
        result = self.service.fetch_image_async(
            image_url=self.test_image_url,
            on_success=self.mock_on_success,
            on_error=self.mock_on_error,
            on_started=self.mock_on_started,
            on_finished=self.mock_on_finished,
            cancellation_check=self.mock_cancellation_check,
        )

        # Verify a thread was created and started
        self.assertIsNotNone(result)
        self.assertTrue(result.daemon)

    def test_fetch_image_async_with_minimal_params(self) -> None:
        """Test that fetch_image_async works with minimal parameters."""
        result = self.service.fetch_image_async(
            image_url=self.test_image_url, on_success=self.mock_on_success, on_error=self.mock_on_error
        )

        # Verify a thread was created
        self.assertIsNotNone(result)
        self.assertTrue(result.daemon)

    def test_fetch_and_process_image_thread_calls_http_client(self) -> None:
        """Test that the thread method calls the HTTP client and processes the image."""
        # Configure HTTP client mock to return image data
        self.mock_http_client.get_binary.return_value = self.test_image_data

        # Configure image processor mock to return processed image
        mock_processed_image = Mock()
        self.mock_image_processor.fetch_image_sync.return_value = mock_processed_image

        # Call the thread method directly for testing
        self.service._fetch_and_process_image_thread(
            image_url=self.test_image_url,
            on_success=self.mock_on_success,
            on_error=self.mock_on_error,
            on_started=self.mock_on_started,
            on_finished=self.mock_on_finished,
            cancellation_check=self.mock_cancellation_check,
        )

        # Verify HTTP client was called
        self.mock_http_client.get_binary.assert_called_once_with(url=self.test_image_url)
        # Verify image processor sync method was called
        self.mock_image_processor.fetch_image_sync.assert_called_once_with(image_data=self.test_image_data)
        # Verify callbacks were called
        self.mock_on_started.assert_called_once()
        self.mock_on_success.assert_called_once_with(mock_processed_image)
        self.mock_on_finished.assert_called_once()

    def test_fetch_and_process_image_thread_handles_http_error(self) -> None:
        """Test that the thread method handles HTTP errors gracefully."""
        # Configure HTTP client mock to raise an exception
        self.mock_http_client.get_binary.side_effect = Exception("HTTP error")

        # Call the thread method directly for testing
        self.service._fetch_and_process_image_thread(
            image_url=self.test_image_url,
            on_success=self.mock_on_success,
            on_error=self.mock_on_error,
            on_started=self.mock_on_started,
            on_finished=self.mock_on_finished,
            cancellation_check=self.mock_cancellation_check,
        )

        # Verify error callback was called
        self.mock_on_error.assert_called_once()
        self.mock_on_finished.assert_called_once()
        self.mock_on_success.assert_not_called()

        # Verify error message contains the URL
        error_message = self.mock_on_error.call_args[0][0]
        self.assertIn(self.test_image_url, error_message)
        self.assertIn("HTTP error", error_message)

    def test_fetch_and_process_image_thread_handles_processor_error(self) -> None:
        """Test that the thread method handles image processor errors gracefully."""
        # Configure HTTP client mock to return image data
        self.mock_http_client.get_binary.return_value = self.test_image_data

        # Configure image processor mock to raise an exception
        self.mock_image_processor.fetch_image_sync.side_effect = Exception("Processing error")

        # Call the thread method directly for testing
        self.service._fetch_and_process_image_thread(
            image_url=self.test_image_url,
            on_success=self.mock_on_success,
            on_error=self.mock_on_error,
            on_started=self.mock_on_started,
            on_finished=self.mock_on_finished,
            cancellation_check=self.mock_cancellation_check,
        )

        # Verify error callback was called
        self.mock_on_error.assert_called_once()
        self.mock_on_finished.assert_called_once()
        self.mock_on_success.assert_not_called()

        # Verify error message contains the URL
        error_message = self.mock_on_error.call_args[0][0]
        self.assertIn(self.test_image_url, error_message)
        self.assertIn("Processing error", error_message)

    def test_fetch_and_process_image_thread_handles_cancellation(self) -> None:
        """Test that the thread method handles cancellation correctly."""
        # Configure HTTP client mock to return image data
        self.mock_http_client.get_binary.return_value = self.test_image_data

        # Configure cancellation check to return True after starting
        # The method checks cancellation multiple times, so provide enough values
        self.mock_cancellation_check.side_effect = [False, True, True, True, True, True]

        # Call the thread method directly for testing
        self.service._fetch_and_process_image_thread(
            image_url=self.test_image_url,
            on_success=self.mock_on_success,
            on_error=self.mock_on_error,
            on_started=self.mock_on_started,
            on_finished=self.mock_on_finished,
            cancellation_check=self.mock_cancellation_check,
        )

        # Verify callbacks were called appropriately
        self.mock_on_started.assert_called_once()
        # Success/error callbacks should not be called due to cancellation
        self.mock_on_success.assert_not_called()
        self.mock_on_error.assert_not_called()
        self.mock_on_finished.assert_not_called()

    def test_process_image_sync_delegates_to_processor(self) -> None:
        """Test that the sync method delegates to the image processor."""
        # Configure image processor mock to return processed image
        mock_processed_image = Mock()
        self.mock_image_processor.fetch_image_sync.return_value = mock_processed_image

        # Call the sync method
        result = self.service._process_image_sync(image_data=self.test_image_data)

        # Verify delegation to image processor
        self.mock_image_processor.fetch_image_sync.assert_called_once_with(image_data=self.test_image_data)
        self.assertIs(result, mock_processed_image)


if __name__ == "__main__":
    unittest.main()
