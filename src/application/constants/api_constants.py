"""API infrastructure constants.

This module contains constants related to external API communication,
HTTP configuration, and other infrastructure concerns.
"""

from typing import Final

# Pokemon GO API.
POKEMON_GO_API_BASE_URL: Final[str] = "https://pokemon-go-api.github.io/pokemon-go-api/api"

# Pokemon GO API keys.
POKEMON_IMAGE_KEY: Final[str] = "image"
POKEMON_SHINY_IMAGE_KEY: Final[str] = "shinyImage"
POKEMON_ASSETS_KEY: Final[str] = "assets"
POKEMON_ID_KEY: Final[str] = "id"

# HTTP Configuration.
DEFAULT_HTTP_TIMEOUT: Final[int] = 30
