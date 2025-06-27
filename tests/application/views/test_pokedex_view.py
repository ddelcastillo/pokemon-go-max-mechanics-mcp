"""Tests for the Pokédex view with image search functionality."""

import tkinter as tk
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.application.views.pokedex_view import PokedexView
from src.domain.ports.outbound.http_client_port import HttpClientPort


class TestPokedexView:
    """Test cases for the Pokédex view."""

    @pytest.fixture
    def mock_http_client(self) -> Mock:
        """Create a mock HTTP client."""
        mock_client = Mock(spec=HttpClientPort)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        return mock_client

    @pytest.fixture
    def mock_navigator(self) -> Mock:
        """Create a mock navigator."""
        navigator = Mock()
        navigator.navigate_to = Mock()
        navigator.update_status = Mock()
        return navigator

    @pytest.fixture
    def root_window(self) -> tk.Tk:
        """Create a root window for testing."""
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        yield root
        root.destroy()

    @pytest.fixture
    def pokedex_view(self, root_window: tk.Tk, mock_navigator: Mock, mock_http_client: Mock) -> PokedexView:
        """Create a Pokédex view instance for testing."""
        return PokedexView(parent=root_window, navigator=mock_navigator, http_client=mock_http_client)

    def test_init_creates_view_with_image_components(
        self, root_window: tk.Tk, mock_navigator: Mock, mock_http_client: Mock
    ) -> None:
        """Test that the view initializes with image search components."""
        view = PokedexView(parent=root_window, navigator=mock_navigator, http_client=mock_http_client)

        assert view.http_client is mock_http_client
        assert view.navigator is mock_navigator
        assert view._image_search_cancelled is False
        assert view._current_image_thread is None
        assert view.image_search_button is None  # Not created until show()

    def test_create_widgets_includes_image_search_button(self, pokedex_view: PokedexView) -> None:
        """Test that create_widgets includes the image search button."""
        pokedex_view.show()

        assert pokedex_view.image_search_button is not None
        assert pokedex_view.image_label is not None
        assert pokedex_view.image_search_button.cget("text") == "🖼️ Search with Image"
        assert pokedex_view.image_search_button.cget("bg") == "#4CAF50"

    def test_image_search_button_disabled_when_no_input(self, pokedex_view: PokedexView) -> None:
        """Test that image search shows error when no Pokemon name is entered."""
        pokedex_view.show()

        with patch.object(pokedex_view, "_show_error") as mock_show_error:
            pokedex_view._on_image_search_click()
            mock_show_error.assert_called_once_with("Please enter a Pokémon name.")

    @patch("src.application.views.pokedex_view.threading.Thread")
    def test_image_search_starts_threads(self, mock_thread: Mock, pokedex_view: PokedexView) -> None:
        """Test that image search starts both data and image threads."""
        pokedex_view.show()
        if pokedex_view.search_entry:
            pokedex_view.search_entry.insert(0, "pikachu")

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        pokedex_view._on_image_search_click()

        # Should create two threads: one for data, one for image
        assert mock_thread.call_count == 2
        assert mock_thread_instance.start.call_count == 2

    def test_cancel_image_search_sets_flag(self, pokedex_view: PokedexView) -> None:
        """Test that canceling image search sets the appropriate flag."""
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        pokedex_view._current_image_thread = mock_thread

        pokedex_view._cancel_current_image_search()

        assert pokedex_view._image_search_cancelled is True

    def test_image_searching_state_disables_button(self, pokedex_view: PokedexView) -> None:
        """Test that image searching state properly disables the button."""
        pokedex_view.show()

        # Test searching state
        pokedex_view._set_image_searching_state(searching=True)
        assert pokedex_view.image_search_button.cget("state") == "disabled"
        assert pokedex_view.image_search_button.cget("text") == "🔄 Loading Image..."

        # Test normal state
        pokedex_view._set_image_searching_state(searching=False)
        assert pokedex_view.image_search_button.cget("state") == "normal"
        assert pokedex_view.image_search_button.cget("text") == "🖼️ Search with Image"

    def test_show_image_error_updates_label(self, pokedex_view: PokedexView) -> None:
        """Test that image errors are properly displayed."""
        pokedex_view.show()

        error_message = "Network error"
        pokedex_view._show_image_error(error_message)

        expected_text = f"Image Error:\n{error_message}"
        assert pokedex_view.image_label.cget("text") == expected_text

    @patch("src.application.views.pokedex_view.ImageTk.PhotoImage")
    def test_display_pokemon_image_updates_label(self, mock_photo_image: Mock, pokedex_view: PokedexView) -> None:
        """Test that displaying a Pokemon image updates the label properly."""
        pokedex_view.show()

        mock_image = Mock()
        pokemon_name = "pikachu"

        pokedex_view._display_pokemon_image(image=mock_image, pokemon_name=pokemon_name)

        assert pokedex_view.image_label.cget("image") == str(mock_image)
        assert pokedex_view.image_label.cget("text") == ""
        assert hasattr(pokedex_view.image_label, "image")

    def test_on_destroy_cancels_image_search(self, pokedex_view: PokedexView) -> None:
        """Test that destroying the view cancels image search."""
        with patch.object(pokedex_view, "_cancel_current_image_search") as mock_cancel:
            pokedex_view.on_destroy()
            mock_cancel.assert_called_once()

    def test_on_back_click_cancels_image_search(self, pokedex_view: PokedexView) -> None:
        """Test that going back cancels image search."""
        with patch.object(pokedex_view, "_cancel_current_image_search") as mock_cancel:
            pokedex_view._on_back_click()
            mock_cancel.assert_called_once()
