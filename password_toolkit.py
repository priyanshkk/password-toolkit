"""Generate strong random passwords and estimate their strength.

Uses ``secrets`` for all randomness, guarantees at least one character from
every enabled character class, and never logs or stores a generated password.
"""

from __future__ import annotations

import argparse
import math
import secrets
import string
import sys

AMBIGUOUS = set("O0oIl1|`'\"")
COMMON_PASSWORDS = {
    "password",
    "password123",
    "12345678",
    "qwerty",
    "letmein",
    "admin123",
    "welcome1",
}


def generate(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """Return a cryptographically secure random password."""
    pools = []
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(string.punctuation)

    if not pools:
        raise ValueError("At least one character class must be enabled.")
    if exclude_ambiguous:
        pools = ["".join(ch for ch in pool if ch not in AMBIGUOUS) for pool in pools]
        if any(not pool for pool in pools):
            raise ValueError("A character class became empty after excluding ambiguous characters.")
    if length < len(pools):
        raise ValueError(f"Length must be at least {len(pools)} for the selected classes.")

    rng = secrets.SystemRandom()
    alphabet = "".join(pools)
    # One character from each enabled class guarantees diversity.
    chars = [rng.choice(pool) for pool in pools]
    chars.extend(rng.choice(alphabet) for _ in range(length - len(chars)))
    rng.shuffle(chars)
    return "".join(chars)


def estimate_strength(password: str) -> tuple[str, float]:
    """Return a (label, estimated_bits) pair based on the character pool size."""
    pool_size = 0
    if any(ch.islower() for ch in password):
        pool_size += 26
    if any(ch.isupper() for ch in password):
        pool_size += 26
    if any(ch.isdigit() for ch in password):
        pool_size += 10
    if any(ch in string.punctuation for ch in password):
        pool_size += 32
    pool_size = max(pool_size, 1)

    entropy = len(password) * math.log2(pool_size)
    if password.lower() in COMMON_PASSWORDS:
        entropy = min(entropy, 10)
    if len(set(password)) <= 3:
        entropy *= 0.5

    if entropy < 30:
        label = "weak"
    elif entropy < 50:
        label = "fair"
    elif entropy < 70:
        label = "good"
    else:
        label = "strong"
    return label, round(entropy, 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and check passwords.")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="generate a random password")
    gen.add_argument("--length", type=int, default=16)
    gen.add_argument("--count", type=int, default=1)
    gen.add_argument("--no-upper", action="store_true")
    gen.add_argument("--no-lower", action="store_true")
    gen.add_argument("--no-digits", action="store_true")
    gen.add_argument("--no-symbols", action="store_true")
    gen.add_argument("--exclude-ambiguous", action="store_true")

    check = sub.add_parser("check", help="estimate the strength of a password")
    check.add_argument("password")
    return parser


def main(argv: list[str] | None = None) -> int:
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


if __name__ == "__main__":
    raise SystemExit(main())
