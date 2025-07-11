"""Pokédex view for searching Pokémon GO data."""

import json
import threading
from tkinter import END, Event, messagebox, scrolledtext
from tkinter.ttk import Button, Entry, Frame, Label, Widget
from typing import Final

from injector import inject

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
from src.application.services.web_image_processing import WebImageProcessingService
from src.application.use_cases.fetch_pokemon_use_case import FetchPokemonUseCase
from src.application.views.base_view import BaseView, ViewNavigator
from src.domain.interfaces.image_processor import ProcessedImage
from src.infrastructure.constants.api_constants import (
    POKEMON_ASSETS_KEY,
    POKEMON_ID_KEY,
    POKEMON_IMAGE_KEY,
    POKEMON_SHINY_IMAGE_KEY,
)


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
        fetch_pokemon_use_case: FetchPokemonUseCase,
    ) -> None:
        """
        Initialize a new Pokédex view for searching and displaying Pokémon GO data.
        
        Creates the UI components and sets up dependencies for navigation, image processing, and asynchronous Pokémon data fetching.
        """
        super().__init__(parent=parent, navigator=navigator)
        self.image_service = image_service
        self.fetch_pokemon_use_case = fetch_pokemon_use_case

        # UI elements.
        self.search_entry: Entry | None = None
        self.search_button: Button | None = None
        self.result_text: scrolledtext.ScrolledText | None = None
        self.base_image_label: Label | None = None
        self.shiny_image_label: Label | None = None
        self.back_button: Button | None = None

        # Current search threads.
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
        """
        Create the UI section containing the Pokémon name input field and search button.
        
        This section includes a label prompting for input, an entry widget for typing the Pokémon name, and a button to initiate the search. The entry widget also binds the Enter key to trigger the search action.
        """
        if not self.frame:
            return
        search_frame = Frame(self.frame)
        search_frame.pack(pady=10)
        # Search label.
        search_label = Label(search_frame, text="Enter name:")
        search_label.pack(side=PACK_SIDE_LEFT, padx=(0, 10))
        # Search entry.
        self.search_entry = Entry(search_frame, width=self.ENTRY_WIDTH)
        self.search_entry.pack(side=PACK_SIDE_LEFT, padx=(0, 10))
        self.search_entry.bind(KEY_RETURN, self._on_search_enter)
        # Search button.
        self.search_button = Button(search_frame, text="🔍 Search", command=self._on_search_click)
        self.search_button.pack(side=PACK_SIDE_LEFT, padx=(0, 5))

    def _create_content_section(self) -> None:
        """
        Create the main content section of the view, including the Pokémon image display and results area.
        """
        if not self.frame:
            return
        # Content frame - don't expand fully to leave room for navigation.
        content_frame = Frame(self.frame)
        content_frame.pack(fill=PACK_FILL_BOTH, expand=True, pady=(20, 5))
        # Image section.
        self._create_image_section(parent=content_frame)
        self._create_results_section(parent=content_frame)

    def _create_image_section(self, *, parent: Frame) -> None:
        """
        Creates and adds the Pokémon base and shiny image display sections to the given parent frame.
        
        Parameters:
            parent (Frame): The parent frame to which the image section is added.
        """
        image_frame = Frame(parent)
        image_frame.pack(side=PACK_SIDE_LEFT, fill=PACK_FILL_Y, padx=(0, 20))

        # Base image section.
        base_image_container = Frame(image_frame, width=220, height=220)
        base_image_container.pack_propagate(False)  # Don't shrink the container to fit the image.
        base_image_container.pack(pady=(0, 10))
        self.base_image_label = Label(base_image_container)
        self.base_image_label.pack(expand=True, fill=PACK_FILL_BOTH)

        # Shiny image section.
        shiny_image_container = Frame(image_frame, width=220, height=220)
        shiny_image_container.pack_propagate(False)  # Don't shrink the container to fit the image.
        shiny_image_container.pack(pady=(0, 10))
        self.shiny_image_label = Label(shiny_image_container)
        self.shiny_image_label.pack(expand=True, fill=PACK_FILL_BOTH)

    def _create_results_section(self, *, parent: Frame) -> None:
        """
        Create and add the scrollable text area for displaying Pokémon search results.
        
        Parameters:
        	parent (Frame): The parent frame that will contain the results section.
        """
        results_frame = Frame(parent)
        results_frame.pack(side=PACK_SIDE_LEFT, fill=PACK_FILL_BOTH, expand=True)
        results_label = Label(results_frame, text="Search Results:")
        results_label.pack(anchor=ANCHOR_W, pady=(0, 5))
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
        """
        Create the navigation section containing a back button for returning to the main menu.
        """
        if not self.frame:
            return
        nav_frame = Frame(self.frame)
        nav_frame.pack(side="bottom", fill=PACK_FILL_X, pady=(10, 10))
        self.back_button = Button(nav_frame, text="⬅️ Back to Menu", command=self._on_back_click)
        self.back_button.pack(side=PACK_SIDE_LEFT, padx=(10, 0))

    def _on_search_enter(self, _: Event) -> None:
        """Handle Enter key press in search entry.

        Args:
            event: The tkinter event object.
        """
        self._on_search_click()

    def _on_search_click(self) -> None:
        """
        Initiates a Pokémon search when the search button is clicked.
        
        Validates the input, cancels any ongoing searches or image fetches, clears previous images, and starts a new background thread to fetch Pokémon data based on the entered name. Displays an error if the input is empty.
        """
        if not self.search_entry:
            return
        if not (pokemon_name := self.search_entry.get().strip().lower()):
            self._show_error("Please enter a Pokémon name.")
            return
        self._cancel_current_search()
        self._cancel_current_image_searches()
        self._clear_images()
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
        """
        Displays the shiny variant image of a Pokémon in the UI and updates the status message.
        
        Parameters:
            image (ProcessedImage): The processed shiny image to display.
            pokemon_name (str): The name of the Pokémon whose shiny image is shown.
        """
        if self.shiny_image_label:
            # Type ignore needed because ProcessedImage protocol doesn't satisfy tkinter's
            # strict _Image type requirement, but it works at runtime since the actual
            # implementation returns a PhotoImage which is compatible.
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
        """
        Handles successful loading of the base Pokémon image by scheduling its display in the UI thread.
        
        Parameters:
            image (ProcessedImage): The processed image to display as the base Pokémon image.
        """
        # This callback is called from a background thread, so we need to use frame.after.
        # Use the stored pokemon name for display.
        if self.frame and self._current_pokemon_name:
            pokemon_name = self._current_pokemon_name
            self.frame.after(0, lambda: self._display_pokemon_base_image(image=image, pokemon_name=pokemon_name))

    def _on_base_image_error(self, error_message: str) -> None:
        """
        Handles errors encountered while loading the base Pokémon image by scheduling an error display update on the UI thread.
        
        Parameters:
            error_message (str): The error message describing the image loading failure.
        """
        # This callback is called from a background thread, so we need to use frame.after.
        if self.frame:
            self.frame.after(0, lambda: self._show_base_image_error(error_message))

    def _on_shiny_image_success(self, image: ProcessedImage) -> None:
        """
        Handles the successful retrieval of a shiny Pokémon image and schedules its display in the UI.
        
        Parameters:
        	image (ProcessedImage): The processed shiny image to display.
        """
        # This callback is called from a background thread, so we need to use frame.after.
        # Use the stored pokemon name for display.
        if self.frame and self._current_pokemon_name:
            pokemon_name = self._current_pokemon_name
            self.frame.after(0, lambda: self._display_pokemon_shiny_image(image=image, pokemon_name=pokemon_name))

    def _on_shiny_image_error(self, error_message: str) -> None:
        """
        Handles errors that occur while loading the shiny Pokémon image by scheduling an error display update on the UI thread.
        
        Parameters:
            error_message (str): The error message describing the image loading failure.
        """
        # This callback is called from a background thread, so we need to use frame.after.
        if self.frame:
            self.frame.after(0, lambda: self._show_shiny_image_error(error_message))

    def _search_pokemon_thread(self, pokemon_name: str) -> None:
        """
        Initiates an asynchronous search for Pokémon GO data by name and manages callbacks for result handling.
        
        Parameters:
            pokemon_name (str): The name of the Pokémon to search for.
        """
        self._current_search_thread = self.fetch_pokemon_use_case.fetch_pokemon_data_async(
            pokemon_name=pokemon_name,
            on_success=self._on_pokemon_data_success,
            on_error=self._on_pokemon_data_error,
            on_started=self._on_pokemon_data_started,
            on_finished=self._on_pokemon_data_finished,
            cancellation_check=lambda: self._search_cancelled,
        )

    def _on_pokemon_data_success(self, data: dict) -> None:
        """
        Handles successful retrieval of Pokémon data by displaying results, updating status, and initiating image fetches for base and shiny forms.
        
        Parameters:
            data (dict): The Pokémon data retrieved from the service.
        """
        if self.frame:
            self.frame.after(0, lambda: self._display_results(results=json.dumps(data, indent=2, ensure_ascii=False)))

            pokemon_name = str(data.get(POKEMON_ID_KEY, "Unknown")).title()
            self.frame.after(0, lambda: self.navigator.update_status(message=f"Found {pokemon_name} in Pokémon GO!"))

            assets = data.get(POKEMON_ASSETS_KEY) or {}

            if base_image_url := assets.get(POKEMON_IMAGE_KEY):
                self._fetch_pokemon_base_image(image_url=base_image_url, pokemon_name=pokemon_name)
            if shiny_image_url := assets.get(POKEMON_SHINY_IMAGE_KEY):
                self._fetch_pokemon_shiny_image(image_url=shiny_image_url, pokemon_name=pokemon_name)

    def _fetch_pokemon_base_image(self, *, image_url: str, pokemon_name: str) -> None:
        """
        Initiate asynchronous fetching of a Pokémon's base image and handle the result via callbacks.
        
        Parameters:
            image_url (str): URL of the Pokémon's base image.
            pokemon_name (str): Name of the Pokémon whose image is being fetched.
        """
        # Store the pokemon name for use in the callback.
        self._current_pokemon_name = pokemon_name
        self._base_image_search_cancelled = False
        self._current_base_image_thread = self.image_service.fetch_image_async(
            image_url=image_url,
            on_success=self._on_base_image_success,
            on_error=self._on_base_image_error,
            cancellation_check=lambda: self._base_image_search_cancelled,
        )

    def _fetch_pokemon_shiny_image(self, *, image_url: str, pokemon_name: str) -> None:
        """
        Initiate asynchronous fetching of a Pokémon's shiny image using the image service.
        
        Parameters:
            image_url (str): URL of the shiny image to fetch.
            pokemon_name (str): Name of the Pokémon whose shiny image is being fetched.
        """
        # Store the pokemon name for use in the callback.
        self._current_pokemon_name = pokemon_name
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
        """
        Handles the back button click by canceling ongoing searches and image fetches, then navigates to the main menu view.
        """
        self._cancel_current_search()
        self._cancel_current_image_searches()
        self.navigator.navigate_to(view_name=MAIN_MENU_VIEW)

    def on_show(self) -> None:
        """Called when the Pokédex view is shown."""
        self.navigator.update_status(message="Enter a Pokémon name to search for GO data.")
        if self.search_entry:
            self.search_entry.focus_set()

    def on_destroy(self) -> None:
        """
        Performs cleanup when the view is destroyed by canceling ongoing search and image fetch operations before invoking the superclass destroy method.
        """
        self._cancel_current_search()
        self._cancel_current_image_searches()
        super().on_destroy()
