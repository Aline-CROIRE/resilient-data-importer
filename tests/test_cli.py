"""Tests for the command-line interface."""

from data_importer.cli import main


def test_import_command_succeeds(mocker, capsys, tmp_path):
    """Display a success message when the import succeeds."""
    mock_import = mocker.patch(
        "data_importer.cli.import_users",
        return_value=3,
    )

    result = main(
        [
            "import",
            "--input",
            str(tmp_path / "users.csv"),
            "--database",
            str(tmp_path / "users.json"),
        ]
    )

    output = capsys.readouterr()

    assert result == 0
    assert "3 user(s) imported" in output.out
    mock_import.assert_called_once()


def test_import_command_handles_failure(mocker, capsys, tmp_path):
    """Display an error and return a nonzero exit code."""
    from data_importer.exceptions import ImporterError

    mocker.patch(
        "data_importer.cli.import_users",
        side_effect=ImporterError("CSV file not found"),
    )

    result = main(
        [
            "import",
            "--input",
            str(tmp_path / "missing.csv"),
            "--database",
            str(tmp_path / "users.json"),
        ]
    )

    output = capsys.readouterr()

    assert result == 1
    assert "Import failed:" in output.out
    assert "CSV file not found" in output.out


def test_import_command_requires_arguments():
    """Reject a command missing its required options."""
    import pytest

    with pytest.raises(SystemExit) as error:
        main(["import"])

    assert error.value.code == 2
