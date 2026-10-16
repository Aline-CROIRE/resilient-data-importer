"""Tests for CSV parsing."""

import pytest

from data_importer.exceptions import (
    DuplicateUserError,
    FileFormatError,
    ImporterError,
)
from data_importer.parser import parse_csv


def test_parse_valid_csv(tmp_path):
    """Parse valid CSV records into users."""
    csv_file = tmp_path / "users.csv"
    csv_file.write_text(
        "user_id,name,email\nUSR001,Aline Niyonizera,aline@example.com\n",
        encoding="utf-8",
    )

    users = parse_csv(csv_file)

    assert len(users) == 1
    assert users[0].user_id == "USR001"
    assert users[0].name == "Aline Niyonizera"


@pytest.mark.parametrize(
    "content",
    [
        "",
        "user_id,name\nUSR001,Aline\n",
        "user_id,name,email\nUSR001,Aline\n",
        "user_id,name,email\nUSR001,Aline,aline@example.com,extra\n",
    ],
)
def test_invalid_csv_format(tmp_path, content):
    """Reject empty files, missing headers, and malformed rows."""
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(content, encoding="utf-8")

    with pytest.raises(FileFormatError):
        parse_csv(csv_file)


def test_duplicate_user_ids_are_rejected(tmp_path):
    """Reject duplicate IDs in the same CSV file."""
    csv_file = tmp_path / "duplicates.csv"
    csv_file.write_text(
        "user_id,name,email\n"
        "USR001,Aline,aline@example.com\n"
        "USR001,Jean,jean@example.com\n",
        encoding="utf-8",
    )

    with pytest.raises(DuplicateUserError):
        parse_csv(csv_file)


def test_missing_file_raises_importer_error(tmp_path):
    """Report a missing source file."""
    with pytest.raises(ImporterError, match="CSV file not found"):
        parse_csv(tmp_path / "missing.csv")


def test_invalid_email_is_rejected(tmp_path):
    """Reject a CSV row containing an invalid email."""
    from data_importer.exceptions import UserValidationError

    csv_file = tmp_path / "invalid-email.csv"
    csv_file.write_text(
        "user_id,name,email\nUSR001,Aline,not-an-email\n",
        encoding="utf-8",
    )

    with pytest.raises(UserValidationError):
        parse_csv(csv_file)


def test_duplicate_headers_are_rejected(tmp_path):
    """Reject a CSV containing repeated column names."""
    csv_file = tmp_path / "duplicate-headers.csv"
    csv_file.write_text(
        "user_id,name,email,email\n"
        "USR001,Aline,aline@example.com,other@example.com\n",
        encoding="utf-8",
    )

    with pytest.raises(FileFormatError):
        parse_csv(csv_file)
