"""Main application controller for the Pokémon Go Max Mechanics GUI."""

import tkinter as tk
from tkinter import BOTH, BOTTOM, LEFT, SUNKEN, X
from tkinter.ttk import Frame
from typing import Final

from src.application.constants.ui_constants import (
    DEFAULT_BACKGROUND_COLOR,
    STATUS_BAR_FONT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.application.constants.view_constants import (
    MAIN_MENU_VIEW,
    POKEDEX_VIEW,
    STATUS_LABEL,
)
from src.application.views.base_view import BaseView, ViewNavigator
from src.application.views.main_menu_view import MainMenuView
from src.application.views.pokedex_view import PokedexView
from src.infrastructure.dependency_injection.setup import injector


class PokemonGoApp(ViewNavigator):
    """Main application controller that manages views and navigation."""

    # Window configuration constants.
    WINDOW_TITLE: Final[str] = "Pokémon Go Max Mechanics"
    MESSAGE_APPLICATION_READY: Final[str] = "Application ready"
    MESSAGE_APPLICATION_STARTED: Final[str] = "Application started. Welcome!"

    def __init__(self) -> None:
        """Initialize the Pokémon Go application."""
        self.root = tk.Tk()

        # View management (initialize before setup).
        self.main_container: Frame | None = None
        self.current_view: BaseView | None = None
        self.views: dict[str, BaseView] = {}

        # Setup window and UI.
        self._setup_window()
        self._create_status_bar()
        self._setup_views()
        self._navigate_to_initial_view()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(width=True, height=True)
        self.root.configure(bg=DEFAULT_BACKGROUND_COLOR)

        # Center the window on screen.
        self._center_window()

    def _center_window(self) -> None:
        """Center the window on the screen."""
        screen_width: int = self.root.winfo_screenwidth()
        screen_height: int = self.root.winfo_screenheight()
        x: int = (screen_width - WINDOW_WIDTH) // 2
        y: int = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _create_status_bar(self) -> None:
        """Create a status bar at the bottom of the window."""
        # Using tk.Frame for status bar since it needs relief and bd styling.
        status_frame = tk.Frame(self.root, relief=SUNKEN, bd=1)
        status_frame.pack(side=BOTTOM, fill=X)
        # Using tk.Label for status since it needs anchor and font styling.
        self.status_label = tk.Label(
            status_frame, text=self.MESSAGE_APPLICATION_READY, anchor="w", font=STATUS_BAR_FONT, padx=10
        )
        self.status_label.pack(side=LEFT)
        # Create main container for views AFTER status bar.
        self.main_container = Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True)

    def _setup_views(self) -> None:
        """Initialize all application views."""
        if not self.main_container:
            return
        self.views[MAIN_MENU_VIEW] = MainMenuView(parent=self.main_container, navigator=self)
        self.views[POKEDEX_VIEW] = injector.create_object(
            PokedexView, additional_kwargs={"parent": self.main_container, "navigator": self}
        )

    def _navigate_to_initial_view(self) -> None:
        """Navigate to the initial view."""
        self.navigate_to(view_name=MAIN_MENU_VIEW)

    # ViewNavigator implementation.
    def navigate_to(self, *, view_name: str) -> None:
        """Navigate to a specific view.

        Args:
            view_name: The name of the view to navigate to.
        """
        if view_name not in self.views:
            self.update_status(message=f"Error: View '{view_name}' not found.")
            return
        if self.current_view:
            self.current_view.hide()
        new_view = self.views[view_name]
        new_view.show()
        self.current_view = new_view

    def update_status(self, *, message: str) -> None:
        """Update the status bar message.

        Args:
            message: The status message to display.
        """
        if hasattr(self, STATUS_LABEL):
            self.status_label.config(text=message)

    def run(self) -> None:
        """Start the application main loop."""
        self.update_status(message=self.MESSAGE_APPLICATION_STARTED)
        self.root.mainloop()

    def cleanup(self) -> None:
        """Clean up resources when the application is closing."""
        # Destroy all views.
        for view in self.views.values():
            view.destroy()

        self.views.clear()
        self.current_view = None
