# Resilient Data Importer CLI

A Python command-line application for importing user records from CSV files into a JSON database. It validates input data, detects invalid records and duplicate user IDs, and provides clear error handling and logging.

## Features

- Import user records from CSV into JSON.
- Validate CSV structure and required fields.
- Detect duplicate user IDs and invalid email addresses.
- Handle malformed input and import errors.
- Use custom exceptions for clear error reporting.
- Separate parsing, validation, importing, and data persistence.
- Include automated tests and code-quality checks.

## Requirements

- Python 3.11 or newer
- pip
- Git

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/Aline-CROIRE/resilient-data-importer.git
cd resilient-data-importer
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Usage

The following examples assume the CLI uses the `import` command with `--input` and `--database` options.

### Import sample data

```powershell
data-importer import --input data/users.csv --database data/users.json
```

### Enable verbose logging

```powershell
data-importer import --input data/users.csv --database data/users.json --verbose
```

### View help

```powershell
data-importer --help
data-importer import --help
```

## Input Format

The CSV input contains user records with the following fields:

```csv
user_id,name,email
USR001,Aline,aline@example.com
USR002,Jean,jean@example.com
```

Input records are checked for required values, valid email addresses, duplicate IDs, and CSV structure errors.

## Project Structure

```text
resilient-data-importer/
├── data/
│   ├── users.csv
│   └── users.json
├── src/
│   └── data_importer/
│       ├── __init__.py
│       ├── cli.py
│       ├── exceptions.py
│       ├── importer.py
│       ├── models.py
│       ├── parser.py
│       ├── repository.py
│       └── validator.py
├── tests/
│   ├── test_cli.py
│   ├── test_importer.py
│   ├── test_parser.py
│   ├── test_repository.py
│   └── test_validator.py
├── .coveragerc
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Testing

Run the test suite:

```powershell
python -m pytest -v
```

Run tests with coverage:

```powershell
python -m coverage erase
python -m coverage run -m pytest
python -m coverage report -m
```

Generate an HTML coverage report:

```powershell
python -m coverage html
Start-Process .\htmlcov\index.html
```

The last recorded verification reported **34 passing tests and 91% overall test coverage**. Run the tests again to verify the current state.

## Code Quality

Run the configured code-quality checks:

```powershell
python -m black --check src tests
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/data_importer
python -m pre_commit run --all-files
git diff --check
```

Install the pre-commit hooks:

```powershell
python -m pre_commit install
```

## Error Handling and Logging

The application uses custom exceptions to communicate import and validation failures. Logging helps track import operations and diagnose errors. Verbose logging can be enabled when more detailed output is needed.

## Design

The project follows a modular Python structure. CSV parsing, data validation, import coordination, JSON persistence, and command-line handling are separated into individual modules to improve maintainability and testability.

## License

No license has been specified for this repository yet.
