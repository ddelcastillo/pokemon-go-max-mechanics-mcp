"""Tests for the Pokedex view."""

import unittest
from unittest.mock import Mock, patch

from src.application.constants.api_constants import (
    POKEMON_ASSETS_KEY,
    POKEMON_IMAGE_KEY,
    POKEMON_SHINY_IMAGE_KEY,
)
from src.application.services.pokemon_go_api import PokemonGoApiService
from src.application.services.web_image_processing import WebImageProcessingService
from src.application.views.pokedex_view import PokedexView
from src.domain.interfaces.image_processor import ProcessedImage


class TestPokedexView(unittest.TestCase):
    """Test cases for PokedexView."""

    def create_mock_image_service(self) -> Mock:
        """Create a mock image service."""
        return Mock(spec=WebImageProcessingService)

    def create_mock_pokemon_go_api_service(self) -> Mock:
        """Create a mock Pokemon GO API service."""
        return Mock(spec=PokemonGoApiService)

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_parent = Mock()
        self.mock_navigator = Mock()
        self.mock_image_service = self.create_mock_image_service()
        self.mock_pokemon_go_api_service = self.create_mock_pokemon_go_api_service()

        self.pokedex_view = PokedexView(
            parent=self.mock_parent,
            navigator=self.mock_navigator,
            image_service=self.mock_image_service,
            pokemon_go_api_service=self.mock_pokemon_go_api_service,
        )

    def test_initialization(self) -> None:
        """Test that the view initializes correctly."""
        self.assertIs(self.pokedex_view.image_service, self.mock_image_service)
        self.assertIs(self.pokedex_view.pokemon_go_api_service, self.mock_pokemon_go_api_service)
        self.assertIsNone(self.pokedex_view._current_search_thread)
        self.assertIsNone(self.pokedex_view._current_base_image_thread)
        self.assertIsNone(self.pokedex_view._current_shiny_image_thread)
        self.assertFalse(self.pokedex_view._search_cancelled)
        self.assertFalse(self.pokedex_view._base_image_search_cancelled)
        self.assertFalse(self.pokedex_view._shiny_image_search_cancelled)

    def test_fetch_pokemon_base_image_with_valid_data(self) -> None:
        """Test fetching Pokemon base image with valid data containing image URL."""
        # Mock data with base image URL
        image_url = "https://example.com/pikachu.png"
        pokemon_name = "Pikachu"

        # Mock the image service fetch method
        mock_thread = Mock()
        self.mock_image_service.fetch_image_async.return_value = mock_thread

        # Call the method
        self.pokedex_view._fetch_pokemon_base_image(image_url=image_url, pokemon_name=pokemon_name)

        # Verify the image service was called with correct parameters
        self.mock_image_service.fetch_image_async.assert_called_once()
        call_args = self.mock_image_service.fetch_image_async.call_args
        self.assertEqual(call_args.kwargs["image_url"], image_url)
        self.assertEqual(call_args.kwargs["on_success"], self.pokedex_view._on_base_image_success)
        self.assertEqual(call_args.kwargs["on_error"], self.pokedex_view._on_base_image_error)
        # Verify the pokemon name is stored internally
        self.assertEqual(self.pokedex_view._current_pokemon_name, pokemon_name)

    def test_fetch_pokemon_shiny_image_with_valid_data(self) -> None:
        """Test fetching Pokemon shiny image with valid data containing image URL."""
        # Mock data with shiny image URL
        image_url = "https://example.com/pikachu_shiny.png"
        pokemon_name = "Pikachu"

        # Mock the image service fetch method
        mock_thread = Mock()
        self.mock_image_service.fetch_image_async.return_value = mock_thread

        # Call the method
        self.pokedex_view._fetch_pokemon_shiny_image(image_url=image_url, pokemon_name=pokemon_name)

        # Verify the image service was called with correct parameters
        self.mock_image_service.fetch_image_async.assert_called_once()
        call_args = self.mock_image_service.fetch_image_async.call_args
        self.assertEqual(call_args.kwargs["image_url"], image_url)
        self.assertEqual(call_args.kwargs["on_success"], self.pokedex_view._on_shiny_image_success)
        self.assertEqual(call_args.kwargs["on_error"], self.pokedex_view._on_shiny_image_error)
        # Verify the pokemon name is stored internally
        self.assertEqual(self.pokedex_view._current_pokemon_name, pokemon_name)

    def test_on_pokemon_data_success_with_both_images(self) -> None:
        """Test handling successful Pokemon data with both base and shiny image URLs."""
        # Mock data with both image URLs in assets (using 'id' field as per API)
        mock_data = {
            "id": 25,  # Using numeric ID as per the actual API
            POKEMON_ASSETS_KEY: {
                POKEMON_IMAGE_KEY: "https://example.com/pikachu.png",
                POKEMON_SHINY_IMAGE_KEY: "https://example.com/pikachu_shiny.png",
            },
        }

        # Mock the frame and image fetching
        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            self.pokedex_view._on_pokemon_data_success(mock_data)

            # Verify base image fetching was called (pokemon name will be "25" from id field)
            mock_fetch_base.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_IMAGE_KEY], pokemon_name="25"
            )
            # Verify shiny image fetching was called
            mock_fetch_shiny.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_SHINY_IMAGE_KEY], pokemon_name="25"
            )

    def test_on_pokemon_data_success_with_base_image_only(self) -> None:
        """Test handling successful Pokemon data with only base image URL."""
        # Mock data with only base image URL (using 'id' field as per API)
        mock_data = {"id": 25, POKEMON_ASSETS_KEY: {POKEMON_IMAGE_KEY: "https://example.com/pikachu.png"}}

        # Mock the frame and image fetching
        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            self.pokedex_view._on_pokemon_data_success(mock_data)

            # Verify base image fetching was called (pokemon name will be "25" from id field)
            mock_fetch_base.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_IMAGE_KEY], pokemon_name="25"
            )
            # Verify shiny image fetching was NOT called
            mock_fetch_shiny.assert_not_called()

    def test_on_pokemon_data_success_without_images(self) -> None:
        """Test handling successful Pokemon data without image URLs."""
        # Mock data without image URLs
        mock_data = {"name": "Pikachu"}

        # Mock the frame
        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            self.pokedex_view._on_pokemon_data_success(mock_data)

            # Verify neither image fetching was called
            mock_fetch_base.assert_not_called()
            mock_fetch_shiny.assert_not_called()

    def test_on_pokemon_data_success_with_missing_id(self) -> None:
        """Test handling successful Pokemon data without id field."""
        # Mock data without id field
        mock_data = {POKEMON_ASSETS_KEY: {POKEMON_IMAGE_KEY: "https://example.com/image.png"}}

        # Mock the frame
        self.pokedex_view.frame = Mock()
        with patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base:
            self.pokedex_view._on_pokemon_data_success(mock_data)

            # Verify base image fetching was called with "Unknown" as name
            mock_fetch_base.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_IMAGE_KEY], pokemon_name="Unknown"
            )

    def test_on_pokemon_data_success_with_empty_data(self) -> None:
        """Test handling empty Pokemon data dictionary."""
        # Mock empty data
        mock_data = {}

        # Mock the frame
        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            # This should not raise any exceptions
            self.pokedex_view._on_pokemon_data_success(mock_data)

            # Verify no image fetching was called
            mock_fetch_base.assert_not_called()
            mock_fetch_shiny.assert_not_called()

    def test_display_pokemon_base_image_with_processed_image(self) -> None:
        """Test displaying a processed base image in the UI."""
        # Create a mock ProcessedImage
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"

        # Mock the base image label
        self.pokedex_view.base_image_label = Mock()

        # Call the method
        self.pokedex_view._display_pokemon_base_image(image=mock_processed_image, pokemon_name=pokemon_name)

        # Verify the image label was configured correctly
        self.pokedex_view.base_image_label.config.assert_called_once_with(image=mock_processed_image, text="")
        # Verify the reference was set to prevent garbage collection
        self.assertEqual(self.pokedex_view.base_image_label.image, mock_processed_image)
        # Verify the navigator was updated
        self.mock_navigator.update_status.assert_called_once_with(message="Base image loaded for Pikachu!")

    def test_display_pokemon_shiny_image_with_processed_image(self) -> None:
        """Test displaying a processed shiny image in the UI."""
        # Create a mock ProcessedImage
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"

        # Mock the shiny image label
        self.pokedex_view.shiny_image_label = Mock()

        # Call the method
        self.pokedex_view._display_pokemon_shiny_image(image=mock_processed_image, pokemon_name=pokemon_name)

        # Verify the image label was configured correctly
        self.pokedex_view.shiny_image_label.config.assert_called_once_with(image=mock_processed_image, text="")
        # Verify the reference was set to prevent garbage collection
        self.assertEqual(self.pokedex_view.shiny_image_label.image, mock_processed_image)
        # Verify the navigator was updated
        self.mock_navigator.update_status.assert_called_once_with(message="Shiny image loaded for Pikachu!")

    def test_on_base_image_success_callback(self) -> None:
        """Test the base image success callback from the image service."""
        # Create a mock ProcessedImage
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"

        # Set up the stored pokemon name
        self.pokedex_view._current_pokemon_name = pokemon_name

        # Mock the frame
        self.pokedex_view.frame = Mock()

        # Mock the display method
        with patch.object(self.pokedex_view, "_display_pokemon_base_image") as mock_display:
            # The callback signature only takes the processed image
            self.pokedex_view._on_base_image_success(mock_processed_image)

            # Verify frame.after was called to schedule UI update
            self.pokedex_view.frame.after.assert_called_once()
            # The lambda should call _display_pokemon_base_image when executed
            lambda_func = self.pokedex_view.frame.after.call_args[0][1]
            lambda_func()
            mock_display.assert_called_once_with(image=mock_processed_image, pokemon_name=pokemon_name)

    def test_on_shiny_image_success_callback(self) -> None:
        """Test the shiny image success callback from the image service."""
        # Create a mock ProcessedImage
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"

        # Set up the stored pokemon name
        self.pokedex_view._current_pokemon_name = pokemon_name

        # Mock the frame
        self.pokedex_view.frame = Mock()

        # Mock the display method
        with patch.object(self.pokedex_view, "_display_pokemon_shiny_image") as mock_display:
            # The callback signature only takes the processed image
            self.pokedex_view._on_shiny_image_success(mock_processed_image)

            # Verify frame.after was called to schedule UI update
            self.pokedex_view.frame.after.assert_called_once()
            # The lambda should call _display_pokemon_shiny_image when executed
            lambda_func = self.pokedex_view.frame.after.call_args[0][1]
            lambda_func()
            mock_display.assert_called_once_with(image=mock_processed_image, pokemon_name=pokemon_name)

    def test_clear_images(self) -> None:
        """Test clearing both image displays."""
        # Mock both image labels
        self.pokedex_view.base_image_label = Mock()
        self.pokedex_view.shiny_image_label = Mock()

        # Call the method
        self.pokedex_view._clear_images()

        # Verify both image labels were cleared
        self.pokedex_view.base_image_label.config.assert_called_once_with(image="", text="No image loaded.")
        self.pokedex_view.shiny_image_label.config.assert_called_once_with(image="", text="No image loaded.")

    def test_cancel_current_image_searches(self) -> None:
        """Test canceling current image searches."""
        # Mock threads as alive
        self.pokedex_view._current_base_image_thread = Mock()
        self.pokedex_view._current_base_image_thread.is_alive.return_value = True
        self.pokedex_view._current_shiny_image_thread = Mock()
        self.pokedex_view._current_shiny_image_thread.is_alive.return_value = True

        # Call the method
        self.pokedex_view._cancel_current_image_searches()

        # Verify both cancellation flags were set
        self.assertTrue(self.pokedex_view._base_image_search_cancelled)
        self.assertTrue(self.pokedex_view._shiny_image_search_cancelled)


if __name__ == "__main__":
    unittest.main()
