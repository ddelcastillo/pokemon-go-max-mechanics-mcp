"""Abstract base view for the application."""

from abc import abstractmethod
from tkinter import BOTH
from tkinter.ttk import Frame, TclError, Widget
from typing import Protocol


class ViewNavigator(Protocol):
    """Protocol for view navigation."""

    def navigate_to(self, *, view_name: str) -> None:
        """Navigate to a specific view.

        Args:
            view_name: The name of the view to navigate to.
        """
        ...

    def update_status(self, *, message: str) -> None:
        """Update the status bar message.

        Args:
            message: The status message to display.
        """
        ...


class BaseView:
    """Abstract base class for all application views using tkinter.

    This class provides a standard structure for building user interface "views"
    in a tkinter-based application. A "view" in this context is a screen or panel
    that displays a particular part of the application's UI, such as a main menu,
    a search form, or a results page.

    BaseView manages the lifecycle of a tkinter Frame, which is a container for
    other widgets (buttons, labels, etc.). It provides methods to show, hide, and
    destroy the view, as well as hooks (`on_show`, `on_hide`, `on_destroy`) that
    subclasses can override to perform custom logic at each stage.

    To use BaseView:
      - Subclass it and implement the `create_widgets` method to add your widgets
        to `self.frame`.
      - Use the provided `show`, `hide`, and `destroy` methods to control the view's
        visibility and cleanup.
      - Use the `navigator` attribute to trigger navigation or update status messages.

    Args:
        parent: The parent tkinter widget (usually the main window or a container).
        navigator: An object implementing the ViewNavigator protocol, used for
            navigation and status updates.

    Example:
        class MyView(BaseView):
            def create_widgets(self) -> None:
                label = tk.Label(self.frame, text="Hello, world!")
                label.pack()
    """

    def __init__(self, *, parent: Widget, navigator: ViewNavigator) -> None:
        """Initialize the base view.

        Args:
            parent: The parent widget.
            navigator: The view navigator for navigation and status updates.
        """
        self.parent = parent
        self.navigator = navigator
        self.frame: Frame | None = None

    @abstractmethod
    def create_widgets(self) -> None:
        """Create and layout the view widgets.

        Subclasses must implement this method to populate self.frame with
        the desired tkinter widgets.
        """
        raise NotImplementedError

    def show(self) -> None:
        """Show the view.

        Creates the frame and widgets if not already created, packs the frame
        into the parent widget, and calls the on_show hook.
        """
        if self.frame is None:
            self.frame = Frame(self.parent, bg="white")
            self.create_widgets()

        self.frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.on_show()

    def hide(self) -> None:
        """Hide the view.

        Removes the frame from the parent widget and calls the on_hide hook.
        """
        if self.frame:
            self.frame.pack_forget()
        self.on_hide()

    def destroy(self) -> None:
        """Destroy the view and clean up resources.

        Destroys the frame and calls the on_destroy hook. Safe to call multiple times.
        """
        if self.frame:
            try:
                self.frame.destroy()
            except TclError:
                # Frame already destroyed, ignore
                pass
            finally:
                self.frame = None
        self.on_destroy()

    def on_show(self) -> None:
        """Called when the view is shown.

        This is a hook method that subclasses can override to perform
        custom initialization when the view becomes visible.
        """
        pass

    def on_hide(self) -> None:
        """Called when the view is hidden.

        This is a hook method that subclasses can override to perform
        cleanup when the view is hidden but not destroyed.
        """
        pass

    def on_destroy(self) -> None:
        """Called when the view is destroyed.

        This is a hook method that subclasses can override to perform
        final cleanup when the view is permanently destroyed.
        """
        pass
