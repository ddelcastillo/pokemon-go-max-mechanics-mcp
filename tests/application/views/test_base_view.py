"""Tests for the base view functionality."""

import tkinter as tk
import unittest
from tkinter.ttk import Widget
from unittest.mock import Mock

from src.application.views.base_view import BaseView, ViewNavigator


class MockTestView(BaseView):
    """Test implementation of BaseView."""

    def __init__(self, *, parent: Widget, navigator: ViewNavigator) -> None:
        """Initialize test view."""
        super().__init__(parent=parent, navigator=navigator)
        self.widgets_created = False

    def create_widgets(self) -> None:
        """Create test widgets."""
        if self.frame:
            test_label = tk.Label(self.frame, text="Test View")
            test_label.pack()
            self.widgets_created = True


class TestBaseView(unittest.TestCase):
    """Test cases for BaseView class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        # Create a ttk Frame as the parent to match the expected Widget type
        from tkinter.ttk import Frame

        self.parent_frame = Frame(self.root)
        self.navigator = Mock(spec=ViewNavigator)
        self.view = MockTestView(parent=self.parent_frame, navigator=self.navigator)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        self.view.destroy()
        self.root.destroy()

    def test_initialization(self) -> None:
        """Test view initialization."""
        self.assertEqual(self.view.parent, self.parent_frame)
        self.assertEqual(self.view.navigator, self.navigator)
        self.assertIsNone(self.view.frame)

    def test_show_creates_frame_and_widgets(self) -> None:
        """Test that show() creates frame and widgets."""
        self.assertIsNone(self.view.frame)
        self.assertFalse(self.view.widgets_created)

        self.view.show()

        self.assertIsNotNone(self.view.frame)
        self.assertTrue(self.view.widgets_created)

    def test_show_only_creates_widgets_once(self) -> None:
        """Test that show() only creates widgets once."""
        self.view.show()
        first_frame = self.view.frame

        # Reset the flag
        self.view.widgets_created = False

        self.view.show()

        # Should be the same frame
        self.assertEqual(self.view.frame, first_frame)
        # Widgets should not be created again
        self.assertFalse(self.view.widgets_created)

    def test_hide_removes_frame_from_display(self) -> None:
        """Test that hide() removes frame from display."""
        self.view.show()

        # Mock the pack_forget method to track calls
        pack_forget_mock = Mock()
        if self.view.frame:
            self.view.frame.pack_forget = pack_forget_mock  # type: ignore[method-assign]

        self.view.hide()

        pack_forget_mock.assert_called_once()

    def test_destroy_removes_frame(self) -> None:
        """Test that destroy() removes the frame."""
        self.view.show()
        self.assertIsNotNone(self.view.frame)

        self.view.destroy()

        self.assertIsNone(self.view.frame)

    def test_lifecycle_callbacks(self) -> None:
        """Test that lifecycle callbacks are called."""
        # Mock the callback methods
        self.view.on_show = Mock()  # type: ignore[method-assign]
        self.view.on_hide = Mock()  # type: ignore[method-assign]
        self.view.on_destroy = Mock()  # type: ignore[method-assign]

        # Test show callback
        self.view.show()
        self.view.on_show.assert_called_once()

        # Test hide callback
        self.view.hide()
        self.view.on_hide.assert_called_once()

        # Test destroy callback
        self.view.destroy()
        self.view.on_destroy.assert_called_once()
