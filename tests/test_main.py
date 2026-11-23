"""CLI tests for ``python -m password_toolkit`` behaviour."""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

# Plain `unittest discover -s tests` uses tests/ as its top-level directory and
# does not import tests/__init__.py, so ensure src/ is importable here too.
SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from password_toolkit import AMBIGUOUS, build_parser, main  # noqa: E402


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    """Run the CLI and capture its output.

    Args:
        argv: Arguments to pass to ``main``.

    Returns:
        A tuple of exit code, stdout and stderr.
    """
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    """Tests for the command-line interface."""

    def test_generate_prints_password_and_estimate(self) -> None:
        """``generate`` prints a password followed by its estimate."""
        code, out, err = run_cli(["generate", "--length", "24"])
        self.assertEqual((code, err), (0, ""))
        line = out.strip()
        password = line.split("  [")[0]
        self.assertEqual(len(password), 24)
        self.assertIn("bits]", line)

    def test_generate_count_prints_one_line_each(self) -> None:
        """``--count`` produces one line per password."""
        code, out, _ = run_cli(["generate", "--length", "20", "--count", "3"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 3)

    def test_length_two_with_four_classes_fails(self) -> None:
        """A length of two with four classes reports a validation error."""
        code, out, err = run_cli(["generate", "--length", "2"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Length must be at least 4", err)

    def test_check_prints_strength(self) -> None:
        """``check`` reports a strength label."""
        code, out, _ = run_cli(["check", "Tr0ub4dor&3xKq"])
        self.assertEqual(code, 0)
        self.assertIn("Strength:", out)
        self.assertIn("bits of entropy", out)

    def test_environment_defaults_are_used_by_cli(self) -> None:
        """Both environment variables affect a bare ``generate`` call."""
        env = {"PASSWORD_LENGTH": "10", "PASSWORD_EXCLUDE_AMBIGUOUS": "1"}
        with mock.patch.dict("os.environ", env):
            code, out, _ = run_cli(["generate"])
            args = build_parser().parse_args(["generate"])
        self.assertEqual(code, 0)
        password = out.strip().split("  [")[0]
        self.assertEqual(len(password), 10)
        self.assertFalse(any(c in AMBIGUOUS for c in password))
        self.assertEqual(args.length, 10)
        self.assertTrue(args.exclude_ambiguous)


if __name__ == "__main__":
    unittest.main()
