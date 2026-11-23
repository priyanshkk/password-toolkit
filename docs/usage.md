# Usage

All examples below use `python -m password_toolkit`. After an editable install
you can also use the `password-toolkit` console script. Passwords are random,
so your output will differ from the samples.

## `generate`

Generate one password with the default length (16) and all four character
classes:

```console
$ python -m password_toolkit generate
%]Y^4wOtck9}6/"<  [strong, ~104.9 bits]
```

Set an explicit length:

```console
$ python -m password_toolkit generate --length 20
=lZ<yhIao_,3K/0(T6^P  [strong, ~131.1 bits]
```

Generate several passwords at once (one line each):

```console
$ python -m password_toolkit generate --count 3 --length 12
7_!l*kL=ouTV  [strong, ~78.7 bits]
K:E/UVLm6GW>  [strong, ~78.7 bits]
=o0_G]>vgK2_  [strong, ~78.7 bits]
```

Omit punctuation:

```console
$ python -m password_toolkit generate --no-symbols --length 16
Ty5SXz2fxVds1RSX  [strong, ~95.3 bits]
```

Omit uppercase, lowercase or digits with `--no-upper`, `--no-lower` and
`--no-digits` respectively. Flags can be combined:

```console
$ python -m password_toolkit generate --no-symbols --no-digits --length 12
bEojoqYzTciz  [good, ~68.4 bits]
```

Exclude visually ambiguous characters (`O`, `0`, `o`, `I`, `l`, `1`, `|`,
backtick, single and double quote). This sample also uses `--no-symbols`:

```console
$ python -m password_toolkit generate --no-symbols --exclude-ambiguous --length 16
P8bcy5pzSZdLLKVz  [strong, ~95.3 bits]
```

### Validation errors

At least one class must be enabled, and the length must be at least the number
of enabled classes. With the default four classes, a length of 2 fails:

```console
$ python -m password_toolkit generate --length 2
error: Length must be at least 4 for the selected classes.
$ echo $?
1
```

Disabling every class is also rejected:

```console
$ python -m password_toolkit generate --no-upper --no-lower --no-digits --no-symbols
error: At least one character class must be enabled.
```

## `check`

Estimate the strength of an existing password:

```console
$ python -m password_toolkit check 'Tr0ub4dor&3xKq'
Strength: strong (~91.8 bits of entropy)
$ python -m password_toolkit check 'password123'
Strength: weak (~10 bits of entropy)
```

Labels and thresholds: `weak` below 30 bits, `fair` below 50, `good` below 70,
and `strong` at 70 or above.

## Environment configuration

Environment defaults apply when the corresponding CLI flag is omitted. See
`.env.example` and the README configuration table.

```console
$ export PASSWORD_LENGTH=12
$ export PASSWORD_EXCLUDE_AMBIGUOUS=1
$ python -m password_toolkit generate
U{#8rqM~Esm{  [strong, ~78.7 bits]
```

`--length` and `--exclude-ambiguous` replace the configured defaults when
supplied. Invalid environment values are ignored (16 / false is used).

## Library use

```python
from password_toolkit import estimate_strength, generate

password = generate(20, use_symbols=False, exclude_ambiguous=True)
label, bits = estimate_strength(password)
print(label, bits)
```
