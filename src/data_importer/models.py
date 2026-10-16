"""Data models used by the data importer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Represent a user imported from a CSV file.

    Attributes:
        user_id: Unique identifier assigned to the user.
        name: Full name of the user.
        email: Email address belonging to the user.
    """

    user_id: str
    name: str
    email: str
