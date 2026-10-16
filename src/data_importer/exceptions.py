"""Custom exceptions raised by the data importer."""


class ImporterError(Exception):
    """Base exception for expected importer failures."""


class FileFormatError(ImporterError):
    """Raised when a CSV file has an invalid format."""


class DuplicateUserError(ImporterError):
    """Raised when a user identifier already exists."""


class UserValidationError(ImporterError):
    """Raised when user data fails validation."""


class StorageError(ImporterError):
    """Raised when reading or writing the JSON repository fails."""
