"""UI constants for the application."""

from typing import Final, Literal

# Background colors
DEFAULT_BACKGROUND_COLOR: Final[str] = "white"

# Window configuration
WINDOW_WIDTH: Final[int] = 900
WINDOW_HEIGHT: Final[int] = 700

# Padding values
DEFAULT_FRAME_PADDING_X: Final[int] = 20
DEFAULT_FRAME_PADDING_Y: Final[int] = 20

# Typography - Fonts
TITLE_FONT: Final[tuple[str, int, str]] = ("Arial", 16, "bold")
STATUS_BAR_FONT: Final[tuple[str, int]] = ("Arial", 9)

# Button styling
BUTTON_WIDTH: Final[int] = 20

# Tkinter layout constants
# Pack side options
PACK_SIDE_LEFT: Final[Literal["left"]] = "left"

# Pack fill options
PACK_FILL_BOTH: Final[Literal["both"]] = "both"
PACK_FILL_X: Final[Literal["x"]] = "x"
PACK_FILL_Y: Final[Literal["y"]] = "y"

# Anchor options
ANCHOR_W: Final[Literal["w"]] = "w"

# Widget states
WIDGET_STATE_NORMAL: Final[Literal["normal"]] = "normal"
WIDGET_STATE_DISABLED: Final[Literal["disabled"]] = "disabled"

# Text wrap options
TEXT_WRAP_WORD: Final[Literal["word"]] = "word"

# Keyboard event constants
KEY_RETURN: Final[str] = "<Return>"
