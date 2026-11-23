"""Tests for generation, strength estimation and configuration."""

from __future__ import annotations

import string
import sys
import unittest
from pathlib import Path
from unittest import mock

# Plain `unittest discover -s tests` uses tests/ as its top-level directory and
# does not import tests/__init__.py, so ensure src/ is importable here too.
SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from password_toolkit import AMBIGUOUS, estimate_strength, generate  # noqa: E402
from password_toolkit.config import (  # noqa: E402
    DEFAULT_PASSWORD_LENGTH,
    get_default_length,
    get_exclude_ambiguous,
)


class PasswordToolkitTests(unittest.TestCase):
    """Behavioural tests preserved from the original single-file module."""

    def test_requested_length(self) -> None:
        """The requested length is honoured."""
        self.assertEqual(len(generate(24)), 24)

    def test_every_enabled_class_is_represented(self) -> None:
        """Each enabled class appears in every generated password."""
        for _ in range(100):
            password = generate(20)
            self.assertTrue(any(c in string.ascii_lowercase for c in password))
            self.assertTrue(any(c in string.ascii_uppercase for c in password))
            self.assertTrue(any(c in string.digits for c in password))
            self.assertTrue(any(c in string.punctuation for c in password))

    def test_exclude_ambiguous_characters(self) -> None:
        """Ambiguous characters are absent when excluded."""
        password = generate(40, exclude_ambiguous=True)
        self.assertFalse(any(c in AMBIGUOUS for c in password))

    def test_respects_disabled_classes(self) -> None:
        """Disabled classes never contribute characters."""
        password = generate(30, use_digits=False, use_symbols=False)
        self.assertTrue(all(c.isalpha() for c in password))

    def test_rejects_impossible_requests(self) -> None:
        """Too few classes or too short a length raise ``ValueError``."""
        with self.assertRaises(ValueError):
            generate(8, use_upper=False, use_lower=False, use_digits=False, use_symbols=False)
        # Four enabled classes still require at least four characters.
        with self.assertRaises(ValueError):
            generate(2)

    def test_strength_scale(self) -> None:
        """Weak and strong passwords land in the expected bands."""
        self.assertEqual(estimate_strength("abc")[0], "weak")
        self.assertIn(estimate_strength("Tr0ub4dor&3xKq")[0], ("good", "strong"))

    def test_common_password_is_capped_as_weak(self) -> None:
        """Known common passwords are capped at 10 bits."""
        label, bits = estimate_strength("Password123")
        self.assertEqual(label, "weak")
        self.assertLessEqual(bits, 10)


class ConfigTests(unittest.TestCase):
    """Tests for genuine environment-variable support."""

    def test_password_length_environment_variable(self) -> None:
        """``PASSWORD_LENGTH`` changes the default length."""
        with mock.patch.dict("os.environ", {"PASSWORD_LENGTH": "12"}):
            self.assertEqual(get_default_length(), 12)
            self.assertEqual(len(generate()), 12)

    def test_exclude_ambiguous_environment_variable(self) -> None:
        """``PASSWORD_EXCLUDE_AMBIGUOUS=1`` changes the default."""
        with mock.patch.dict("os.environ", {"PASSWORD_EXCLUDE_AMBIGUOUS": "1"}):
            self.assertTrue(get_exclude_ambiguous())
            self.assertFalse(any(c in AMBIGUOUS for c in generate(40)))

    def test_invalid_environment_values_fall_back(self) -> None:
        """Invalid values fall back to documented defaults."""
        with mock.patch.dict(
            "os.environ",
            {"PASSWORD_LENGTH": "nope", "PASSWORD_EXCLUDE_AMBIGUOUS": "yes"},
        ):
            self.assertEqual(get_default_length(), DEFAULT_PASSWORD_LENGTH)
            self.assertFalse(get_exclude_ambiguous())


if __name__ == "__main__":
    unittest.main()
