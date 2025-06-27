from src.domain.errors.base import DomainError


class HttpClientError(DomainError):
    """Exception raised when HTTP client operations fail.

    This exception is raised when HTTP requests fail due to network issues,
    server errors, or invalid responses.
    """

    def __init__(self, *, message: str, status_code: int | None = None) -> None:
        """Initialize the HttpClientError.

        Args:
            message: Error message describing what went wrong.
            status_code: Optional HTTP status code if available.
        """
        super().__init__(message)
        self.status_code = status_code
