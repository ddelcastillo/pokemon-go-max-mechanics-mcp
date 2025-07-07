"""Main menu view for the application."""

from tkinter.ttk import Button, Frame, Label, Widget
from typing import Final

from src.application.constants.ui_constants import BUTTON_WIDTH, TITLE_FONT
from src.application.constants.view_constants import POKEDEX_VIEW
from src.application.views.base_view import BaseView, ViewNavigator


class MainMenuView(BaseView):
    """Main menu view with navigation options."""

    # Application-specific text constants
    TITLE_TEXT: Final[str] = "Max Mechanics"
    SUBTITLE_TEXT: Final[str] = "Choose an option to explore:"

    POKEDEX_BUTTON_TEXT: Final[str] = "📚 Pokédex API"
    TEAM_BUILDER_BUTTON_TEXT: Final[str] = "👥 G-Max Tank Analysis"
    MAX_MECHANICS_BUTTON_TEXT: Final[str] = "⚡ G-Max Best Attacker"

    def __init__(self, *, parent: Widget, navigator: ViewNavigator) -> None:
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
        title_label = Label(self.frame, text=self.TITLE_TEXT, font=TITLE_FONT)
        title_label.pack(pady=(40, 20))

        # Subtitle
        subtitle_label = Label(self.frame, text=self.SUBTITLE_TEXT)
        subtitle_label.pack(pady=(0, 40))

        # Menu buttons container
        buttons_frame = Frame(self.frame)
        buttons_frame.pack(expand=True)

        # Team Builder button (disabled for now)
        team_builder_button = Button(
            buttons_frame, text=self.TEAM_BUILDER_BUTTON_TEXT, width=BUTTON_WIDTH, state="disabled"
        )
        team_builder_button.pack(pady=10)

        # Max Mechanics button (disabled for now)
        max_mechanics_button = Button(
            buttons_frame, text=self.MAX_MECHANICS_BUTTON_TEXT, width=BUTTON_WIDTH, state="disabled"
        )
        max_mechanics_button.pack(pady=10)
        # Pokédex button
        pokedex_button = Button(
            buttons_frame, text=self.POKEDEX_BUTTON_TEXT, width=BUTTON_WIDTH, command=self._on_pokedex_click
        )
        pokedex_button.pack(pady=10)

    def _on_pokedex_click(self) -> None:
        """Handle Pokédex button click."""
        self.navigator.update_status(message="Opening Pokédex...")
        self.navigator.navigate_to(view_name=POKEDEX_VIEW)

    def on_show(self) -> None:
        """Called when the main menu is shown."""
        self.navigator.update_status(message="Welcome! Select an option from the menu.")
