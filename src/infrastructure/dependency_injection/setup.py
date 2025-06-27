from injector import Injector

from src.infrastructure.dependency_injection.modules.http_client import HttpClientModule


def create_injector() -> Injector:
    """Create and configure the main injector instance.

    Returns:
        Configured injector instance with all modules.
    """
    return Injector(modules=[HttpClientModule()])


# Global injector instance
injector: Injector = create_injector()
