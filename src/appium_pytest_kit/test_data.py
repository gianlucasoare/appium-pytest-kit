"""Test data factories — generate unique, realistic test data per run."""


import logging
import random
import string
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ── Core random generators ───────────────────────────────────────────────


def random_string(length: int = 8, *, prefix: str = "", charset: str | None = None) -> str:
    """Generate a random alphanumeric string.

    Args:
        length: Number of random characters (excluding prefix).
        prefix: Static prefix prepended to the random part.
        charset: Custom character set. Defaults to lowercase ASCII + digits.
    """
    chars = charset or (string.ascii_lowercase + string.digits)
    body = "".join(random.choices(chars, k=length))
    return f"{prefix}{body}"


def random_email(*, domain: str = "test.example.com", prefix: str = "user") -> str:
    """Generate a unique email address.

    Example: ``user_a3b7c2d1@test.example.com``
    """
    return f"{prefix}_{random_string(8)}@{domain}"


def random_phone(*, country_code: str = "+1", length: int = 10) -> str:
    """Generate a random phone number.

    Example: ``+15551234567``
    """
    digits = "".join(random.choices(string.digits, k=length))
    return f"{country_code}{digits}"


def random_username(*, prefix: str = "testuser") -> str:
    """Generate a unique username.

    Example: ``testuser_x7k2m9``
    """
    return f"{prefix}_{random_string(6)}"


def random_password(
    length: int = 12,
    *,
    uppercase: bool = True,
    digits: bool = True,
    special: bool = True,
) -> str:
    """Generate a random password meeting common complexity requirements.

    Guarantees at least one character from each enabled category.
    """
    required: list[str] = [random.choice(string.ascii_lowercase)]
    pool = string.ascii_lowercase

    if uppercase:
        required.append(random.choice(string.ascii_uppercase))
        pool += string.ascii_uppercase
    if digits:
        required.append(random.choice(string.digits))
        pool += string.digits
    if special:
        specials = "!@#$%^&*"
        required.append(random.choice(specials))
        pool += specials

    remaining = length - len(required)
    if remaining > 0:
        required.extend(random.choices(pool, k=remaining))

    chars = list(required)
    random.shuffle(chars)
    return "".join(chars)


def random_int(low: int = 1, high: int = 10000) -> int:
    """Generate a random integer in ``[low, high]``."""
    return random.randint(low, high)


def random_choice(options: list[Any]) -> Any:
    """Pick a random item from a list."""
    return random.choice(options)


def unique_id(*, prefix: str = "") -> str:
    """Generate a UUID4-based unique identifier.

    Example: ``prefix_a1b2c3d4``
    """
    short = uuid.uuid4().hex[:8]
    return f"{prefix}_{short}" if prefix else short


def timestamp_id(*, prefix: str = "ts") -> str:
    """Generate a timestamp-based identifier.

    Example: ``ts_1711660800_a3b7``
    """
    ts = int(time.time())
    suffix = random_string(4)
    return f"{prefix}_{ts}_{suffix}"


# ── DataFactory ──────────────────────────────────────────────────────────


