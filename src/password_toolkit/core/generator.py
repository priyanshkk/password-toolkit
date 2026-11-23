"""Password generation and strength estimation.

All randomness comes from :class:`secrets.SystemRandom`. Every enabled
character class contributes at least one character to the result.
"""

from __future__ import annotations

import math
import secrets
import string

from password_toolkit.config import (
    AMBIGUOUS,
    COMMON_PASSWORDS,
    get_default_length,
    get_exclude_ambiguous,
)


def generate(
    length: int | None = None,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool | None = None,
) -> str:
    """Return a cryptographically secure random password.

    Args:
        length: Desired length. When omitted, ``PASSWORD_LENGTH`` (or 16) is used.
        use_upper: Include uppercase letters.
        use_lower: Include lowercase letters.
        use_digits: Include digits.
        use_symbols: Include punctuation.
        exclude_ambiguous: Drop confusing characters. When omitted,
            ``PASSWORD_EXCLUDE_AMBIGUOUS`` (or ``False``) is used.

    Returns:
        A password containing at least one character from each enabled class.

    Raises:
        ValueError: If no class is enabled, a class becomes empty after
            filtering, or ``length`` is smaller than the number of classes.
    """
    if length is None:
        length = get_default_length()
    if exclude_ambiguous is None:
        exclude_ambiguous = get_exclude_ambiguous()

    pools: list[str] = []
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
    """Return a ``(label, estimated_bits)`` pair for *password*.

    The estimate is ``len(password) * log2(pool_size)``, where the pool grows
    when lowercase, uppercase, digits and punctuation are present. Known common
    passwords are capped at 10 bits and passwords with three or fewer distinct
    characters have their estimate halved.

    Args:
        password: The password to evaluate. It is never logged or stored.

    Returns:
        A label (``weak``, ``fair``, ``good`` or ``strong``) and a rounded
        entropy estimate in bits.
    """
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
