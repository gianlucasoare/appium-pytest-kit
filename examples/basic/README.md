# mobilkit basic example

## Run

1. `pip install mobilkit`
2. `cp .env.example .env`
3. `pytest -q`

`pytest -q` runs only the non-integration sample by default. To run driver session startup test:

- `pytest -q -m integration`
