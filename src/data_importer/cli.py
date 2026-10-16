"""Command-line interface for the resilient data importer."""

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from data_importer.exceptions import ImporterError
from data_importer.importer import import_users
from data_importer.repository import JsonUserRepository


def configure_logging(verbose: bool = False) -> None:
    """Configure application logging.

    Args:
        verbose: Whether to enable debug-level logging.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="data-importer",
        description="Import validated user records from CSV into JSON.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    import_parser = subparsers.add_parser(
        "import",
        help="Import users from a CSV file.",
    )
    import_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the source CSV file.",
    )
    import_parser.add_argument(
        "--database",
        type=Path,
        required=True,
        help="Path to the JSON database.",
    )
    import_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI application.

    Args:
        argv: Optional command-line arguments for testing.

    Returns:
        Zero on success, one on an import failure.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.verbose)
    logger = logging.getLogger(__name__)

    if args.command == "import":
        repository = JsonUserRepository(args.database)

        try:
            count = import_users(args.input, repository)
        except ImporterError as error:
            print(f"Import failed: {error}")
            return 1

        print(f"Import successful: {count} user(s) imported.")
        logger.info("CLI import completed successfully.")
        return 0

    parser.error("Unsupported command.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
