"""Tests for user validation."""

import pytest

from data_importer.exceptions import UserValidationError
from data_importer.models import User
from data_importer.validator import validate_user


@pytest.mark.parametrize(
    "user",
    [
        User("", "Aline", "aline@example.com"),
        User("USR001", " ", "aline@example.com"),
        User("USR001", "Aline", ""),
        User("USR001", "Aline", "not-an-email"),
        User("USR001", "Aline", "missing-domain@"),
        User("USR001", "Aline", "has spaces@example.com"),
    ],
)
def test_invalid_users_are_rejected(user):
    """Reject missing required values and malformed email addresses."""
    with pytest.raises(UserValidationError):
        validate_user(user)


@pytest.mark.parametrize(
    "email",
    [
        "aline@example.com",
        "jean.doe@company.org",
        "student+lab@example.co.rw",
    ],
)
def test_valid_email_formats_are_accepted(email):
    """Accept common email address formats."""
    validate_user(User("USR001", "Aline", email))


def test_email_with_surrounding_whitespace_is_accepted():
    """Validate the trimmed email value."""
    validate_user(User("USR001", "Aline", " aline@example.com "))
