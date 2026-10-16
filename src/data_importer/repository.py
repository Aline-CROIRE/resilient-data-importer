"""JSON-backed storage for imported users."""

import json
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from data_importer.exceptions import DuplicateUserError, StorageError
from data_importer.models import User

logger = logging.getLogger(__name__)


class JsonUserRepository:
    """Store users in a JSON file."""

    def __init__(self, file_path: Path) -> None:
        """Initialize the repository.

        Args:
            file_path: Path to the JSON database.
        """
        self._file_path = file_path

    def get_all(self) -> list[User]:
        """Return all users currently stored.

        Returns:
            The stored users, or an empty list if the file does not exist.

        Raises:
            StorageError: If the database cannot be read or is invalid.
        """
        if not self._file_path.exists():
            return []

        try:
            with self._file_path.open("r", encoding="utf-8") as database_file:
                records = json.load(database_file)

            if not isinstance(records, list):
                raise StorageError("The JSON database must contain a list.")

            users: list[User] = []

            for record in records:
                if not isinstance(record, dict):
                    raise StorageError("A database record is not an object.")

                try:
                    users.append(
                        User(
                            user_id=record["user_id"],
                            name=record["name"],
                            email=record["email"],
                        )
                    )
                except (KeyError, TypeError) as error:
                    raise StorageError(
                        "A database record has an invalid structure."
                    ) from error

            return users

        except StorageError:
            raise
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise StorageError(
                f"Unable to read JSON database: {self._file_path}"
            ) from error

    def save_all(self, users: list[User]) -> None:
        """Atomically replace the stored user records.

        Args:
            users: Complete collection of users to persist.

        Raises:
            StorageError: If writing the database fails.
        """
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None

        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self._file_path.parent,
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                json.dump(
                    [
                        {
                            "user_id": user.user_id,
                            "name": user.name,
                            "email": user.email,
                        }
                        for user in users
                    ],
                    temporary_file,
                    indent=2,
                )
                temporary_file.write("\n")

            os.replace(temporary_path, self._file_path)
            logger.info("Saved %d users", len(users))

        except (OSError, TypeError, ValueError) as error:
            raise StorageError(
                f"Unable to write JSON database: {self._file_path}"
            ) from error
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def add_users(self, new_users: list[User]) -> int:
        """Add users while rejecting duplicate IDs.

        Args:
            new_users: Users to add to the database.

        Returns:
            The number of users added.

        Raises:
            DuplicateUserError: If an ID already exists or repeats in
                the incoming batch.
            StorageError: If the existing database cannot be read or saved.
        """
        existing_users = self.get_all()
        existing_ids = {user.user_id for user in existing_users}
        incoming_ids: set[str] = set()

        for user in new_users:
            if user.user_id in existing_ids or user.user_id in incoming_ids:
                raise DuplicateUserError(
                    f"User ID {user.user_id!r} already exists."
                )

            incoming_ids.add(user.user_id)

        self.save_all(existing_users + new_users)
        return len(new_users)
