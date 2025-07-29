from __future__ import annotations

from typing import TYPE_CHECKING

from injector import Module, singleton

from src.application.services.web_image_processing import WebImageProcessingService
from src.domain.interfaces.image_processor import ImageProcessor
from src.infrastructure.services.pil_image_processor import PILImageProcessor

if TYPE_CHECKING:
    from injector import Binder


class ImageServiceModule(Module):
    """Module for configuring image service dependencies."""

    def configure(self, binder: Binder) -> None:
        """Configure image service bindings.

        Args:
            binder: The injector binder for setting up dependencies.
        """
        binder.bind(ImageProcessor, to=PILImageProcessor, scope=singleton)  # type: ignore[type-abstract]
        # Bind to itself so the injector manages and injects a singleton instance when ImageService is required.
        binder.bind(WebImageProcessingService, to=WebImageProcessingService, scope=singleton)
