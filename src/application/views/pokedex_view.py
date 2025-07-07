"""Pokédex view for searching Pokémon GO data."""

import json
import threading
from tkinter import END, Event, messagebox, scrolledtext
from tkinter.ttk import Button, Entry, Frame, Label, Widget
from typing import Final

from injector import inject

from src.application.constants.api_constants import (
    POKEMON_ASSETS_KEY,
    POKEMON_ID_KEY,
    POKEMON_IMAGE_KEY,
    POKEMON_SHINY_IMAGE_KEY,
)
from src.application.constants.ui_constants import (
    ANCHOR_W,
    KEY_RETURN,
    PACK_FILL_BOTH,
    PACK_FILL_X,
    PACK_FILL_Y,
    PACK_SIDE_LEFT,
    TEXT_WRAP_WORD,
    TITLE_FONT,
    WIDGET_STATE_DISABLED,
    WIDGET_STATE_NORMAL,
)
from src.application.constants.view_constants import IMAGE, MAIN_MENU_VIEW
from src.application.services.pokemon_go_api import PokemonGoApiService
from src.application.services.web_image_processing import WebImageProcessingService
from src.application.views.base_view import BaseView, ViewNavigator
from src.domain.interfaces.image_processor import ProcessedImage


class PokedexView(BaseView):
    """Pokédex view for searching and displaying Pokémon GO data."""

    # UI Configuration constants
    TITLE_TEXT: Final[str] = "Pokédex API Search"
    ENTRY_WIDTH: Final[int] = 30
    RESULT_WIDTH: Final[int] = 80
    RESULT_HEIGHT: Final[int] = 20

    @inject
    def __init__(
        self,
        *,
        parent: Widget,
        navigator: ViewNavigator,
        image_service: WebImageProcessingService,
        pokemon_go_api_service: PokemonGoApiService,
    ) -> None:
        """Initialize the Pokédex view.

        Args:
            parent: The parent widget.
            navigator: The view navigator for navigation and status updates.
            image_service: Service for handling Pokemon image operations.
            pokemon_go_api_service: Service for fetching Pokemon GO data.
        """
        super().__init__(parent=parent, navigator=navigator)
        self.image_service = image_service
        self.pokemon_go_api_service = pokemon_go_api_service

        # UI elements
        self.search_entry: Entry | None = None
        self.search_button: Button | None = None
        self.result_text: scrolledtext.ScrolledText | None = None
        self.base_image_label: Label | None = None
        self.shiny_image_label: Label | None = None
        self.back_button: Button | None = None

        # Current search thread
        self._current_search_thread: threading.Thread | None = None
        self._current_base_image_thread: threading.Thread | None = None
        self._current_shiny_image_thread: threading.Thread | None = None
        self._search_cancelled: bool = False
        self._base_image_search_cancelled: bool = False
        self._shiny_image_search_cancelled: bool = False
        self._current_pokemon_name: str | None = None

    def create_widgets(self) -> None:
        """Create and layout the Pokédex widgets."""
        if not self.frame:
            return

        self._create_title_section()
        self._create_search_section()
        self._create_navigation_section()
        self._create_content_section()

    def _create_title_section(self) -> None:
        """Create the title section of the Pokédex view."""
        if not self.frame:
            return
        title_label = Label(self.frame, text=self.TITLE_TEXT, font=TITLE_FONT)
        title_label.pack(pady=(20, 30))

    def _create_search_section(self) -> None:
        """Create the search input and buttons section."""
        if not self.frame:
            return
        search_frame = Frame(self.frame)
        search_frame.pack(pady=10)
        # Search label.
        search_label = Label(search_frame, text="Enter name:")
        search_label.pack(side=PACK_SIDE_LEFT, padx=(0, 10))
        # Search entry
        self.search_entry = Entry(search_frame, width=self.ENTRY_WIDTH)
        self.search_entry.pack(side=PACK_SIDE_LEFT, padx=(0, 10))
        self.search_entry.bind(KEY_RETURN, self._on_search_enter)
        # Search button.
        self.search_button = Button(search_frame, text="🔍 Search", command=self._on_search_click)
        self.search_button.pack(side=PACK_SIDE_LEFT, padx=(0, 5))

    def _create_content_section(self) -> None:
        """Create the main content section with image and results."""
        if not self.frame:
            return
        # Content frame - don't expand fully to leave room for navigation
        content_frame = Frame(self.frame)
        content_frame.pack(fill=PACK_FILL_BOTH, expand=True, pady=(20, 5))
        # Image section.
        self._create_image_section(parent=content_frame)
        self._create_results_section(parent=content_frame)

    def _create_image_section(self, *, parent: Frame) -> None:
        """Create the image display section.

        Args:
            parent: The parent frame to contain the image section.
        """
        image_frame = Frame(parent)
        image_frame.pack(side=PACK_SIDE_LEFT, fill=PACK_FILL_Y, padx=(0, 20))

        # Base image section.
        base_image_container = Frame(image_frame, width=220, height=220)
        base_image_container.pack_propagate(False)  # Don't shrink the container to fit the image.
        base_image_container.pack(pady=(0, 10))
        # Base image label.
        self.base_image_label = Label(base_image_container)
        self.base_image_label.pack(expand=True, fill=PACK_FILL_BOTH)

        # Shiny image section.
        shiny_image_container = Frame(image_frame, width=220, height=220)
        shiny_image_container.pack_propagate(False)  # Don't shrink the container to fit the image.
        shiny_image_container.pack(pady=(0, 10))
        # Shiny image label.
        self.shiny_image_label = Label(shiny_image_container)
        self.shiny_image_label.pack(expand=True, fill=PACK_FILL_BOTH)

    def _create_results_section(self, *, parent: Frame) -> None:
        """Create the search results display section.

        Args:
            parent: The parent frame to contain the results section.
        """
        results_frame = Frame(parent)
        results_frame.pack(side=PACK_SIDE_LEFT, fill=PACK_FILL_BOTH, expand=True)
        # Results label.
        results_label = Label(results_frame, text="Search Results:")
        results_label.pack(anchor=ANCHOR_W, pady=(0, 5))
        # Results text area.
        self.result_text = scrolledtext.ScrolledText(
            results_frame,
            width=self.RESULT_WIDTH,
            height=self.RESULT_HEIGHT,
            font=("Consolas", 10),
            wrap=TEXT_WRAP_WORD,
            state=WIDGET_STATE_DISABLED,
        )
        self.result_text.pack(fill=PACK_FILL_BOTH, expand=True)

    def _create_navigation_section(self) -> None:
        """Create the navigation section with back button."""
        if not self.frame:
            return
        # Navigation frame - pack at bottom to ensure visibility
        nav_frame = Frame(self.frame)
        nav_frame.pack(side="bottom", fill=PACK_FILL_X, pady=(10, 10))
        # Back button.
        self.back_button = Button(nav_frame, text="⬅️ Back to Menu", command=self._on_back_click)
        self.back_button.pack(side=PACK_SIDE_LEFT, padx=(10, 0))

    def _on_search_enter(self, _: Event) -> None:
        """Handle Enter key press in search entry.

        Args:
            event: The tkinter event object.
        """
        self._on_search_click()

    def _on_search_click(self) -> None:
        """Handle search button click."""
        if not self.search_entry:
            return
        if not (pokemon_name := self.search_entry.get().strip().lower()):
            self._show_error("Please enter a Pokémon name.")
            return
        # Cancel any ongoing searches (both data and images).
        self._cancel_current_search()
        self._cancel_current_image_searches()
        # Clear any existing images.
        self._clear_images()
        # Start new search in background thread (data and images).
        self._search_cancelled = False
        self._current_search_thread = threading.Thread(
            target=self._search_pokemon_thread, args=(pokemon_name,), daemon=True
        )
        self._current_search_thread.start()

    def _cancel_current_search(self) -> None:
        """Cancel the current search if running."""
        if self._current_search_thread and self._current_search_thread.is_alive():
            self._search_cancelled = True

    def _cancel_current_image_searches(self) -> None:
        """Cancel the current image searches if running."""
        if self._current_base_image_thread and self._current_base_image_thread.is_alive():
            self._base_image_search_cancelled = True
        if self._current_shiny_image_thread and self._current_shiny_image_thread.is_alive():
            self._shiny_image_search_cancelled = True

    def _display_pokemon_base_image(self, *, image: ProcessedImage, pokemon_name: str) -> None:
        """Display the Pokemon base image in the UI.

        Args:
            image: The processed image to display.
            pokemon_name: The name of the Pokemon for the image.
        """
        if self.base_image_label:
            # Type ignore needed because ProcessedImage protocol doesn't satisfy tkinter's
            # strict _Image type requirement, but it works at runtime since the actual
            # implementation returns a PhotoImage which is compatible.
            self.base_image_label.config(image=image, text="")  # type: ignore[call-overload]
            # Keep a reference to prevent garbage collection.
            self.base_image_label.image = image  # type: ignore[attr-defined]
            self.navigator.update_status(message=f"Base image loaded for {pokemon_name.title()}!")

    def _display_pokemon_shiny_image(self, *, image: ProcessedImage, pokemon_name: str) -> None:
        """Display the Pokemon shiny image in the UI.

        Args:
            image: The processed image to display.
            pokemon_name: The name of the Pokemon for the image.
        """
        if self.shiny_image_label:
            # Type ignore needed because ProcessedImage protocol doesn't satisfy tkinter's
            # strict _Image type requirement, but it works at runtime since the actual
            # implementation returns a PhotoImage which is compatible
            self.shiny_image_label.config(image=image, text="")  # type: ignore[call-overload]
            # Keep a reference to prevent garbage collection.
            self.shiny_image_label.image = image  # type: ignore[attr-defined]
            self.navigator.update_status(message=f"Shiny image loaded for {pokemon_name.title()}!")

    def _show_base_image_error(self, message: str) -> None:
        """Show a base image loading error.

        Args:
            message: The error message to display.
        """
        if self.base_image_label:
            self.base_image_label.config(image="", text=f"Base Image Error:\n{message}")
            if hasattr(self.base_image_label, IMAGE):
                delattr(self.base_image_label, IMAGE)

    def _show_shiny_image_error(self, message: str) -> None:
        """Show a shiny image loading error.

        Args:
            message: The error message to display.
        """
        if self.shiny_image_label:
            self.shiny_image_label.config(image="", text=f"Shiny Image Error:\n{message}")
            if hasattr(self.shiny_image_label, IMAGE):
                delattr(self.shiny_image_label, IMAGE)

    def _clear_images(self) -> None:
        """Clear both image displays and show default text."""
        if self.base_image_label:
            self.base_image_label.config(image="", text="No image loaded.")
            if hasattr(self.base_image_label, IMAGE):
                delattr(self.base_image_label, IMAGE)
        if self.shiny_image_label:
            self.shiny_image_label.config(image="", text="No image loaded.")
            if hasattr(self.shiny_image_label, IMAGE):
                delattr(self.shiny_image_label, IMAGE)

    def _on_base_image_success(self, image: ProcessedImage) -> None:
        """Handle successful base image loading from the service.

        Args:
            image: The processed image ready for display.
        """
        # This callback is called from a background thread, so we need to use frame.after.
        # Use the stored pokemon name for display
        if self.frame and self._current_pokemon_name:
            pokemon_name = self._current_pokemon_name
            self.frame.after(0, lambda: self._display_pokemon_base_image(image=image, pokemon_name=pokemon_name))

    def _on_base_image_error(self, error_message: str) -> None:
        """Handle base image loading error from the service.

        Args:
            error_message: The error message from the service.
        """
        # This callback is called from a background thread, so we need to use frame.after
        if self.frame:
            self.frame.after(0, lambda: self._show_base_image_error(error_message))

    def _on_shiny_image_success(self, image: ProcessedImage) -> None:
        """Handle successful shiny image loading from the service.

        Args:
            image: The processed image ready for display.
        """
        # This callback is called from a background thread, so we need to use frame.after.
        # Use the stored pokemon name for display
        if self.frame and self._current_pokemon_name:
            pokemon_name = self._current_pokemon_name
            self.frame.after(0, lambda: self._display_pokemon_shiny_image(image=image, pokemon_name=pokemon_name))

    def _on_shiny_image_error(self, error_message: str) -> None:
        """Handle shiny image loading error from the service.

        Args:
            error_message: The error message from the service.
        """
        # This callback is called from a background thread, so we need to use frame.after
        if self.frame:
            self.frame.after(0, lambda: self._show_shiny_image_error(error_message))

    def _search_pokemon_thread(self, pokemon_name: str) -> None:
        """Search for Pokémon GO data using the Pokemon GO API service.

        Args:
            pokemon_name: The name of the Pokémon to search for.
        """
        # Start Pokemon GO data search using the service
        self._current_search_thread = self.pokemon_go_api_service.fetch_pokemon_data_async(
            pokemon_name=pokemon_name,
            on_success=self._on_pokemon_data_success,
            on_error=self._on_pokemon_data_error,
            on_started=self._on_pokemon_data_started,
            on_finished=self._on_pokemon_data_finished,
            cancellation_check=lambda: self._search_cancelled,
        )

    def _on_pokemon_data_success(self, data: dict) -> None:
        """Handle successful data retrieval from the service.

        Args:
            data: The retrieved data.
        """
        if self.frame:
            self.frame.after(0, lambda: self._display_results(results=json.dumps(data, indent=2, ensure_ascii=False)))

            # Extract Pokemon name safely
            pokemon_name = str(data.get(POKEMON_ID_KEY, "Unknown")).title()
            self.frame.after(0, lambda: self.navigator.update_status(message=f"Found {pokemon_name} in Pokémon GO!"))

            # Extract image URLs from the assets field and fetch both images
            assets = data.get(POKEMON_ASSETS_KEY) or {}

            # Fetch base image
            if base_image_url := assets.get(POKEMON_IMAGE_KEY):
                self._fetch_pokemon_base_image(image_url=base_image_url, pokemon_name=pokemon_name)

            # Fetch shiny image
            if shiny_image_url := assets.get(POKEMON_SHINY_IMAGE_KEY):
                self._fetch_pokemon_shiny_image(image_url=shiny_image_url, pokemon_name=pokemon_name)

    def _fetch_pokemon_base_image(self, *, image_url: str, pokemon_name: str) -> None:
        """Fetch Pokemon base image using the image service.

        Args:
            image_url: The URL of the image to fetch.
            pokemon_name: The name of the Pokemon.
        """
        # Store the pokemon name for use in the callback
        self._current_pokemon_name = pokemon_name

        # Start base image search using the service.
        self._base_image_search_cancelled = False
        self._current_base_image_thread = self.image_service.fetch_image_async(
            image_url=image_url,
            on_success=self._on_base_image_success,
            on_error=self._on_base_image_error,
            cancellation_check=lambda: self._base_image_search_cancelled,
        )

    def _fetch_pokemon_shiny_image(self, *, image_url: str, pokemon_name: str) -> None:
        """Fetch Pokemon shiny image using the image service.

        Args:
            image_url: The URL of the image to fetch.
            pokemon_name: The name of the Pokemon.
        """
        # Store the pokemon name for use in the callback
        self._current_pokemon_name = pokemon_name

        # Start shiny image search using the service.
        self._shiny_image_search_cancelled = False
        self._current_shiny_image_thread = self.image_service.fetch_image_async(
            image_url=image_url,
            on_success=self._on_shiny_image_success,
            on_error=self._on_shiny_image_error,
            cancellation_check=lambda: self._shiny_image_search_cancelled,
        )

    def _on_pokemon_data_error(self, error_message: str) -> None:
        """Handle error during data retrieval from the service.

        Args:
            error_message: The error message from the service.
        """
        if self.frame:
            self.frame.after(0, lambda: self._show_error(error_message))

    def _on_pokemon_data_started(self) -> None:
        """Handle when data retrieval starts."""
        if self.frame:
            self.frame.after(0, lambda: self._set_searching_state(searching=True))

    def _on_pokemon_data_finished(self) -> None:
        """Handle when data retrieval finishes."""
        if self.frame:
            self.frame.after(0, lambda: self._set_searching_state(searching=False))

    def _set_searching_state(self, *, searching: bool) -> None:
        """Set the UI state for searching.

        Args:
            searching: Whether currently searching.
        """
        if self.search_button:
            if searching:
                self.search_button.config(text="🔄 Searching...", state=WIDGET_STATE_DISABLED)
            else:
                self.search_button.config(text="🔍 Search", state=WIDGET_STATE_NORMAL)

    def _display_results(self, *, results: str) -> None:
        """Display search results in the text area.

        Args:
            results: The formatted results to display.
        """
        if not self.result_text:
            return

        self.result_text.config(state=WIDGET_STATE_NORMAL)  # type: ignore[call-overload]
        self.result_text.delete(1.0, END)
        self.result_text.insert(1.0, results)
        self.result_text.config(state=WIDGET_STATE_DISABLED)  # type: ignore[call-overload]

    def _show_error(self, message: str) -> None:
        """Show an error message to the user.

        Args:
            message: The error message to display.
        """
        messagebox.showerror("Error", message)
        if self.result_text:
            self._display_results(results=f"Error: {message}")
        self.navigator.update_status(message="Search failed.")

    def _on_back_click(self) -> None:
        """Handle back button click."""
        # Cancel any ongoing searches
        self._cancel_current_search()
        self._cancel_current_image_searches()
        self.navigator.navigate_to(view_name=MAIN_MENU_VIEW)

    def on_show(self) -> None:
        """Called when the Pokédex view is shown."""
        self.navigator.update_status(message="Enter a Pokémon name to search for GO data.")
        if self.search_entry:
            self.search_entry.focus_set()

    def on_destroy(self) -> None:
        """Called when the view is destroyed."""
        # Cancel any ongoing searches.
        self._cancel_current_search()
        self._cancel_current_image_searches()
        super().on_destroy()
