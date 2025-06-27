"""Main menu view for the application."""

import tkinter as tk
from typing import Final

from src.application.views.base_view import BaseView, ViewNavigator


class MainMenuView(BaseView):
    """Main menu view with navigation options."""

    # UI Configuration constants
    TITLE_TEXT: Final[str] = "Pokémon Go Max Mechanics"
    TITLE_FONT: Final[tuple[str, int, str]] = ("Arial", 24, "bold")
    TITLE_COLOR: Final[str] = "#1f4e79"

    SUBTITLE_TEXT: Final[str] = "Choose an option to explore:"
    SUBTITLE_FONT: Final[tuple[str, int]] = ("Arial", 14)
    SUBTITLE_COLOR: Final[str] = "#666666"

    BUTTON_FONT: Final[tuple[str, int, str]] = ("Arial", 12, "bold")
    BUTTON_WIDTH: Final[int] = 20
    BUTTON_HEIGHT: Final[int] = 2

    def __init__(self, *, parent: tk.Widget, navigator: ViewNavigator) -> None:
        """Initialize the main menu view.

        Args:
            parent: The parent widget.
            navigator: The view navigator for navigation and status updates.
        """
        super().__init__(parent=parent, navigator=navigator)

    def create_widgets(self) -> None:
        """Create and layout the main menu widgets."""
        if not self.frame:
            return

        # Title
        title_label = tk.Label(self.frame, text=self.TITLE_TEXT, font=self.TITLE_FONT, fg=self.TITLE_COLOR, bg="white")
        title_label.pack(pady=(40, 20))

        # Subtitle
        subtitle_label = tk.Label(
            self.frame, text=self.SUBTITLE_TEXT, font=self.SUBTITLE_FONT, fg=self.SUBTITLE_COLOR, bg="white"
        )
        subtitle_label.pack(pady=(0, 40))

        # Menu buttons container
        buttons_frame = tk.Frame(self.frame, bg="white")
        buttons_frame.pack(expand=True)

        # Pokédex button
        pokedex_button = tk.Button(
            buttons_frame,
            text="📚 Pokédex",
            font=self.BUTTON_FONT,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#4CAF50",
            fg="white",
            relief="raised",
            command=self._on_pokedex_click,
        )
        pokedex_button.pack(pady=10)

        # Future buttons can be added here
        # Team Builder button (disabled for now)
        team_builder_button = tk.Button(
            buttons_frame,
            text="👥 Team Builder",
            font=self.BUTTON_FONT,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#CCCCCC",
            fg="#666666",
            relief="raised",
            state="disabled",
        )
        team_builder_button.pack(pady=10)

        # Max Mechanics button (disabled for now)
        max_mechanics_button = tk.Button(
            buttons_frame,
            text="⚡ Max Mechanics",
            font=self.BUTTON_FONT,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#CCCCCC",
            fg="#666666",
            relief="raised",
            state="disabled",
        )
        max_mechanics_button.pack(pady=10)

    def _on_pokedex_click(self) -> None:
        """Handle Pokédex button click."""
        self.navigator.update_status(message="Opening Pokédex...")
        self.navigator.navigate_to(view_name="pokedex")

    def on_show(self) -> None:
        """Called when the main menu is shown."""
        self.navigator.update_status(message="Welcome! Select an option from the menu.")
