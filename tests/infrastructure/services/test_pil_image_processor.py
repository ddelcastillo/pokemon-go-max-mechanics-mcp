"""Tests for the PIL Image Processor Service."""

import unittest
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.services.pil_image_processor import PILImageProcessor


class TestPILImageProcessor(unittest.TestCase):
    """Test cases for PILImageProcessor."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = PILImageProcessor()

        # Mock callbacks
        self.mock_on_success = Mock()
        self.mock_on_error = Mock()
        self.mock_on_started = Mock()
        self.mock_on_finished = Mock()
        self.mock_cancellation_check = Mock(return_value=False)

        # Test data
        self.test_image_data = b"fake_image_data"

    def test_initialization(self) -> None:
        """Test that the service initializes correctly."""
        service = PILImageProcessor()

        # Service should initialize without any dependencies
        self.assertIsInstance(service, PILImageProcessor)

    @patch("threading.Thread")
    def test_fetch_image_async_starts_thread(self, mock_thread: Mock) -> None:
        """Test that fetch_image_async starts a daemon thread."""
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        result = self.service.fetch_image_async(
            image_data=self.test_image_data,
            on_success=self.mock_on_success,
            on_error=self.mock_on_error,
            on_started=self.mock_on_started,
            on_finished=self.mock_on_finished,
            cancellation_check=self.mock_cancellation_check,
        )

        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        self.assertIs(result, mock_thread_instance)

        # Verify it's a daemon thread
        _, kwargs = mock_thread.call_args
        self.assertTrue(kwargs["daemon"])

    @patch("src.infrastructure.services.pil_image_processor.Image")
    @patch("src.infrastructure.services.pil_image_processor.ImageTk.PhotoImage")
    def test_download_and_process_image_success(self, mock_photo_image: Mock, mock_image: Mock) -> None:
        """Test successful image processing."""
        # Mock PIL image processing
        mock_pil_image = Mock()
        mock_pil_image.mode = "RGB"
        mock_converted_image = Mock()
        mock_final_image = Mock()

        mock_image.open.return_value = mock_pil_image
        mock_image.Mode.RGBA = "RGBA"
        mock_pil_image.convert.return_value = mock_converted_image
        mock_photo_image.return_value = mock_final_image

        result = self.service._download_and_process_image(image_data=self.test_image_data)

        # Verify image processing steps
        mock_image.open.assert_called_once()
        mock_pil_image.convert.assert_called_once_with("RGBA")
        mock_photo_image.assert_called_once_with(mock_converted_image)

        self.assertIs(result, mock_final_image)

    @patch("src.infrastructure.services.pil_image_processor.Image")
    def test_download_and_process_image_with_rgba_mode(self, mock_image: Mock) -> None:
        """Test image processing when image is already in RGBA mode."""
        # Mock PIL image already in RGBA mode
        mock_pil_image = Mock()
        mock_pil_image.mode = "RGBA"

        mock_image.open.return_value = mock_pil_image
        mock_image.Mode.RGBA = "RGBA"

        with patch("src.infrastructure.services.pil_image_processor.ImageTk.PhotoImage") as mock_photo_image:
            mock_final_image = Mock()
            mock_photo_image.return_value = mock_final_image

            result = self.service._download_and_process_image(image_data=self.test_image_data)

            # Verify image processing steps
            mock_image.open.assert_called_once()
            # Should not convert since it's already RGBA
            mock_pil_image.convert.assert_not_called()
            mock_photo_image.assert_called_once_with(mock_pil_image)

            self.assertIs(result, mock_final_image)

    def test_download_and_process_image_error(self) -> None:
        """Test handling of error during image processing."""
        with (
            patch(
                "src.infrastructure.services.pil_image_processor.Image.open", side_effect=Exception("Invalid image")
            ),
            self.assertRaisesRegex(ValueError, "Failed to load image"),
        ):
            self.service._download_and_process_image(image_data=self.test_image_data)

    def test_fetch_image_thread_success(self) -> None:
        """Test successful image processing in the fetching thread."""
        with patch.object(self.service, "_download_and_process_image") as mock_download:
            mock_processed_image = Mock()
            mock_download.return_value = mock_processed_image

            self.service._fetch_image_thread(
                image_data=self.test_image_data,
                on_success=self.mock_on_success,
                on_error=self.mock_on_error,
                on_started=self.mock_on_started,
                on_finished=self.mock_on_finished,
                cancellation_check=self.mock_cancellation_check,
            )

            # Verify method calls
            self.mock_on_started.assert_called_once()
            mock_download.assert_called_once_with(image_data=self.test_image_data)
            self.mock_on_success.assert_called_once_with(mock_processed_image)
            self.mock_on_finished.assert_called_once()

    def test_fetch_image_thread_exception_handling(self) -> None:
        """Test exception handling in the image fetching thread."""
        with patch.object(self.service, "_download_and_process_image", side_effect=Exception("Processing error")):
            self.service._fetch_image_thread(
                image_data=self.test_image_data,
                on_success=self.mock_on_success,
                on_error=self.mock_on_error,
                on_started=self.mock_on_started,
                on_finished=self.mock_on_finished,
                cancellation_check=self.mock_cancellation_check,
            )

            self.mock_on_started.assert_called_once()
            self.mock_on_error.assert_called_once()
            error_call_args = self.mock_on_error.call_args[0][0]
            self.assertIn("Error loading image", error_call_args)
            self.assertIn("Processing error", error_call_args)
            self.mock_on_success.assert_not_called()
            self.mock_on_finished.assert_called_once()

    def test_fetch_image_thread_early_cancellation(self) -> None:
        """Test early cancellation before image processing."""
        # Mock cancellation to return True immediately
        self.mock_cancellation_check.return_value = True

        with patch.object(self.service, "_download_and_process_image") as mock_download:
            self.service._fetch_image_thread(
                image_data=self.test_image_data,
                on_success=self.mock_on_success,
                on_error=self.mock_on_error,
                on_started=self.mock_on_started,
                on_finished=self.mock_on_finished,
                cancellation_check=self.mock_cancellation_check,
            )

            # Should start but not proceed due to immediate cancellation
            self.mock_on_started.assert_called_once()
            mock_download.assert_not_called()
            self.mock_on_success.assert_not_called()
            self.mock_on_error.assert_not_called()
            self.mock_on_finished.assert_not_called()

    def test_fetch_image_sync_success(self) -> None:
        """Test successful synchronous image processing."""
        with patch.object(self.service, "_download_and_process_image") as mock_download:
            mock_processed_image = Mock()
            mock_download.return_value = mock_processed_image

            result = self.service.fetch_image_sync(image_data=self.test_image_data)

            # Verify delegation to download method
            mock_download.assert_called_once_with(image_data=self.test_image_data)
            self.assertIs(result, mock_processed_image)

    def test_fetch_image_sync_error_propagation(self) -> None:
        """Test that synchronous method propagates errors correctly."""
        with (
            patch.object(self.service, "_download_and_process_image", side_effect=ValueError("Processing error")),
            self.assertRaisesRegex(ValueError, "Processing error"),
        ):
            self.service.fetch_image_sync(image_data=self.test_image_data)


# Pytest-style parametrized test (separate from unittest class)
@pytest.mark.parametrize("image_data", [b"fake_image_data", b"another_image_data", b"third_image_data"])
def test_fetch_image_sync_with_different_data_parametrized(image_data: bytes) -> None:
    """Test synchronous method with different image data using pytest parametrization."""
    service = PILImageProcessor()

    with patch.object(service, "_download_and_process_image") as mock_download:
        mock_processed_image = Mock()
        mock_download.return_value = mock_processed_image

        result = service.fetch_image_sync(image_data=image_data)

        mock_download.assert_called_once_with(image_data=image_data)
        assert result is mock_processed_image


if __name__ == "__main__":
    unittest.main()
