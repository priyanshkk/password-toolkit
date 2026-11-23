# Architecture

## Module map

```text
src/password_toolkit/
├── __init__.py        public API re-exports and version
├── __main__.py        `python -m password_toolkit` entry point
├── config.py          constants and environment-backed defaults
└── core/
    ├── __init__.py    core package marker
    ├── generator.py   password generation and strength estimation
    └── cli.py         argparse parser and command dispatch
```

There is deliberately no `utils` package: the two core modules share only the
small configuration surface in `config.py`, so a generic helper module would be
artificial.

## Data flow

### `generate`

1. `cli.main()` parses arguments. Unspecified defaults come from `config.py`
   (`PASSWORD_LENGTH`, `PASSWORD_EXCLUDE_AMBIGUOUS`) via `build_parser()`.
2. `core.generator.generate()` builds one character pool per enabled class.
3. Ambiguous characters are filtered out when requested; an empty pool is a
   validation error.
4. A `secrets.SystemRandom()` draws one character from each pool, fills the
   remainder from the combined alphabet, and shuffles the result.
5. `estimate_strength()` labels the result, and `cli.main()` prints one line:
   `<password>  [<label>, ~<bits> bits]`.

### `check`

`cli.main()` passes the positional password directly to `estimate_strength()`
and prints `Strength: <label> (~<bits> bits of entropy)`. No value is stored or
logged by the application.

## Design decisions

- **`secrets.SystemRandom` over `random`:** generated passwords must not be
  predictable from a seeded PRNG.
- **One character per enabled class:** guarantees diversity without rejecting
  and retrying whole passwords; the remaining characters are drawn uniformly
  from the union of pools, which slightly biases class distribution but is
  simple and bounded.
- **Entropy as a teaching heuristic:** `length × log2(pool_size)` is computed
  from the classes actually present in the password. Common passwords are
  capped at 10 bits and low-diversity strings are halved. This is not a
  zxcvbn-style estimator and makes no claim about real-world guessing risk.
- **Validation before generation:** requesting fewer characters than enabled
  classes raises `ValueError` (for example, length 2 with four classes). The
  CLI converts that into a `1` exit status and an `error:` line on stderr.
- **Environment defaults are read at call time:** `get_default_length()` and
  `get_exclude_ambiguous()` are functions rather than import-time constants, so
  changing the environment affects the next CLI invocation or library call.
  Invalid values fall back to 16 / false instead of crashing.
- **Flat public API:** `password_toolkit.generate`, `estimate_strength` and
  `main` are re-exported from `__init__.py` so simple imports keep working
  regardless of the internal module split.

## Testing model

`tests/test_core.py` covers generation, validation, strength bands and config
parsing. `tests/test_main.py` calls `main()` with argument lists and captures
stdout/stderr. Both modules insert `src/` into `sys.path` because plain
`unittest discover -s tests` uses `tests/` as its top-level directory.
