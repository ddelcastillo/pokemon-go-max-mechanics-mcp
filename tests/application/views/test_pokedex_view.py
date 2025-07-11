"""Tests for the Pokedex view."""

import unittest
from typing import Any, Callable
from unittest.mock import Mock, patch

from src.application.services.web_image_processing import WebImageProcessingService
from src.application.use_cases.fetch_pokemon_use_case import FetchPokemonUseCase
from src.application.views.pokedex_view import PokedexView
from src.domain.interfaces.image_processor import ProcessedImage
from src.infrastructure.constants.api_constants import (
    POKEMON_ASSETS_KEY,
    POKEMON_IMAGE_KEY,
    POKEMON_SHINY_IMAGE_KEY,
)


class TestPokedexView(unittest.TestCase):
    """Test cases for PokedexView."""

    def create_mock_image_service(self) -> Mock:
        """
        Create and return a mock instance of the WebImageProcessingService for use in tests.
        
        Returns:
            Mock: A mock object adhering to the WebImageProcessingService interface.
        """
        return Mock(spec=WebImageProcessingService)

    def create_mock_fetch_pokemon_use_case(self) -> Mock:
        """
        Create and return a mock instance of the FetchPokemonUseCase for testing purposes.
        
        Returns:
            Mock: A mock object adhering to the FetchPokemonUseCase interface.
        """
        return Mock(spec=FetchPokemonUseCase)

    def setUp(self) -> None:
        """
        Set up the test environment by initializing mocks and creating a PokedexView instance with mocked dependencies.
        """
        self.mock_parent = Mock()
        self.mock_navigator = Mock()
        self.mock_image_service = self.create_mock_image_service()
        self.mock_fetch_pokemon_use_case = self.create_mock_fetch_pokemon_use_case()

        self.pokedex_view = PokedexView(
            parent=self.mock_parent,
            navigator=self.mock_navigator,
            image_service=self.mock_image_service,
            fetch_pokemon_use_case=self.mock_fetch_pokemon_use_case,
        )

    def test_initialization(self) -> None:
        """
        Verify that the PokedexView instance is initialized with the correct dependencies and that its internal state flags and threads are set to their default values.
        """
        self.assertIs(self.pokedex_view.image_service, self.mock_image_service)
        self.assertIs(self.pokedex_view.fetch_pokemon_use_case, self.mock_fetch_pokemon_use_case)
        self.assertIsNone(self.pokedex_view._current_search_thread)
        self.assertIsNone(self.pokedex_view._current_base_image_thread)
        self.assertIsNone(self.pokedex_view._current_shiny_image_thread)
        self.assertFalse(self.pokedex_view._search_cancelled)
        self.assertFalse(self.pokedex_view._base_image_search_cancelled)
        self.assertFalse(self.pokedex_view._shiny_image_search_cancelled)

    def test_fetch_pokemon_base_image_with_valid_data(self) -> None:
        """
        Verifies that fetching a Pokémon's base image with a valid URL calls the image service with correct parameters and updates the current Pokémon name.
        """
        image_url = "https://example.com/pikachu.png"
        pokemon_name = "Pikachu"

        mock_thread = Mock()
        self.mock_image_service.fetch_image_async.return_value = mock_thread

        self.pokedex_view._fetch_pokemon_base_image(image_url=image_url, pokemon_name=pokemon_name)

        self.mock_image_service.fetch_image_async.assert_called_once()
        call_args = self.mock_image_service.fetch_image_async.call_args
        self.assertEqual(call_args.kwargs["image_url"], image_url)
        self.assertEqual(call_args.kwargs["on_success"], self.pokedex_view._on_base_image_success)
        self.assertEqual(call_args.kwargs["on_error"], self.pokedex_view._on_base_image_error)
        self.assertEqual(self.pokedex_view._current_pokemon_name, pokemon_name)

    def test_fetch_pokemon_shiny_image_with_valid_data(self) -> None:
        """
        Test that `_fetch_pokemon_shiny_image` calls the image service with the correct shiny image URL, callbacks, and updates the current Pokémon name.
        """
        image_url = "https://example.com/pikachu_shiny.png"
        pokemon_name = "Pikachu"

        mock_thread = Mock()
        self.mock_image_service.fetch_image_async.return_value = mock_thread

        self.pokedex_view._fetch_pokemon_shiny_image(image_url=image_url, pokemon_name=pokemon_name)

        self.mock_image_service.fetch_image_async.assert_called_once()
        call_args = self.mock_image_service.fetch_image_async.call_args
        self.assertEqual(call_args.kwargs["image_url"], image_url)
        self.assertEqual(call_args.kwargs["on_success"], self.pokedex_view._on_shiny_image_success)
        self.assertEqual(call_args.kwargs["on_error"], self.pokedex_view._on_shiny_image_error)
        self.assertEqual(self.pokedex_view._current_pokemon_name, pokemon_name)

    def test_on_pokemon_data_success_with_both_images(self) -> None:
        """
        Test that both base and shiny image fetch methods are called with correct URLs and Pokémon ID when both images are present in the data.
        """
        mock_data: dict[str, Any] = {
            "id": 25,
            POKEMON_ASSETS_KEY: {
                POKEMON_IMAGE_KEY: "https://example.com/pikachu.png",
                POKEMON_SHINY_IMAGE_KEY: "https://example.com/pikachu_shiny.png",
            },
        }

        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            self.pokedex_view._on_pokemon_data_success(mock_data)

            mock_fetch_base.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_IMAGE_KEY], pokemon_name="25"
            )
            mock_fetch_shiny.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_SHINY_IMAGE_KEY], pokemon_name="25"
            )

    def test_on_pokemon_data_success_with_base_image_only(self) -> None:
        """
        Test that only the base image is fetched when Pokémon data contains a base image URL but no shiny image URL.
        
        Verifies that `_fetch_pokemon_base_image` is called with the correct URL and Pokémon name, and `_fetch_pokemon_shiny_image` is not called.
        """
        mock_data: dict[str, Any] = {
            "id": 25,
            POKEMON_ASSETS_KEY: {POKEMON_IMAGE_KEY: "https://example.com/pikachu.png"},
        }

        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            self.pokedex_view._on_pokemon_data_success(mock_data)

            mock_fetch_base.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_IMAGE_KEY], pokemon_name="25"
            )
            mock_fetch_shiny.assert_not_called()

    def test_on_pokemon_data_success_without_images(self) -> None:
        """
        Test that no image fetch methods are called when Pokémon data lacks image URLs.
        """
        mock_data = {"name": "Pikachu"}

        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            self.pokedex_view._on_pokemon_data_success(mock_data)

            mock_fetch_base.assert_not_called()
            mock_fetch_shiny.assert_not_called()

    def test_on_pokemon_data_success_with_missing_id(self) -> None:
        """
        Test that `_on_pokemon_data_success` uses "Unknown" as the Pokémon name when the ID field is missing in the data.
        """
        mock_data = {POKEMON_ASSETS_KEY: {POKEMON_IMAGE_KEY: "https://example.com/image.png"}}

        self.pokedex_view.frame = Mock()
        with patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base:
            self.pokedex_view._on_pokemon_data_success(mock_data)

            mock_fetch_base.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_IMAGE_KEY], pokemon_name="Unknown"
            )

    def test_on_pokemon_data_success_with_empty_data(self) -> None:
        """
        Test that no image fetch methods are called when the Pokémon data dictionary is empty.
        """
        mock_data: dict[str, Any] = {}

        self.pokedex_view.frame = Mock()
        with (
            patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base,
            patch.object(self.pokedex_view, "_fetch_pokemon_shiny_image") as mock_fetch_shiny,
        ):
            self.pokedex_view._on_pokemon_data_success(mock_data)

            mock_fetch_base.assert_not_called()
            mock_fetch_shiny.assert_not_called()

    def test_display_pokemon_base_image_with_processed_image(self) -> None:
        """
        Verifies that the processed base image is displayed in the UI, the label is updated, and the navigator status reflects the loaded image.
        """
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"
        self.pokedex_view.base_image_label = Mock()

        self.pokedex_view._display_pokemon_base_image(image=mock_processed_image, pokemon_name=pokemon_name)

        self.pokedex_view.base_image_label.config.assert_called_once_with(image=mock_processed_image, text="")
        self.assertEqual(self.pokedex_view.base_image_label.image, mock_processed_image)
        self.mock_navigator.update_status.assert_called_once_with(message="Base image loaded for Pikachu!")

    def test_display_pokemon_shiny_image_with_processed_image(self) -> None:
        """
        Verifies that the shiny image label is updated with the processed shiny image and the navigator status is set appropriately when displaying a shiny Pokémon image.
        """
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"

        self.pokedex_view.shiny_image_label = Mock()

        self.pokedex_view._display_pokemon_shiny_image(image=mock_processed_image, pokemon_name=pokemon_name)

        self.pokedex_view.shiny_image_label.config.assert_called_once_with(image=mock_processed_image, text="")
        self.assertEqual(self.pokedex_view.shiny_image_label.image, mock_processed_image)
        self.mock_navigator.update_status.assert_called_once_with(message="Shiny image loaded for Pikachu!")

    def test_on_base_image_success_callback(self) -> None:
        """
        Test that the base image success callback schedules a UI update and displays the processed image with the correct Pokémon name.
        """
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"

        self.pokedex_view._current_pokemon_name = pokemon_name

        self.pokedex_view.frame = Mock()

        with patch.object(self.pokedex_view, "_display_pokemon_base_image") as mock_display:
            self.pokedex_view._on_base_image_success(mock_processed_image)
            self.pokedex_view.frame.after.assert_called_once()
            lambda_func: Callable[[], None] = self.pokedex_view.frame.after.call_args[0][1]  # type: ignore[index]
            lambda_func()
            mock_display.assert_called_once_with(image=mock_processed_image, pokemon_name=pokemon_name)

    def test_on_shiny_image_success_callback(self) -> None:
        """
        Test that the shiny image success callback schedules a UI update and displays the processed shiny image for the current Pokémon.
        """
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"
        self.pokedex_view._current_pokemon_name = pokemon_name
        self.pokedex_view.frame = Mock()
        with patch.object(self.pokedex_view, "_display_pokemon_shiny_image") as mock_display:
            self.pokedex_view._on_shiny_image_success(mock_processed_image)
            self.pokedex_view.frame.after.assert_called_once()
            lambda_func: Callable[[], None] = self.pokedex_view.frame.after.call_args[0][1]  # type: ignore[index]
            lambda_func()
            mock_display.assert_called_once_with(image=mock_processed_image, pokemon_name=pokemon_name)

    def test_clear_images(self) -> None:
        """
        Test that the _clear_images method resets both base and shiny image labels to show no image loaded.
        """
        self.pokedex_view.base_image_label = Mock()
        self.pokedex_view.shiny_image_label = Mock()

        self.pokedex_view._clear_images()

        self.pokedex_view.base_image_label.config.assert_called_once_with(image="", text="No image loaded.")
        self.pokedex_view.shiny_image_label.config.assert_called_once_with(image="", text="No image loaded.")

    def test_cancel_current_image_searches(self) -> None:
        """
        Test that image search cancellation flags are set when current image fetch threads are active.
        """
        self.pokedex_view._current_base_image_thread = Mock()
        self.pokedex_view._current_base_image_thread.is_alive.return_value = True
        self.pokedex_view._current_shiny_image_thread = Mock()
        self.pokedex_view._current_shiny_image_thread.is_alive.return_value = True

        self.pokedex_view._cancel_current_image_searches()

        self.assertTrue(self.pokedex_view._base_image_search_cancelled)
        self.assertTrue(self.pokedex_view._shiny_image_search_cancelled)


if __name__ == "__main__":
    unittest.main()
