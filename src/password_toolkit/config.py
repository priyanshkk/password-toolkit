"""Configuration constants and environment-backed defaults.

Two optional environment variables are honoured:

* ``PASSWORD_LENGTH`` - default length used by ``generate`` and the CLI.
* ``PASSWORD_EXCLUDE_AMBIGUOUS`` - ``1`` excludes visually ambiguous characters.

Invalid values are ignored so a typo can never make the CLI unusable.
"""

from __future__ import annotations

import os

#: Characters that are easy to confuse in printed passwords.
AMBIGUOUS: frozenset[str] = frozenset("O0oIl1|`'\"")
#: Passwords that are capped at a deliberately low entropy estimate.
COMMON_PASSWORDS: frozenset[str] = frozenset(
    {
        "password",
        "password123",
        "12345678",
        "qwerty",
        "letmein",
        "admin123",
        "welcome1",
    }
)

DEFAULT_PASSWORD_LENGTH = 16
DEFAULT_EXCLUDE_AMBIGUOUS = False
PASSWORD_LENGTH_ENV = "PASSWORD_LENGTH"
EXCLUDE_AMBIGUOUS_ENV = "PASSWORD_EXCLUDE_AMBIGUOUS"


def get_default_length() -> int:
    """Return the configured default password length.

    The value comes from ``PASSWORD_LENGTH`` when it is a positive integer;
    otherwise :data:`DEFAULT_PASSWORD_LENGTH` is used.

    Returns:
        A positive password length.
    """
    raw = os.environ.get(PASSWORD_LENGTH_ENV)
    if raw is None:
        return DEFAULT_PASSWORD_LENGTH
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_PASSWORD_LENGTH
    return value if value > 0 else DEFAULT_PASSWORD_LENGTH


def get_exclude_ambiguous() -> bool:
    """Return whether ambiguous characters should be excluded by default.

    Only the exact value ``1`` (ignoring surrounding whitespace) enables the
    exclusion; any other value disables it.

    Returns:
        ``True`` when ``PASSWORD_EXCLUDE_AMBIGUOUS=1``, otherwise ``False``.
    """
    return os.environ.get(EXCLUDE_AMBIGUOUS_ENV, "0").strip() == "1"
