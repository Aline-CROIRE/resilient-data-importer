
"""CSV parsing for user data imports."""

import csv
import logging
from pathlib import Path

from data_importer.exceptions import (
    DuplicateUserError,
    FileFormatError,
    ImporterError,
)
from data_importer.models import User
from data_importer.validator import validate_user

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"user_id", "name", "email"}


def parse_csv(file_path: Path) -> list[User]:
    """Read, validate, and parse users from a CSV file.

    Args:
        file_path: Path to the source CSV file.

    Returns:
        A list of validated User objects.

    Raises:
        ImporterError: If the file cannot be read.
        FileFormatError: If the CSV structure is invalid.
        DuplicateUserError: If an ID occurs more than once.
        UserValidationError: If a user's data is invalid.
    """
    users: list[User] = []
    seen_ids: set[str] = set()

    try:
        with file_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                raise FileFormatError("The CSV file is empty or has no header.")

            reader.fieldnames = [
                field.strip() for field in reader.fieldnames
            ]

            if (
                len(reader.fieldnames) != len(set(reader.fieldnames))
                or set(reader.fieldnames) != REQUIRED_COLUMNS
            ):
                raise FileFormatError(
                    "CSV headers must contain exactly: "
                    "user_id, name, email."
                )

            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise FileFormatError(
                        f"Unexpected extra column at row {row_number}."
                    )

                if any(value is None for value in row.values()):
                    raise FileFormatError(
                        f"Missing column value at row {row_number}."
                    )

                if not any(value.strip() for value in row.values()):
                    raise FileFormatError(
                        f"Blank record at row {row_number}."
                    )

                user = User(
                    user_id=row["user_id"].strip(),
                    name=row["name"].strip(),
                    email=row["email"].strip(),
                )

                validate_user(user)

                if user.user_id in seen_ids:
                    raise DuplicateUserError(
                        f"Duplicate user ID {user.user_id!r} "
                        f"at row {row_number}."
                    )

                seen_ids.add(user.user_id)
                users.append(user)

    except (FileFormatError, DuplicateUserError, ImporterError):
        logger.warning("CSV import parsing failed: %s", file_path)
        raise
    except FileNotFoundError as error:
        logger.error("CSV file not found: %s", file_path)
        raise ImporterError(
            f"CSV file not found: {file_path}"
        ) from error
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        logger.exception("Unable to read CSV file: %s", file_path)
        raise ImporterError(
            f"Unable to read CSV file: {file_path}"
        ) from error
    else:
        logger.info("Parsed %d users from %s", len(users), file_path)
        return users
    finally:
        logger.debug("Finished attempting to parse %s", file_path)
