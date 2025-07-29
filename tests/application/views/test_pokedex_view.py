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
        return Mock(spec=WebImageProcessingService)

    def create_mock_fetch_pokemon_use_case(self) -> Mock:
        return Mock(spec=FetchPokemonUseCase)

    def setUp(self) -> None:
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
        """Test that the view initializes correctly."""
        self.assertIs(self.pokedex_view.image_service, self.mock_image_service)
        self.assertIs(self.pokedex_view.fetch_pokemon_use_case, self.mock_fetch_pokemon_use_case)
        self.assertIsNone(self.pokedex_view._current_search_thread)
        self.assertIsNone(self.pokedex_view._current_base_image_thread)
        self.assertIsNone(self.pokedex_view._current_shiny_image_thread)
        self.assertFalse(self.pokedex_view._search_cancelled)
        self.assertFalse(self.pokedex_view._base_image_search_cancelled)
        self.assertFalse(self.pokedex_view._shiny_image_search_cancelled)

    def test_fetch_pokemon_base_image_with_valid_data(self) -> None:
        """Test fetching Pokemon base image with valid data containing image URL."""
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
        """Test handling successful Pokemon data with only base image URL."""
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
        """Test handling successful Pokemon data without image URLs."""
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
        """Test handling successful Pokemon data without id field."""
        mock_data = {POKEMON_ASSETS_KEY: {POKEMON_IMAGE_KEY: "https://example.com/image.png"}}

        self.pokedex_view.frame = Mock()
        with patch.object(self.pokedex_view, "_fetch_pokemon_base_image") as mock_fetch_base:
            self.pokedex_view._on_pokemon_data_success(mock_data)

            mock_fetch_base.assert_called_once_with(
                image_url=mock_data[POKEMON_ASSETS_KEY][POKEMON_IMAGE_KEY], pokemon_name="Unknown"
            )

    def test_on_pokemon_data_success_with_empty_data(self) -> None:
        """Test handling empty Pokemon data dictionary."""
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
        """Test displaying a processed base image in the UI."""
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"
        self.pokedex_view.base_image_label = Mock()

        self.pokedex_view._display_pokemon_base_image(image=mock_processed_image, pokemon_name=pokemon_name)

        self.pokedex_view.base_image_label.config.assert_called_once_with(image=mock_processed_image, text="")
        self.assertEqual(self.pokedex_view.base_image_label.image, mock_processed_image)
        self.mock_navigator.update_status.assert_called_once_with(message="Base image loaded for Pikachu!")

    def test_display_pokemon_shiny_image_with_processed_image(self) -> None:
        """Test displaying a processed shiny image in the UI."""
        mock_processed_image = Mock(spec=ProcessedImage)
        pokemon_name = "Pikachu"

        self.pokedex_view.shiny_image_label = Mock()

        self.pokedex_view._display_pokemon_shiny_image(image=mock_processed_image, pokemon_name=pokemon_name)

        self.pokedex_view.shiny_image_label.config.assert_called_once_with(image=mock_processed_image, text="")
        self.assertEqual(self.pokedex_view.shiny_image_label.image, mock_processed_image)
        self.mock_navigator.update_status.assert_called_once_with(message="Shiny image loaded for Pikachu!")

    def test_on_base_image_success_callback(self) -> None:
        """Test the base image success callback from the image service."""
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
        """Test the shiny image success callback from the image service."""
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
        self.pokedex_view.base_image_label = Mock()
        self.pokedex_view.shiny_image_label = Mock()

        self.pokedex_view._clear_images()

        self.pokedex_view.base_image_label.config.assert_called_once_with(image="", text="No image loaded.")
        self.pokedex_view.shiny_image_label.config.assert_called_once_with(image="", text="No image loaded.")

    def test_cancel_current_image_searches(self) -> None:
        self.pokedex_view._current_base_image_thread = Mock()
        self.pokedex_view._current_base_image_thread.is_alive.return_value = True
        self.pokedex_view._current_shiny_image_thread = Mock()
        self.pokedex_view._current_shiny_image_thread.is_alive.return_value = True

        self.pokedex_view._cancel_current_image_searches()

        self.assertTrue(self.pokedex_view._base_image_search_cancelled)
        self.assertTrue(self.pokedex_view._shiny_image_search_cancelled)
