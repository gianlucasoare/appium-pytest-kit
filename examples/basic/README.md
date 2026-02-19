# appium-pytest-kit basic example

## Run

1. `pip install appium-pytest-kit`
2. `cp .env.example .env`
3. `pytest -q`

`pytest -q` runs only the non-integration sample by default. To run driver session startup test:

- `pytest -q -m integration`
