
"""Tests for the import service."""

from pathlib import Path

import pytest

from data_importer.exceptions import (
    DuplicateUserError,
    ImporterError,
)
from data_importer.importer import import_users
from data_importer.models import User


@pytest.fixture
def csv_path(tmp_path):
    """Return a path for a sample CSV file."""
    return tmp_path / "users.csv"


@pytest.fixture
def sample_users():
    """Provide representative user records."""
    return [
        User("USR001", "Aline", "aline@example.com"),
        User("USR002", "Jean", "jean@example.com"),
    ]


def test_import_users_success(mocker, csv_path, sample_users):
    """Parse and persist users successfully."""
    mock_parse = mocker.patch(
        "data_importer.importer.parse_csv",
        return_value=sample_users,
    )
    repository = mocker.Mock()
    repository.add_users.return_value = 2

    result = import_users(csv_path, repository)

    assert result == 2
    mock_parse.assert_called_once_with(csv_path)
    repository.add_users.assert_called_once_with(sample_users)


def test_import_users_propagates_parser_error(mocker, csv_path):
    """Do not write records when parsing fails."""
    mocker.patch(
        "data_importer.importer.parse_csv",
        side_effect=ImporterError("Invalid CSV"),
    )
    repository = mocker.Mock()

    with pytest.raises(ImporterError, match="Invalid CSV"):
        import_users(csv_path, repository)

    repository.add_users.assert_not_called()


def test_import_users_propagates_duplicate_error(
    mocker, csv_path, sample_users
):
    """Propagate duplicate errors from the repository."""
    mocker.patch(
        "data_importer.importer.parse_csv",
        return_value=sample_users,
    )
    repository = mocker.Mock()
    repository.add_users.side_effect = DuplicateUserError("Duplicate ID")

    with pytest.raises(DuplicateUserError, match="Duplicate ID"):
        import_users(csv_path, repository)


def test_import_users_accepts_empty_csv_result(mocker, csv_path):
    """Allow a valid CSV with headers but no user records."""
    mocker.patch(
        "data_importer.importer.parse_csv",
        return_value=[],
    )
    repository = mocker.Mock()
    repository.add_users.return_value = 0

    assert import_users(csv_path, repository) == 0
    repository.add_users.assert_called_once_with([])


def test_import_users_end_to_end(tmp_path):
    """Import CSV records into a real temporary JSON database."""
    from data_importer.repository import JsonUserRepository

    csv_path = tmp_path / "users.csv"
    database_path = tmp_path / "users.json"

    csv_path.write_text(
        "user_id,name,email\n"
        "USR001,Aline,aline@example.com\n"
        "USR002,Jean,jean@example.com\n",
        encoding="utf-8",
    )

    repository = JsonUserRepository(database_path)

    count = import_users(csv_path, repository)

    assert count == 2
    assert [user.user_id for user in repository.get_all()] == [
        "USR001",
        "USR002",
    ]
