"""
Exception hierarchy for TGPC system.

This module defines all custom exceptions used throughout the TGPC system
with proper inheritance and error handling capabilities.
"""

from typing import Any, Dict, Optional


class TGPCException(Exception):
    """
    Base exception for all TGPC-related errors.

    This is the root exception class that all other TGPC exceptions
    inherit from. It provides common functionality for error handling
    and logging.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize TGPC exception.

        Args:
            message: Human-readable error message.
            error_code: Optional error code for programmatic handling.
            context: Optional context information about the error.
            cause: Optional underlying exception that caused this error.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None
        }

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class NetworkException(TGPCException):
    """
    Exception for network-related errors.

    Raised when there are issues with HTTP requests, connectivity,
    or server responses during data extraction.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize network exception.

        Args:
            message: Error message.
            status_code: HTTP status code if applicable.
            url: URL that caused the error if applicable.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if status_code:
            context['status_code'] = status_code
        if url:
            context['url'] = url

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.status_code = status_code
        self.url = url


class DataValidationException(TGPCException):
    """
    Exception for data validation errors.

    Raised when data doesn't meet validation criteria or
    contains invalid formats or values.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize data validation exception.

        Args:
            message: Error message.
            field_name: Name of the field that failed validation.
            field_value: Value that failed validation.
            validation_rule: Description of the validation rule that failed.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = str(field_value)
        if validation_rule:
            context['validation_rule'] = validation_rule

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule


class ConfigurationException(TGPCException):
    """
    Exception for configuration-related errors.

    Raised when there are issues with system configuration,
    missing required settings, or invalid configuration values.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize configuration exception.

        Args:
            message: Error message.
            config_key: Configuration key that caused the error.
            config_value: Configuration value that caused the error.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if config_key:
            context['config_key'] = config_key
        if config_value is not None:
            context['config_value'] = str(config_value)

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.config_key = config_key
        self.config_value = config_value


class StorageException(TGPCException):
    """
    Exception for storage and file operation errors.

    Raised when there are issues with file I/O, backup operations,
    or data persistence.
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize storage exception.

        Args:
            message: Error message.
            file_path: File path that caused the error.
            operation: Storage operation that failed.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if file_path:
            context['file_path'] = file_path
        if operation:
            context['operation'] = operation

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.file_path = file_path
        self.operation = operation


class RateLimitException(NetworkException):
    """
    Exception for rate limiting errors.

    Raised when requests are being rate limited or blocked
    by the target server.
    """

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize rate limit exception.

        Args:
            message: Error message.
            retry_after: Seconds to wait before retrying.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if retry_after:
            context['retry_after'] = retry_after

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.retry_after = retry_after


class AuthenticationException(TGPCException):
    """
    Exception for authentication and authorization errors.

    Raised when there are issues with credentials, permissions,
    or access control.
    """

    def __init__(
        self,
        message: str,
        auth_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize authentication exception.

        Args:
            message: Error message.
            auth_type: Type of authentication that failed.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if auth_type:
            context['auth_type'] = auth_type

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.auth_type = auth_type


class ParsingException(DataValidationException):
    """
    Exception for data parsing errors.

    Raised when there are issues parsing HTML, JSON, or other
    data formats during extraction.
    """

    def __init__(
        self,
        message: str,
        data_format: Optional[str] = None,
        parse_location: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize parsing exception.

        Args:
            message: Error message.
            data_format: Format of data being parsed (html, json, etc.).
            parse_location: Location in data where parsing failed.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if data_format:
            context['data_format'] = data_format
        if parse_location:
            context['parse_location'] = parse_location

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.data_format = data_format
        self.parse_location = parse_location


class ExtractionException(TGPCException):
    """
    Exception for data extraction errors.

    Raised when there are issues during the data extraction process
    that don't fit into other specific categories.
    """

    def __init__(
        self,
        message: str,
        extraction_type: Optional[str] = None,
        registration_number: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize extraction exception.

        Args:
            message: Error message.
            extraction_type: Type of extraction (basic, detailed, etc.).
            registration_number: Registration number being processed.
            **kwargs: Additional arguments for base exception.
        """
        context = kwargs.get('context', {})
        if extraction_type:
            context['extraction_type'] = extraction_type
        if registration_number:
            context['registration_number'] = registration_number

        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.extraction_type = extraction_type
        self.registration_number = registration_number


