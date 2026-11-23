"""Argument parsing and command dispatch for password-toolkit."""

from __future__ import annotations

import argparse
import sys

from password_toolkit.config import get_default_length, get_exclude_ambiguous
from password_toolkit.core.generator import estimate_strength, generate


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser with environment-aware defaults.

    Returns:
        A parser with the ``generate`` and ``check`` subcommands.
    """
    parser = argparse.ArgumentParser(description="Generate and check passwords.")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="generate a random password")
    gen.add_argument("--length", type=int, default=get_default_length())
    gen.add_argument("--count", type=int, default=1)
    gen.add_argument("--no-upper", action="store_true")
    gen.add_argument("--no-lower", action="store_true")
    gen.add_argument("--no-digits", action="store_true")
    gen.add_argument("--no-symbols", action="store_true")
    gen.add_argument("--exclude-ambiguous", action="store_true", default=get_exclude_ambiguous())

    check = sub.add_parser("check", help="estimate the strength of a password")
    check.add_argument("password")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI.

    Args:
        argv: Optional argument list; ``sys.argv[1:]`` is used when omitted.

    Returns:
        ``0`` on success and ``1`` when generation fails validation.
    """
    args = build_parser().parse_args(argv)

    if args.command == "generate":
        try:
            for _ in range(args.count):
                password = generate(
                    length=args.length,
                    use_upper=not args.no_upper,
                    use_lower=not args.no_lower,
                    use_digits=not args.no_digits,
                    use_symbols=not args.no_symbols,
                    exclude_ambiguous=args.exclude_ambiguous,
                )
                label, bits = estimate_strength(password)
                print(f"{password}  [{label}, ~{bits} bits]")
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    label, bits = estimate_strength(args.password)
    print(f"Strength: {label} (~{bits} bits of entropy)")
    return 0
