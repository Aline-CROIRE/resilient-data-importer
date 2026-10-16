"""Tests for the JSON user repository."""

import json

import pytest

from data_importer.exceptions import DuplicateUserError, StorageError
from data_importer.models import User
from data_importer.repository import JsonUserRepository


@pytest.fixture
def repository(tmp_path):
    """Provide a repository backed by a temporary JSON file."""
    return JsonUserRepository(tmp_path / "users.json")


def test_missing_database_returns_empty_list(repository):
    """A missing database represents an empty collection."""
    assert repository.get_all() == []


def test_save_and_load_users(repository):
    """Persist users and load them back."""
    users = [User("USR001", "Aline", "aline@example.com")]

    repository.save_all(users)

    assert repository.get_all() == users


def test_add_users_preserves_existing_records(repository):
    """Adding a user preserves previously stored records."""
    first = User("USR001", "Aline", "aline@example.com")
    second = User("USR002", "Jean", "jean@example.com")

    repository.add_users([first])
    count = repository.add_users([second])

    assert count == 1
    assert repository.get_all() == [first, second]


def test_existing_duplicate_is_rejected(repository):
    """Reject an ID already present in the database."""
    user = User("USR001", "Aline", "aline@example.com")
    repository.add_users([user])

    with pytest.raises(DuplicateUserError):
        repository.add_users([user])

    assert repository.get_all() == [user]


def test_duplicate_within_batch_is_rejected(repository):
    """Reject repeated IDs before persisting the batch."""
    first = User("USR001", "Aline", "aline@example.com")
    second = User("USR001", "Jean", "jean@example.com")

    with pytest.raises(DuplicateUserError):
        repository.add_users([first, second])

    assert repository.get_all() == []


def test_invalid_json_raises_storage_error(repository):
    """Reject malformed JSON."""
    repository._file_path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(StorageError):
        repository.get_all()


def test_saved_json_is_valid(repository):
    """Ensure the saved database has the expected JSON structure."""
    user = User("USR001", "Aline", "aline@example.com")

    repository.save_all([user])

    records = json.loads(repository._file_path.read_text(encoding="utf-8"))

    assert records == [
        {
            "user_id": "USR001",
            "name": "Aline",
            "email": "aline@example.com",
        }
    ]


def test_save_all_wraps_directory_creation_error(repository, mocker):
    """Convert directory creation failures into StorageError."""
    mocker.patch.object(
        type(repository._file_path.parent),
        "mkdir",
        side_effect=PermissionError("Permission denied"),
    )

    with pytest.raises(
        StorageError,
        match="Unable to write JSON database",
    ):
        repository.save_all([])
