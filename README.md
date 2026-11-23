# Password Toolkit

[![Tests](https://github.com/priyanshkk/password-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/priyanshkk/password-toolkit/actions/workflows/tests.yml)
[![Lint and Typing](https://github.com/priyanshkk/password-toolkit/actions/workflows/linter.yml/badge.svg)](https://github.com/priyanshkk/password-toolkit/actions/workflows/linter.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Tests: unittest](https://img.shields.io/badge/tests-unittest-brightgreen.svg)
![Typing: mypy](https://img.shields.io/badge/typing-mypy-blue.svg)

## The problem

Quick password generators are easy to write badly: they use `random` instead of
a cryptographic source, silently omit a character class you asked for, accept
a length too short to contain all enabled classes, or quietly log what they
generated. This project is a small, auditable command-line tool that gets those
basics right and explains its strength estimate instead of presenting a
mysterious score.

## Overview

`password_toolkit` generates passwords with `secrets.SystemRandom`, guarantees
one character from every enabled class, and estimates strength with a
documented entropy heuristic. It has no runtime dependencies beyond the Python
standard library, supports Python 3.10-3.13, and can be used as a CLI
(`python -m password_toolkit`) or as a library (`from password_toolkit import
generate`). Generated passwords are printed once and never stored.

Details: [documentation index](docs/index.md) · [architecture](docs/architecture.md)
· [full usage reference](docs/usage.md).

## Tech stack

| Area | Choice | Why |
| --- | --- | --- |
| Language | Python 3.10+ | Standard-library only at runtime |
| Randomness | `secrets.SystemRandom` | Cryptographically secure source |
| CLI | `argparse` | Subcommands, validation, no dependency |
| Packaging | Hatchling, PEP 621 | `src/` layout and console-script entry point |
| Testing | `unittest`, `pytest` | Same tests run under both runners |
| Linting | Ruff (`E,F,I,UP,B,SIM`, 100 columns) | Fast, deterministic checks |
| Typing | mypy (strict) | Checked over `src/password_toolkit` |
| CI | GitHub Actions | Tests on 3.10-3.13, lint + typing on 3.12 |

## Real demo output

Captured by running the CLI from a checkout (passwords are random, so your
output will differ):

```console
$ python -m password_toolkit generate
%]Y^4wOtck9}6/"<  [strong, ~104.9 bits]

$ python -m password_toolkit generate --no-symbols --exclude-ambiguous --length 16
P8bcy5pzSZdLLKVz  [strong, ~95.3 bits]

$ python -m password_toolkit generate --count 3 --length 12
7_!l*kL=ouTV  [strong, ~78.7 bits]
K:E/UVLm6GW>  [strong, ~78.7 bits]
=o0_G]>vgK2_  [strong, ~78.7 bits]

$ python -m password_toolkit check 'Tr0ub4dor&3xKq'
Strength: strong (~91.8 bits of entropy)

$ python -m password_toolkit generate --length 2
error: Length must be at least 4 for the selected classes.
```

The estimator computes `length × log2(pool_size)` from the character classes
present, caps known common passwords at 10 bits and halves the score for
strings with three or fewer distinct characters. Labels: `weak` (<30),
`fair` (<50), `good` (<70), `strong` (>=70). It is a teaching heuristic, not a
replacement for a dedicated password-strength estimator.

## Install and setup

```bash
git clone https://github.com/priyanshkk/password-toolkit.git
cd password-toolkit

# Windows
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
.venv\Scripts\python -m password_toolkit --help

# POSIX (macOS / Linux)
sh scripts/setup.sh
.venv/bin/python -m password_toolkit --help
```

The setup scripts create `.venv` and install `requirements-dev.txt`, which is
an editable install (`-e ".[dev]"`) with pytest, Ruff, mypy and build. For a
runtime-only install use `python -m pip install -e .` (the `password-toolkit`
console script is then available). Running the tests from the repo root does
not require installation.

## Usage examples

```bash
# 20-character password with every class enabled
python -m password_toolkit generate --length 20

# Letters and digits only, without confusing O/0/I/l/1 characters
python -m password_toolkit generate --no-symbols --exclude-ambiguous

# Five passwords at once
python -m password_toolkit generate --count 5

# Disable a specific class
python -m password_toolkit generate --no-upper

# Check an existing password
python -m password_toolkit check 'Tr0ub4dor&3xKq'
```

Every flag and error case is documented in [docs/usage.md](docs/usage.md).

## Project structure

```text
password-toolkit/
├── .github/
│   ├── ISSUE_TEMPLATE/{bug_report.md,feature_request.md}
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/{tests.yml,linter.yml}
├── docs/{index.md,architecture.md,usage.md}
├── scripts/{setup.ps1,setup.sh}
├── src/password_toolkit/
│   ├── __init__.py          public API
│   ├── __main__.py          python -m entry point
│   ├── config.py            constants + environment defaults
│   └── core/
│       ├── generator.py     generation and strength estimation
│       └── cli.py           argument parsing and dispatch
├── tests/
│   ├── __init__.py          src/ path setup for package imports
│   ├── test_core.py         logic, validation and config tests
│   └── test_main.py         CLI tests
├── .env.example
├── .pre-commit-config.yaml
├── requirements.txt         stdlib only (editable install)
├── requirements-dev.txt     -e ".[dev]"
├── pyproject.toml
├── LICENSE
└── README.md
```

## Environment configuration

Copy `.env.example` to `.env` if you use a dotenv loader, or export the
variables directly. `config.py` reads them on every call.

| Variable | Default | Effect |
| --- | --- | --- |
| `PASSWORD_LENGTH` | `16` | Positive integer used as the default for `generate` and the CLI when `--length` is omitted. Invalid or non-positive values fall back to 16. |
| `PASSWORD_EXCLUDE_AMBIGUOUS` | `0` | Set to `1` to omit `O`, `0`, `o`, `I`, `l`, `1`, `|`, backtick and quote characters by default; any other value keeps them. |

## Testing and checks

```bash
python -m unittest discover -s tests -v   # 15 tests
python -m pytest                          # same tests via pytest
python -m ruff check .                    # E,F,I,UP,B,SIM, line length 100
python -m mypy src/password_toolkit       # strict typing
```

## Roadmap

- Optional word-list (passphrase) generation mode.
- An opt-in `--min-entropy` flag that rejects weak configurations.
- A documented, pluggable strength estimator interface.

These are ideas only; they are not implemented in this version.

## License

MIT - see [LICENSE](LICENSE). Copyright (c) 2026 Priyanshu Kumar.
