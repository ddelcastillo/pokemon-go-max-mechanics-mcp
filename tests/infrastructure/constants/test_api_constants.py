"""Tests for API constants."""

from src.infrastructure.constants.api_constants import (
    DEFAULT_HTTP_TIMEOUT,
    POKEMON_GO_API_BASE_URL,
)


class TestApiConstants:
    """Test suite for API constants."""

    def test_pokemon_go_api_base_url_is_defined(self) -> None:
        """Test that the Pokémon GO API base URL is properly defined."""
        assert POKEMON_GO_API_BASE_URL == "https://pokemon-go-api.github.io/pokemon-go-api/api"
        assert isinstance(POKEMON_GO_API_BASE_URL, str)
        assert POKEMON_GO_API_BASE_URL.startswith("https://")

    def test_default_http_timeout_is_defined(self) -> None:
        """Test that the default HTTP timeout is properly defined."""
        assert DEFAULT_HTTP_TIMEOUT == 30
        assert isinstance(DEFAULT_HTTP_TIMEOUT, int)
        assert DEFAULT_HTTP_TIMEOUT > 0
