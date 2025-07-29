import logging

from src.application.app import PokemonGoApp

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for the application."""
    app = PokemonGoApp()

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
