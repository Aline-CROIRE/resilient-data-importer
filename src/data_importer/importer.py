"""Coordinate CSV parsing and user persistence."""

import logging
from pathlib import Path

from data_importer.exceptions import ImporterError
from data_importer.parser import parse_csv
from data_importer.repository import JsonUserRepository

logger = logging.getLogger(__name__)


def import_users(
    csv_path: Path,
    repository: JsonUserRepository,
) -> int:
    """Import users from a CSV file into the JSON repository.

    Args:
        csv_path: Path to the source CSV file.
        repository: Repository used to store users.

    Returns:
        Number of users successfully imported.

    Raises:
        ImporterError: If parsing, validation, or storage fails.
    """
    try:
        users = parse_csv(csv_path)
        imported_count = repository.add_users(users)

    except ImporterError:
        logger.exception("Import failed for %s", csv_path)
        raise
    else:
        logger.info(
            "Import completed successfully: %d users from %s",
            imported_count,
            csv_path,
        )
        return imported_count
    finally:
        logger.debug("Import attempt finished for %s", csv_path)