@dataclass
class DataFactory:
    """Configurable test data factory with seeded randomness.

    Use a seed for reproducible test data across runs:

    Example::

        factory = DataFactory(seed=42)
        user = factory.user()
        print(user["email"])  # same every time with seed=42

    Or use without a seed for unique data per run:

    Example::

        factory = DataFactory()
        user = factory.user()
        print(user["email"])  # unique each run
    """

    seed: int | None = None
    email_domain: str = "test.example.com"
    phone_country_code: str = "+1"
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def _str(self, length: int = 8, *, prefix: str = "") -> str:
        chars = string.ascii_lowercase + string.digits
        body = "".join(self._rng.choices(chars, k=length))
        return f"{prefix}{body}"

    def email(self, *, prefix: str = "user", domain: str | None = None) -> str:
        """Generate a unique email."""
        d = domain or self.email_domain
        return f"{prefix}_{self._str(8)}@{d}"

    def phone(self, *, country_code: str | None = None, length: int = 10) -> str:
        """Generate a random phone number."""
        cc = country_code or self.phone_country_code
        digits = "".join(self._rng.choices(string.digits, k=length))
        return f"{cc}{digits}"

    def username(self, *, prefix: str = "testuser") -> str:
        """Generate a unique username."""
        return f"{prefix}_{self._str(6)}"

    def password(self, length: int = 12) -> str:
        """Generate a random password meeting complexity requirements."""
        required = [
            self._rng.choice(string.ascii_lowercase),
            self._rng.choice(string.ascii_uppercase),
            self._rng.choice(string.digits),
            self._rng.choice("!@#$%^&*"),
        ]
        pool = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*"
        remaining = length - len(required)
        if remaining > 0:
            required.extend(self._rng.choices(pool, k=remaining))
        chars = list(required)
        self._rng.shuffle(chars)
        return "".join(chars)

    def full_name(self) -> str:
        """Generate a random full name."""
        firsts = [
            "Alice", "Bob", "Charlie", "Dana", "Eve", "Frank", "Grace", "Hank",
            "Ivy", "Jack", "Kate", "Leo", "Maya", "Nate", "Olivia", "Paul",
        ]
        lasts = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller",
            "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "White", "Martin",
        ]
        return f"{self._rng.choice(firsts)} {self._rng.choice(lasts)}"

    def user(self, **overrides: Any) -> dict[str, Any]:
        """Generate a complete user profile dict.

        Returns a dict with keys: ``email``, ``username``, ``password``,
        ``phone``, ``full_name``, ``id``. Override any field via kwargs.

        Example::

            factory = DataFactory()
            user = factory.user(email="fixed@example.com")
        """
        data: dict[str, Any] = {
            "id": self._str(8, prefix="user_"),
            "email": self.email(),
            "username": self.username(),
            "password": self.password(),
            "phone": self.phone(),
            "full_name": self.full_name(),
        }
        data.update(overrides)
        return data

    def address(self, **overrides: Any) -> dict[str, Any]:
        """Generate a random address dict.

        Returns keys: ``street``, ``city``, ``state``, ``zip_code``, ``country``.
        """
        streets = ["123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Elm Dr", "654 Cedar Ln"]
        cities = ["Springfield", "Riverdale", "Shelbyville", "Portland", "Ashland"]
        states = ["CA", "NY", "TX", "FL", "WA", "OR", "IL", "PA"]

        data: dict[str, Any] = {
            "street": self._rng.choice(streets),
            "city": self._rng.choice(cities),
            "state": self._rng.choice(states),
            "zip_code": "".join(self._rng.choices(string.digits, k=5)),
            "country": "US",
        }
        data.update(overrides)
        return data

    def credit_card(self, **overrides: Any) -> dict[str, Any]:
        """Generate a test credit card dict (non-real numbers).

        Returns keys: ``number``, ``expiry``, ``cvv``, ``holder_name``.
        Uses standard test card numbers that will never charge.
        """
        test_numbers = [
            "4111111111111111",  # Visa test
            "5500000000000004",  # Mastercard test
            "340000000000009",   # Amex test
        ]
        month = self._rng.randint(1, 12)
        year = self._rng.randint(2026, 2030)

        data: dict[str, Any] = {
            "number": self._rng.choice(test_numbers),
            "expiry": f"{month:02d}/{year}",
            "cvv": "".join(self._rng.choices(string.digits, k=3)),
            "holder_name": self.full_name(),
        }
        data.update(overrides)
        return data

    def batch_users(self, count: int, **shared_overrides: Any) -> list[dict[str, Any]]:
        """Generate multiple unique user profiles.

        Args:
            count: Number of users to generate.
            **shared_overrides: Fields applied to every user.
        """
        return [self.user(**shared_overrides) for _ in range(count)]
