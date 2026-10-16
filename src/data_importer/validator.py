"""Validation rules for imported user records."""

import re

from data_importer.exceptions import UserValidationError
from data_importer.models import User

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_user(user: User) -> None:
    """Validate the required fields of a user.

    Args:
        user: The user record to validate.

    Raises:
        UserValidationError: If a required field is empty or
            the email address has an invalid format.
    """
    if not user.user_id.strip():
        raise UserValidationError("User ID cannot be empty.")

    if not user.name.strip():
        raise UserValidationError(
            f"Name cannot be empty for user ID {user.user_id!r}."
        )

    if not user.email.strip():
        raise UserValidationError(
            f"Email cannot be empty for user ID {user.user_id!r}."
        )

    if not EMAIL_PATTERN.fullmatch(user.email.strip()):
        raise UserValidationError(
            f"Invalid email address for user ID {user.user_id!r}."
        )
