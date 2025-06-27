"""Main entry point for the Pokémon Go Max Mechanics application."""

from src.application.app import PokemonGoApp


def main() -> None:
    """Entry point for the application."""
    app = PokemonGoApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted by user.")
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
