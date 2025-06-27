"""Tests for the main application controller."""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch, MagicMock, call

from src.application.app import PokemonGoApp


class TestPokemonGoApp(unittest.TestCase):
    """Test cases for PokemonGoApp class."""

    @patch("src.application.app.injector")
    @patch("tkinter.Label")
    @patch("tkinter.Frame")
    @patch("tkinter.Tk")
    def setUp(self, mock_tk_class, mock_frame_class, mock_label_class, mock_injector) -> None:
        """Set up test fixtures."""
        # Mock the root window
        self.mock_root = MagicMock()
        self.mock_root.winfo_screenwidth.return_value = 1920
        self.mock_root.winfo_screenheight.return_value = 1080
        mock_tk_class.return_value = self.mock_root

        # Mock Frame class
        self.mock_frame = MagicMock()
        mock_frame_class.return_value = self.mock_frame

        # Mock Label class
        self.mock_label = MagicMock()
        mock_label_class.return_value = self.mock_label

        # Mock the injector
        mock_http_client = Mock()
        mock_injector.get.return_value = mock_http_client

        # Create the app
        self.app = PokemonGoApp()
        self.app.status_label = self.mock_label

    def test_initialization(self) -> None:
        """Test application initialization."""
        # Verify window setup was called
        self.mock_root.title.assert_called_with("Pokémon Go Max Mechanics")
        # Check that geometry was called with the window size and position
        geometry_calls = self.mock_root.geometry.call_args_list
        self.assertTrue(any("900x700" in str(call) for call in geometry_calls))
        self.mock_root.resizable.assert_called_with(width=True, height=True)
        self.mock_root.configure.assert_called_with(bg="white")

    def test_navigate_to_valid_view(self) -> None:
        """Test navigation to a valid view."""
        # Mock views
        mock_old_view = Mock()
        mock_new_view = Mock()

        self.app.views = {"old_view": mock_old_view, "new_view": mock_new_view}
        self.app.current_view = mock_old_view

        # Navigate to new view
        self.app.navigate_to(view_name="new_view")

        # Verify old view was hidden and new view was shown
        mock_old_view.hide.assert_called_once()
        mock_new_view.show.assert_called_once()
        self.assertEqual(self.app.current_view, mock_new_view)

    def test_navigate_to_invalid_view(self) -> None:
        """Test navigation to an invalid view."""
        self.app.views = {}

        # Navigate to invalid view
        self.app.navigate_to(view_name="nonexistent_view")

        # Verify error status was set
        self.mock_label.config.assert_called_with(text="Error: View 'nonexistent_view' not found.")

    def test_update_status_with_label(self) -> None:
        """Test status update when status label exists."""
        self.app.update_status(message="Test message")

        self.mock_label.config.assert_called_with(text="Test message")

    def test_cleanup_destroys_views(self) -> None:
        """Test that cleanup destroys all views."""
        mock_view1 = Mock()
        mock_view2 = Mock()

        self.app.views = {"view1": mock_view1, "view2": mock_view2}
        self.app.current_view = mock_view1

        self.app.cleanup()

        # Verify all views were destroyed
        mock_view1.destroy.assert_called_once()
        mock_view2.destroy.assert_called_once()

        # Verify state was reset
        self.assertEqual(self.app.views, {})
        self.assertIsNone(self.app.current_view)
