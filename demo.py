"""Interactive demonstration of the Resilient Data Importer."""

import csv
import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from data_importer.exceptions import ImporterError
from data_importer.importer import import_users
from data_importer.repository import JsonUserRepository

logger = logging.getLogger(__name__)


def choose_csv_file(root: tk.Tk) -> Path | None:
    """Let the user browse for a CSV file."""
    selected = filedialog.askopenfilename(
        parent=root,
        title="Select the CSV file to import",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )

    if not selected:
        return None

    return Path(selected)


def choose_json_file(root: tk.Tk) -> Path | None:
    """Let the user choose where to save the JSON database."""
    selected = filedialog.asksaveasfilename(
        parent=root,
        title="Choose where to save the JSON database",
        initialdir=str(Path.cwd() / "data"),
        initialfile="demo_users.json",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
    )

    if not selected:
        return None

    return Path(selected)


def validate_csv_file(csv_path: Path) -> None:
    """Check the selected file before starting the import."""
    if not csv_path.exists():
        raise ValueError("The selected file does not exist.")

    if not csv_path.is_file():
        raise ValueError("The selected path is not a file.")

    if csv_path.suffix.lower() != ".csv":
        raise ValueError("Please select a file with a .csv extension.")

    if csv_path.stat().st_size == 0:
        raise ValueError("The selected CSV file is empty.")

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            headers = next(reader, None)

    except (OSError, UnicodeError, csv.Error) as error:
        raise ValueError(f"Could not read the CSV file: {error}") from error

    expected_headers = {"user_id", "name", "email"}

    if not headers:
        raise ValueError("The CSV file does not contain a header row.")

    actual_headers = {header.strip() for header in headers}

    if not expected_headers.issubset(actual_headers):
        raise ValueError(
            "The CSV must contain these headers: "
            "user_id, name, email.\n"
            f"Headers found: {headers}"
        )


def main() -> int:
    """Run the interactive import demonstration."""
    print("\n=== Resilient Data Importer ===")
    print("Import user records from CSV into a JSON database.\n")

    root = tk.Tk()
    root.withdraw()

    try:
        csv_path = choose_csv_file(root)

        if csv_path is None:
            print("No CSV file selected. Demo cancelled.")
            return 0

        print(f"Selected CSV: {csv_path}")

        try:
            validate_csv_file(csv_path)
        except ValueError as error:
            print(f"\nInvalid CSV file: {error}")
            return 1

        json_path = choose_json_file(root)

        if json_path is None:
            print("No output location selected. Demo cancelled.")
            return 0

        print(f"JSON output: {json_path}")

    finally:
        root.destroy()

    if csv_path.resolve() == json_path.resolve():
        print("\nError: Input and output files must be different.")
        return 1

    verbose = input("Enable verbose logging? [y/N]: ").strip().lower()

    logging.basicConfig(
        level=logging.DEBUG if verbose in {"y", "yes"} else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )

    try:
        repository = JsonUserRepository(json_path)
        count = import_users(csv_path, repository)

    except (ImporterError, OSError, UnicodeError) as error:
        print(f"\nImport failed: {error}")
        return 1

    print("\nImport completed successfully.")
    print(f"Users imported: {count}")
    print(f"Source file: {csv_path}")
    print(f"JSON database: {json_path}")

    try:
        with json_path.open("r", encoding="utf-8") as file:
            records = file.read()

        print("\nSaved JSON contents:")
        print(records)

    except (OSError, UnicodeError) as error:
        print(f"Import succeeded, but the JSON preview failed: {error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
