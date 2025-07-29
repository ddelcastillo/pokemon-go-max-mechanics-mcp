from injector import Injector

from src.application.services.web_image_processing import WebImageProcessingService
from src.domain.interfaces.image_processor import ImageProcessor
from src.infrastructure.dependency_injection.modules.http_client import HttpClientModule
from src.infrastructure.dependency_injection.modules.image_service import (
    ImageServiceModule,
)
from src.infrastructure.services.pil_image_processor import PILImageProcessor


def test_provide_image_processor_returns_pil_processor() -> None:
    """Test that the ImageServiceModule provides an instance of PILImageProcessor."""
    injector = Injector(modules=[ImageServiceModule()])
    processor = injector.get(ImageProcessor)  # type: ignore[type-abstract]
    assert isinstance(processor, PILImageProcessor)


def test_provide_web_image_processing_service_returns_service() -> None:
    """Test that the ImageServiceModule provides an instance of WebImageProcessingService."""
    # Include HttpClientModule to satisfy WebImageProcessingService dependencies
    injector = Injector(modules=[HttpClientModule(), ImageServiceModule()])
    service = injector.get(WebImageProcessingService)
    assert isinstance(service, WebImageProcessingService)


def test_image_processor_is_singleton() -> None:
    """Test that the ImageProcessor provides the same instance when requested multiple times."""
    injector = Injector(modules=[ImageServiceModule()])
    processor1 = injector.get(ImageProcessor)  # type: ignore[type-abstract]
    processor2 = injector.get(ImageProcessor)  # type: ignore[type-abstract]
    assert processor1 is processor2


def test_web_image_processing_service_is_singleton() -> None:
    """Test that the WebImageProcessingService provides the same instance when requested multiple times."""
    # Include HttpClientModule to satisfy WebImageProcessingService dependencies
    injector = Injector(modules=[HttpClientModule(), ImageServiceModule()])
    service1 = injector.get(WebImageProcessingService)
    service2 = injector.get(WebImageProcessingService)
    assert service1 is service2
