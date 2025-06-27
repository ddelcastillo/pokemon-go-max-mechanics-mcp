"""API infrastructure constants.

This module contains constants related to external API communication,
HTTP configuration, and other infrastructure concerns.
"""

from typing import Final

# Pokemon GO API Configuration
POKEMON_GO_API_BASE_URL: Final[str] = "https://pogoapi.net/api/v1"

# Pokemon Image API Configuration  
POKEMON_IMAGE_API_BASE_URL: Final[str] = "https://pokeapi.co/api/v2/pokemon"
POKEMON_SPRITE_BASE_URL: Final[str] = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"

# HTTP Configuration
DEFAULT_HTTP_TIMEOUT: Final[int] = 30
