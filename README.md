# Password Toolkit

A tiny CLI for generating cryptographically secure passwords and estimating
how strong a password is. Uses only the standard library (`secrets`, `string`,
`math`, `argparse`).

## Usage

```bash
# 20-character password with everything enabled
python password_toolkit.py generate --length 20

# Letters and digits only, no confusing O/0/I/l/1 characters
python password_toolkit.py generate --no-symbols --exclude-ambiguous

# Generate 5 at once
python password_toolkit.py generate --count 5

# Check an existing password
python password_toolkit.py check 'Tr0ub4dor&3xKq'
```

## What "strength" means here

The estimator computes `length × log2(pool size)`, where the pool grows when
the password uses lowercase, uppercase, digits and punctuation. It then caps
known common passwords at 10 bits and halves the score for passwords using
three or fewer distinct characters. Labels: weak (<30), fair (<50), good
(<70), strong (>=70).

This is a useful teaching heuristic, not a replacement for a dedicated
zxcvbn-style estimator.

## Safety notes

- Every character comes from `secrets.SystemRandom()`.
- At least one character from each enabled class is guaranteed.
- Generated passwords are printed once and never stored anywhere.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
