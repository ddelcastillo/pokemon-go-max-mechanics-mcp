"""Main application controller for the Pokémon Go Max Mechanics GUI."""

import tkinter as tk
from typing import Final

from src.application.views.base_view import BaseView, ViewNavigator
from src.application.views.main_menu_view import MainMenuView
from src.application.views.pokedex_view import PokedexView
from src.domain.ports.outbound.http_client_port import HttpClientPort
from src.infrastructure.dependency_injection.setup import injector


class PokemonGoApp(ViewNavigator):
    """Main application controller that manages views and navigation."""

    # Window configuration constants
    WINDOW_WIDTH: Final[int] = 900
    WINDOW_HEIGHT: Final[int] = 700
    WINDOW_TITLE: Final[str] = "Pokémon Go Max Mechanics"

    def __init__(self) -> None:
        """Initialize the Pokémon Go application."""
        self.root = tk.Tk()

        # View management (initialize before setup)
        self.main_container: tk.Frame | None = None
        self.current_view: BaseView | None = None
        self.views: dict[str, BaseView] = {}

        # Setup window and UI
        self._setup_window()
        self._create_status_bar()
        self._setup_views()
        self._navigate_to_initial_view()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.resizable(width=True, height=True)
        self.root.configure(bg="white")

        # Center the window on screen
        self._center_window()

    def _center_window(self) -> None:
        """Center the window on the screen."""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position
        x = (screen_width - self.WINDOW_WIDTH) // 2
        y = (screen_height - self.WINDOW_HEIGHT) // 2

        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")

    def _create_status_bar(self) -> None:
        """Create a status bar at the bottom of the window."""
        status_frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(status_frame, text="Application ready", anchor=tk.W, font=("Arial", 9), padx=10)
        self.status_label.pack(side=tk.LEFT)

        # Create main container for views AFTER status bar
        self.main_container = tk.Frame(self.root, bg="white")
        self.main_container.pack(fill=tk.BOTH, expand=True)

    def _setup_views(self) -> None:
        """Initialize all application views."""
        if not self.main_container:
            return

        # Main menu view
        self.views["main_menu"] = MainMenuView(parent=self.main_container, navigator=self)

        # Pokédex view (created using dependency injection)
        # Get the HTTP client from the injector
        http_client = injector.get(HttpClientPort)  # type: ignore[type-abstract]
        self.views["pokedex"] = PokedexView(parent=self.main_container, navigator=self, http_client=http_client)

    def _navigate_to_initial_view(self) -> None:
        """Navigate to the initial view."""
        self.navigate_to(view_name="main_menu")

    # ViewNavigator implementation
    def navigate_to(self, *, view_name: str) -> None:
        """Navigate to a specific view.

        Args:
            view_name: The name of the view to navigate to.
        """
        if view_name not in self.views:
            self.update_status(message=f"Error: View '{view_name}' not found.")
            return

        # Hide current view
        if self.current_view:
            self.current_view.hide()

        # Show new view
        new_view = self.views[view_name]
        new_view.show()
        self.current_view = new_view

        self.update_status(message=f"Navigated to {view_name.replace('_', ' ').title()}")

    def update_status(self, *, message: str) -> None:
        """Update the status bar message.

        Args:
            message: The status message to display.
        """
        if hasattr(self, "status_label"):
            self.status_label.config(text=message)

    def run(self) -> None:
        """Start the application main loop."""
        self.update_status(message="Application started. Welcome!")
        self.root.mainloop()

    def cleanup(self) -> None:
        """Clean up resources when the application is closing."""
        # Destroy all views
        for view in self.views.values():
            view.destroy()

        self.views.clear()
        self.current_view = None
