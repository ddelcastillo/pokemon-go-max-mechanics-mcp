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

# Typography - Colors
TITLE_COLOR: Final[str] = "#1f4e79"
SUBTITLE_COLOR: Final[str] = "#666666"

# Button styling
BUTTON_WIDTH: Final[int] = 20
BUTTON_HEIGHT: Final[int] = 2

# Tkinter layout constants
# Pack side options
PACK_SIDE_LEFT: Final[Literal["left"]] = "left"
PACK_SIDE_RIGHT: Final[Literal["right"]] = "right"
PACK_SIDE_TOP: Final[Literal["top"]] = "top"
PACK_SIDE_BOTTOM: Final[Literal["bottom"]] = "bottom"

# Pack fill options
PACK_FILL_BOTH: Final[Literal["both"]] = "both"
PACK_FILL_X: Final[Literal["x"]] = "x"
PACK_FILL_Y: Final[Literal["y"]] = "y"
PACK_FILL_NONE: Final[Literal["none"]] = "none"

# Anchor options
ANCHOR_W: Final[Literal["w"]] = "w"
ANCHOR_E: Final[Literal["e"]] = "e"
ANCHOR_N: Final[Literal["n"]] = "n"
ANCHOR_S: Final[Literal["s"]] = "s"
ANCHOR_NW: Final[Literal["nw"]] = "nw"
ANCHOR_NE: Final[Literal["ne"]] = "ne"
ANCHOR_SW: Final[Literal["sw"]] = "sw"
ANCHOR_SE: Final[Literal["se"]] = "se"
ANCHOR_CENTER: Final[Literal["center"]] = "center"

# Widget states
WIDGET_STATE_NORMAL: Final[Literal["normal"]] = "normal"
WIDGET_STATE_DISABLED: Final[Literal["disabled"]] = "disabled"
WIDGET_STATE_ACTIVE: Final[Literal["active"]] = "active"

# Text wrap options
TEXT_WRAP_WORD: Final[Literal["word"]] = "word"
TEXT_WRAP_CHAR: Final[Literal["char"]] = "char"
TEXT_WRAP_NONE: Final[Literal["none"]] = "none"

# Keyboard event constants
KEY_RETURN: Final[str] = "<Return>"
KEY_ENTER: Final[str] = "<Enter>"
KEY_ESCAPE: Final[str] = "<Escape>"
KEY_TAB: Final[str] = "<Tab>"
KEY_BACKSPACE: Final[str] = "<BackSpace>"
KEY_DELETE: Final[str] = "<Delete>"
KEY_LEFT: Final[str] = "<Left>"
KEY_RIGHT: Final[str] = "<Right>"
KEY_UP: Final[str] = "<Up>"
KEY_DOWN: Final[str] = "<Down>"
