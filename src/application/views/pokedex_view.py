"""Pokédex view for searching Pokémon GO data."""

import json
import threading
import tkinter as tk
from io import BytesIO
from tkinter import messagebox, scrolledtext
from typing import Final

from injector import inject
from PIL import Image, ImageTk  # type: ignore[import-untyped]

from src.application.views.base_view import BaseView, ViewNavigator
from src.constants.api_constants import POKEMON_GO_API_BASE_URL, POKEMON_SPRITE_BASE_URL
from src.domain.ports.outbound.http_client_port import HttpClientPort


class PokedexView(BaseView):
    """Pokédex view for searching and displaying Pokémon GO data."""

    # UI Configuration constants
    TITLE_TEXT: Final[str] = "Pokédex Search"
    TITLE_FONT: Final[tuple[str, int, str]] = ("Arial", 20, "bold")
    TITLE_COLOR: Final[str] = "#1f4e79"

    LABEL_FONT: Final[tuple[str, int]] = ("Arial", 12)
    BUTTON_FONT: Final[tuple[str, int, str]] = ("Arial", 10, "bold")

    ENTRY_WIDTH: Final[int] = 30
    RESULT_WIDTH: Final[int] = 80
    RESULT_HEIGHT: Final[int] = 20

    # Image configuration
    IMAGE_SIZE: Final[tuple[int, int]] = (200, 200)

    @inject
    def __init__(self, *, parent: tk.Widget, navigator: ViewNavigator, http_client: HttpClientPort) -> None:
        """Initialize the Pokédex view.

        Args:
            parent: The parent widget.
            navigator: The view navigator for navigation and status updates.
            http_client: HTTP client for API requests.
        """
        super().__init__(parent=parent, navigator=navigator)
        self.http_client = http_client

        # UI elements
        self.search_entry: tk.Entry | None = None
        self.search_button: tk.Button | None = None
        self.image_search_button: tk.Button | None = None
        self.result_text: scrolledtext.ScrolledText | None = None
        self.image_label: tk.Label | None = None
        self.back_button: tk.Button | None = None

        # Current search thread
        self._current_search_thread: threading.Thread | None = None
        self._current_image_thread: threading.Thread | None = None
        self._search_cancelled = False
        self._image_search_cancelled = False

    def create_widgets(self) -> None:
        """Create and layout the Pokédex widgets."""
        if not self.frame:
            return

        # Title
        title_label = tk.Label(self.frame, text=self.TITLE_TEXT, font=self.TITLE_FONT, fg=self.TITLE_COLOR, bg="white")
        title_label.pack(pady=(20, 30))

        # Search section
        search_frame = tk.Frame(self.frame, bg="white")
        search_frame.pack(pady=10)

        # Search label
        search_label = tk.Label(search_frame, text="Enter Pokémon name:", font=self.LABEL_FONT, bg="white")
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        # Search entry
        self.search_entry = tk.Entry(search_frame, width=self.ENTRY_WIDTH, font=self.LABEL_FONT)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind("<Return>", self._on_search_enter)

        # Search buttons
        button_frame = tk.Frame(search_frame, bg="white")
        button_frame.pack(side=tk.LEFT)

        # Regular search button
        self.search_button = tk.Button(
            button_frame,
            text="🔍 Search",
            font=self.BUTTON_FONT,
            bg="#2196F3",
            fg="white",
            command=self._on_search_click,
        )
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))

        # Image search button
        self.image_search_button = tk.Button(
            button_frame,
            text="🖼️ Search with Image",
            font=self.BUTTON_FONT,
            bg="#4CAF50",
            fg="white",
            command=self._on_image_search_click,
        )
        self.image_search_button.pack(side=tk.LEFT)

        # Content section with image and results
        content_frame = tk.Frame(self.frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 10))

        # Image section
        image_frame = tk.Frame(content_frame, bg="white")
        image_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        image_title_label = tk.Label(image_frame, text="Pokémon Image:", font=self.LABEL_FONT, bg="white")
        image_title_label.pack(anchor=tk.W, pady=(0, 5))

        # Image display - create a frame to constrain the image size
        image_container = tk.Frame(image_frame, bg="white", width=220, height=220)
        image_container.pack_propagate(False)  # Don't shrink the container
        image_container.pack(pady=(0, 10))

        self.image_label = tk.Label(
            image_container,
            text="No image loaded",
            font=self.LABEL_FONT,
            bg="lightgray",
            relief=tk.SUNKEN,
            justify=tk.CENTER,
        )
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Results section
        results_frame = tk.Frame(content_frame, bg="white")
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Results label
        results_label = tk.Label(results_frame, text="Search Results:", font=self.LABEL_FONT, bg="white")
        results_label.pack(anchor=tk.W, pady=(0, 5))

        # Results text area
        self.result_text = scrolledtext.ScrolledText(
            results_frame,
            width=self.RESULT_WIDTH,
            height=self.RESULT_HEIGHT,
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Navigation section
        nav_frame = tk.Frame(self.frame, bg="white")
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        # Back button
        self.back_button = tk.Button(
            nav_frame,
            text="← Back to Menu",
            font=self.BUTTON_FONT,
            bg="#FF9800",
            fg="white",
            command=self._on_back_click,
        )
        self.back_button.pack(side=tk.LEFT)

    def _on_search_enter(self, event: tk.Event) -> None:
        """Handle Enter key press in search entry."""
        self._on_search_click()

    def _on_search_click(self) -> None:
        """Handle search button click."""
        if not self.search_entry:
            return

        pokemon_name = self.search_entry.get().strip().lower()
        if not pokemon_name:
            self._show_error("Please enter a Pokémon name.")
            return

        # Cancel any ongoing searches (both data and image)
        self._cancel_current_search()
        self._cancel_current_image_search()

        # Clear any existing image
        self._clear_image()

        # Start new search in background thread (data only)
        self._search_cancelled = False
        self._current_search_thread = threading.Thread(
            target=self._search_pokemon_thread, args=(pokemon_name,), daemon=True
        )
        self._current_search_thread.start()

    def _on_image_search_click(self) -> None:
        """Handle image search button click."""
        if not self.search_entry:
            return

        pokemon_name = self.search_entry.get().strip().lower()
        if not pokemon_name:
            self._show_error("Please enter a Pokémon name.")
            return

        # Cancel any ongoing searches
        self._cancel_current_search()
        self._cancel_current_image_search()

        # Start new searches in background threads
        self._search_cancelled = False
        self._image_search_cancelled = False

        # Start both searches simultaneously
        self._current_search_thread = threading.Thread(
            target=self._search_pokemon_thread, args=(pokemon_name,), daemon=True
        )
        self._current_image_thread = threading.Thread(
            target=self._search_pokemon_image_thread, args=(pokemon_name,), daemon=True
        )

        self._current_search_thread.start()
        self._current_image_thread.start()

    def _cancel_current_search(self) -> None:
        """Cancel the current search if running."""
        if self._current_search_thread and self._current_search_thread.is_alive():
            self._search_cancelled = True

    def _cancel_current_image_search(self) -> None:
        """Cancel the current image search if running."""
        if self._current_image_thread and self._current_image_thread.is_alive():
            self._image_search_cancelled = True

    def _search_pokemon_image_thread(self, pokemon_name: str) -> None:
        """Search for and display Pokémon image in a background thread.

        Args:
            pokemon_name: The name of the Pokémon to search for.
        """
        try:
            # Update UI on main thread
            if self.frame:
                self.frame.after(0, lambda: self._set_image_searching_state(searching=True))
                self.frame.after(
                    0, lambda: self.navigator.update_status(message=f"Fetching image for {pokemon_name.title()}...")
                )

            # Try to get the Pokemon ID from PokeAPI first
            with self.http_client as client:
                if self._image_search_cancelled:
                    return

                # Get Pokemon data from PokeAPI to get the ID
                pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
                pokemon_id = None
                try:
                    pokemon_data = client.get(url=pokeapi_url)
                    pokemon_id = pokemon_data.get("id")
                    if not pokemon_id:
                        raise ValueError("No ID found in PokeAPI response")
                except Exception as e:
                    if not self._image_search_cancelled:
                        error_msg = f"Could not find Pokemon '{pokemon_name}' in PokeAPI: {e!s}"
                        if self.frame:
                            self.frame.after(0, lambda: self._show_image_error(error_msg))
                    return

                if self._image_search_cancelled:
                    return

                # Download the sprite image
                sprite_url = f"{POKEMON_SPRITE_BASE_URL}/{pokemon_id}.png"
                try:
                    image_data: bytes = client.get_binary(url=sprite_url)

                    if self._image_search_cancelled:
                        return

                    # Process the image
                    pil_image = Image.open(BytesIO(image_data))
                    # Convert to RGBA if needed for better compatibility
                    converted_image = pil_image.convert("RGBA") if pil_image.mode != "RGBA" else pil_image
                    resized_image = converted_image.resize(self.IMAGE_SIZE, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)  # type: ignore[no-untyped-call]

                    # Display the image on main thread
                    if self.frame:
                        self.frame.after(
                            0, lambda: self._display_pokemon_image(image=photo, pokemon_name=pokemon_name)
                        )

                except Exception as e:
                    if not self._image_search_cancelled:
                        error_msg = f"Failed to load image: {e!s}"
                        if self.frame:
                            self.frame.after(0, lambda: self._show_image_error(error_msg))

        except Exception as e:
            if not self._image_search_cancelled:
                error_msg = f"Error loading image for {pokemon_name}: {e!s}"
                if self.frame:
                    self.frame.after(0, lambda: self._show_image_error(error_msg))
        finally:
            if not self._image_search_cancelled and self.frame:
                self.frame.after(0, lambda: self._set_image_searching_state(searching=False))

    def _display_pokemon_image(self, *, image: ImageTk.PhotoImage, pokemon_name: str) -> None:
        """Display the Pokemon image in the UI.

        Args:
            image: The processed image to display.
            pokemon_name: The name of the Pokemon for the image.
        """
        if self.image_label:
            self.image_label.config(image=image, text="")
            # Keep a reference to prevent garbage collection
            self.image_label.image = image  # type: ignore[attr-defined]
            self.navigator.update_status(message=f"Image loaded for {pokemon_name.title()}!")

    def _show_image_error(self, message: str) -> None:
        """Show an image loading error.

        Args:
            message: The error message to display.
        """
        if self.image_label:
            self.image_label.config(image="", text=f"Image Error:\n{message}")
            # Clear any existing image reference
            if hasattr(self.image_label, "image"):
                delattr(self.image_label, "image")

    def _clear_image(self) -> None:
        """Clear the image display and show default text."""
        if self.image_label:
            self.image_label.config(image="", text="No image loaded")
            # Clear any existing image reference
            if hasattr(self.image_label, "image"):
                delattr(self.image_label, "image")

    def _set_image_searching_state(self, *, searching: bool) -> None:
        """Set the UI state for image searching.

        Args:
            searching: Whether currently searching for images.
        """
        if self.image_search_button:
            if searching:
                self.image_search_button.config(text="🔄 Loading Image...", state=tk.DISABLED)
            else:
                self.image_search_button.config(text="🖼️ Search with Image", state=tk.NORMAL)

    def _search_pokemon_thread(self, pokemon_name: str) -> None:
        """Search for Pokémon GO data using the API in a background thread.

        Args:
            pokemon_name: The name of the Pokémon to search for.
        """
        try:
            # Update UI on main thread
            if self.frame:
                self.frame.after(0, lambda: self._set_searching_state(searching=True))
                self.frame.after(0, lambda: self.navigator.update_status(message=f"Searching for {pokemon_name}..."))

            import httpx

            with httpx.Client(timeout=10.0) as client:
                if self._search_cancelled:
                    return

                # First, get all Pokémon names to find the correct ID
                names_url = f"{POKEMON_GO_API_BASE_URL}/pokemon_names.json"
                names_response = client.get(names_url)
                names_response.raise_for_status()
                pokemon_names = names_response.json()

                # Validate that we got the expected response format
                if not isinstance(pokemon_names, dict):
                    raise ValueError(f"Expected dictionary response from names API, got {type(pokemon_names)}")

                # Find the Pokémon by name (case-insensitive)
                pokemon_id = None
                pokemon_exact_name = None
                for pid, data in pokemon_names.items():
                    if isinstance(data, dict) and "name" in data and data["name"].lower() == pokemon_name.lower():
                        pokemon_id = int(pid)
                        pokemon_exact_name = data["name"]
                        break

                if pokemon_id is None:
                    if self.frame:
                        self.frame.after(
                            0, lambda: self._show_error(f"Pokémon '{pokemon_name}' not found in Pokémon GO.")
                        )
                    return

                if self._search_cancelled:
                    return

                # Get comprehensive Pokémon GO data
                pokemon_data = {"id": pokemon_id, "name": pokemon_exact_name}

                # Get stats
                stats_url = f"{POKEMON_GO_API_BASE_URL}/pokemon_stats.json"
                stats_response = client.get(stats_url)
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    if isinstance(stats_data, list):
                        for stat in stats_data:
                            if isinstance(stat, dict) and "id" in stat and stat["id"] == pokemon_id:
                                pokemon_data["stats"] = {
                                    "base_attack": stat.get("base_attack", "N/A"),
                                    "base_defense": stat.get("base_defense", "N/A"),
                                    "base_stamina": stat.get("base_stamina", "N/A"),
                                }
                                break

                # Get max CP
                cp_url = f"{POKEMON_GO_API_BASE_URL}/pokemon_max_cp.json"
                cp_response = client.get(cp_url)
                if cp_response.status_code == 200:
                    cp_data = cp_response.json()
                    if isinstance(cp_data, list):
                        for cp in cp_data:
                            if isinstance(cp, dict) and "id" in cp and cp["id"] == pokemon_id:
                                pokemon_data["max_cp"] = cp.get("max_cp", "N/A")
                                break

                # Get types
                types_url = f"{POKEMON_GO_API_BASE_URL}/pokemon_types.json"
                types_response = client.get(types_url)
                if types_response.status_code == 200:
                    types_data = types_response.json()
                    if isinstance(types_data, list):
                        for type_data in types_data:
                            if (
                                isinstance(type_data, dict)
                                and "pokemon_id" in type_data
                                and type_data["pokemon_id"] == pokemon_id
                            ):
                                pokemon_data["types"] = type_data.get("type", "N/A")
                                break

            if self._search_cancelled:
                return

            # Format and display results on main thread
            formatted_data = json.dumps(pokemon_data, indent=2, ensure_ascii=False)
            if self.frame:
                self.frame.after(0, lambda: self._display_results(results=formatted_data))
                self.frame.after(
                    0, lambda: self.navigator.update_status(message=f"Found {pokemon_exact_name} in Pokémon GO!")
                )

        except httpx.HTTPStatusError as e:
            if not self._search_cancelled and self.frame:
                error_msg = f"API request failed (HTTP {e.response.status_code})"
                self.frame.after(0, lambda: self._show_error(error_msg))
        except httpx.RequestError as e:
            if not self._search_cancelled and self.frame:
                error_msg = f"Network error: {e!s}"
                self.frame.after(0, lambda: self._show_error(error_msg))
        except KeyError as e:
            if not self._search_cancelled and self.frame:
                error_msg = f"API response missing expected key {e}. The Pokemon GO API structure may have changed."
                self.frame.after(0, lambda: self._show_error(error_msg))
        except ValueError as e:
            if not self._search_cancelled and self.frame:
                error_msg = f"Invalid API response format: {e!s}"
                self.frame.after(0, lambda: self._show_error(error_msg))
        except Exception as e:
            if not self._search_cancelled and self.frame:
                error_msg = f"Error searching for {pokemon_name}: {e!s}"
                self.frame.after(0, lambda: self._show_error(error_msg))
        finally:
            if not self._search_cancelled and self.frame:
                self.frame.after(0, lambda: self._set_searching_state(searching=False))

    def _set_searching_state(self, *, searching: bool) -> None:
        """Set the UI state for searching.

        Args:
            searching: Whether currently searching.
        """
        if self.search_button:
            if searching:
                self.search_button.config(text="🔄 Searching...", state=tk.DISABLED)
            else:
                self.search_button.config(text="🔍 Search", state=tk.NORMAL)

        if self.image_search_button:
            if searching:
                self.image_search_button.config(state=tk.DISABLED)
            else:
                self.image_search_button.config(state=tk.NORMAL)

    def _display_results(self, *, results: str) -> None:
        """Display search results in the text area.

        Args:
            results: The formatted results to display.
        """
        if not self.result_text:
            return

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, results)
        self.result_text.config(state=tk.DISABLED)

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
        self._cancel_current_image_search()
        self.navigator.navigate_to(view_name="main_menu")

    def on_show(self) -> None:
        """Called when the Pokédex view is shown."""
        self.navigator.update_status(message="Enter a Pokémon name to search for GO data.")
        if self.search_entry:
            self.search_entry.focus_set()

    def on_destroy(self) -> None:
        """Called when the view is destroyed."""
        # Cancel any ongoing searches
        self._cancel_current_search()
        self._cancel_current_image_search()
        super().on_destroy()
