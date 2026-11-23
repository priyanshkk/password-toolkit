"""Generate strong random passwords and estimate their strength.

The public helpers are re-exported here for a convenient import path; the
implementation lives in :mod:`password_toolkit.core.generator` and the CLI in
:mod:`password_toolkit.core.cli`.
"""

from password_toolkit.config import AMBIGUOUS, COMMON_PASSWORDS
from password_toolkit.core.cli import build_parser, main
from password_toolkit.core.generator import estimate_strength, generate

__version__ = "0.1.0"

__all__ = [
    "AMBIGUOUS",
    "COMMON_PASSWORDS",
    "build_parser",
    "estimate_strength",
    "generate",
    "main",
]