class ValidationError(DataValidationException):
    """
    Alias for DataValidationException for backward compatibility.
    """
    pass


# Exception mapping for HTTP status codes
HTTP_EXCEPTION_MAP = {
    400: DataValidationException,
    401: AuthenticationException,
    403: AuthenticationException,
    404: NetworkException,
    429: RateLimitException,
    500: NetworkException,
    502: NetworkException,
    503: NetworkException,
    504: NetworkException,
}


def create_http_exception(
    status_code: int,
    message: str,
    url: Optional[str] = None,
    **kwargs
) -> NetworkException:
    """
    Create appropriate exception based on HTTP status code.

    Args:
        status_code: HTTP status code.
        message: Error message.
        url: URL that caused the error.
        **kwargs: Additional arguments for exception.

    Returns:
        Appropriate exception instance based on status code.
    """
    exception_class = HTTP_EXCEPTION_MAP.get(status_code, NetworkException)

    return exception_class(
        message=message,
        status_code=status_code,
        url=url,
        error_code=f"HTTP_{status_code}",
        **kwargs
    )


def handle_exception_chain(exception: Exception) -> TGPCException:
    """
    Convert a generic exception to appropriate TGPC exception.

    Args:
        exception: Original exception to convert.

    Returns:
        TGPC exception with original exception as cause.
    """
    if isinstance(exception, TGPCException):
        return exception

    # Map common exception types
    if isinstance(exception, (ConnectionError, TimeoutError)):
        return NetworkException(
            message=f"Network error: {str(exception)}",
            error_code="NETWORK_ERROR",
            cause=exception
        )
    elif isinstance(exception, ValueError):
        return DataValidationException(
            message=f"Data validation error: {str(exception)}",
            error_code="VALIDATION_ERROR",
            cause=exception
        )
    elif isinstance(exception, (FileNotFoundError, PermissionError, OSError)):
        return StorageException(
            message=f"Storage error: {str(exception)}",
            error_code="STORAGE_ERROR",
            cause=exception
        )
    else:
        # Generic TGPC exception for unknown errors
        return TGPCException(
            message=f"Unexpected error: {str(exception)}",
            error_code="UNKNOWN_ERROR",
            cause=exception
        )


class ExceptionHandler:
    """
    Centralized exception handler for consistent error processing.

    This class provides methods for handling, logging, and converting
    exceptions throughout the TGPC system.
    """

    def __init__(self, logger=None):
        """
        Initialize exception handler.

        Args:
            logger: Optional logger instance for error logging.
        """
        self.logger = logger

    def handle_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = True
    ) -> Optional[TGPCException]:
        """
        Handle an exception with logging and conversion.

        Args:
            exception: Exception to handle.
            context: Additional context information.
            reraise: Whether to reraise the exception after handling.

        Returns:
            TGPC exception if not reraising, None otherwise.

        Raises:
            TGPCException: If reraise is True.
        """
        # Convert to TGPC exception
        tgpc_exception = handle_exception_chain(exception)

        # Add context if provided
        if context:
            tgpc_exception.context.update(context)

        # Log the exception
        if self.logger:
            self.logger.error(
                f"Exception handled: {tgpc_exception.message}",
                extra=tgpc_exception.to_dict()
            )

        if reraise:
            raise tgpc_exception
        else:
            return tgpc_exception

    def log_exception(
        self,
        exception: Exception,
        level: str = "error",
        extra_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an exception without handling it.

        Args:
            exception: Exception to log.
            level: Log level (debug, info, warning, error, critical).
            extra_context: Additional context to include in log.
        """
        if not self.logger:
            return

        tgpc_exception = handle_exception_chain(exception)

        if extra_context:
            tgpc_exception.context.update(extra_context)

        log_method = getattr(self.logger, level.lower(), self.logger.error)
        log_method(
            f"Exception logged: {tgpc_exception.message}",
            extra=tgpc_exception.to_dict()
        )
