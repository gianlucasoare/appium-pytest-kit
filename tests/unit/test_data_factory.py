"""Tests for the test data factory module."""

from appium_pytest_kit.test_data import (
    DataFactory,
    random_choice,
    random_email,
    random_int,
    random_password,
    random_phone,
    random_string,
    random_username,
    timestamp_id,
    unique_id,
)


class TestRandomGenerators:
    """Standalone random generator functions."""

    def test_random_string_default_length(self) -> None:
        result = random_string()
        assert len(result) == 8
        assert result.isalnum()

    def test_random_string_custom_length(self) -> None:
        result = random_string(16)
        assert len(result) == 16

    def test_random_string_with_prefix(self) -> None:
        result = random_string(4, prefix="test_")
        assert result.startswith("test_")
        assert len(result) == 9  # prefix(5) + body(4)

    def test_random_string_custom_charset(self) -> None:
        result = random_string(10, charset="abc")
        assert all(c in "abc" for c in result)

    def test_random_email_format(self) -> None:
        result = random_email()
        assert "@test.example.com" in result
        assert result.startswith("user_")

    def test_random_email_custom_domain(self) -> None:
        result = random_email(domain="custom.org", prefix="admin")
        assert "@custom.org" in result
        assert result.startswith("admin_")

    def test_random_phone_format(self) -> None:
        result = random_phone()
        assert result.startswith("+1")
        assert len(result) == 12  # +1 + 10 digits

    def test_random_phone_custom_country(self) -> None:
        result = random_phone(country_code="+44", length=10)
        assert result.startswith("+44")

    def test_random_username_format(self) -> None:
        result = random_username()
        assert result.startswith("testuser_")
        assert len(result) == len("testuser_") + 6

    def test_random_password_default(self) -> None:
        result = random_password()
        assert len(result) == 12
        assert any(c.islower() for c in result)
        assert any(c.isupper() for c in result)
        assert any(c.isdigit() for c in result)
        assert any(c in "!@#$%^&*" for c in result)

    def test_random_password_simple(self) -> None:
        result = random_password(8, uppercase=False, digits=False, special=False)
        assert len(result) == 8
        assert result.isalpha()
        assert result.islower()

    def test_random_int_range(self) -> None:
        for _ in range(20):
            result = random_int(1, 10)
            assert 1 <= result <= 10

    def test_random_choice_from_list(self) -> None:
        options = ["a", "b", "c"]
        result = random_choice(options)
        assert result in options

    def test_unique_id_no_prefix(self) -> None:
        result = unique_id()
        assert len(result) == 8  # uuid hex[:8]

    def test_unique_id_with_prefix(self) -> None:
        result = unique_id(prefix="order")
        assert result.startswith("order_")

    def test_unique_id_uniqueness(self) -> None:
        ids = {unique_id() for _ in range(100)}
        assert len(ids) == 100

    def test_timestamp_id_format(self) -> None:
        result = timestamp_id()
        assert result.startswith("ts_")
        parts = result.split("_")
        assert len(parts) == 3
        assert parts[1].isdigit()


class TestDataFactory:
    """DataFactory class behavior."""

    def test_seeded_produces_deterministic_output(self) -> None:
        f1 = DataFactory(seed=42)
        f2 = DataFactory(seed=42)

        assert f1.email() == f2.email()
        assert f1.username() == f2.username()
        assert f1.password() == f2.password()

    def test_different_seeds_produce_different_output(self) -> None:
        f1 = DataFactory(seed=1)
        f2 = DataFactory(seed=2)

        assert f1.email() != f2.email()

    def test_email_method(self) -> None:
        f = DataFactory(seed=99)
        result = f.email()
        assert "@test.example.com" in result

    def test_email_custom_domain(self) -> None:
        f = DataFactory()
        result = f.email(domain="corp.io")
        assert "@corp.io" in result

    def test_phone_method(self) -> None:
        f = DataFactory(seed=99)
        result = f.phone()
        assert result.startswith("+1")
        assert len(result) == 12

    def test_phone_custom_country(self) -> None:
        f = DataFactory(phone_country_code="+44")
        result = f.phone()
        assert result.startswith("+44")

    def test_username_method(self) -> None:
        f = DataFactory(seed=99)
        result = f.username()
        assert result.startswith("testuser_")

    def test_password_method(self) -> None:
        f = DataFactory(seed=99)
        result = f.password()
        assert len(result) == 12

    def test_full_name_method(self) -> None:
        f = DataFactory(seed=99)
        result = f.full_name()
        parts = result.split()
        assert len(parts) == 2

    def test_user_method_returns_all_keys(self) -> None:
        f = DataFactory(seed=99)
        user = f.user()

        assert "id" in user
        assert "email" in user
        assert "username" in user
        assert "password" in user
        assert "phone" in user
        assert "full_name" in user

    def test_user_overrides(self) -> None:
        f = DataFactory(seed=99)
        user = f.user(email="fixed@example.com", phone="+1234567890")

        assert user["email"] == "fixed@example.com"
        assert user["phone"] == "+1234567890"
        # Non-overridden fields are still generated
        assert user["username"].startswith("testuser_")

    def test_address_method(self) -> None:
        f = DataFactory(seed=99)
        addr = f.address()

        assert "street" in addr
        assert "city" in addr
        assert "state" in addr
        assert "zip_code" in addr
        assert "country" in addr
        assert len(addr["zip_code"]) == 5

    def test_address_overrides(self) -> None:
        f = DataFactory(seed=99)
        addr = f.address(city="Custom City")

        assert addr["city"] == "Custom City"

    def test_credit_card_method(self) -> None:
        f = DataFactory(seed=99)
        card = f.credit_card()

        assert "number" in card
        assert "expiry" in card
        assert "cvv" in card
        assert "holder_name" in card
        assert len(card["cvv"]) == 3
        assert card["number"] in [
            "4111111111111111",
            "5500000000000004",
            "340000000000009",
        ]

    def test_credit_card_overrides(self) -> None:
        f = DataFactory(seed=99)
        card = f.credit_card(holder_name="John Doe")

        assert card["holder_name"] == "John Doe"

    def test_batch_users(self) -> None:
        f = DataFactory(seed=99)
        users = f.batch_users(5)

        assert len(users) == 5
        emails = [u["email"] for u in users]
        assert len(set(emails)) == 5  # all unique

    def test_batch_users_with_shared_overrides(self) -> None:
        f = DataFactory(seed=99)
        users = f.batch_users(3, phone="+1111111111")

        for u in users:
            assert u["phone"] == "+1111111111"

    def test_unseeded_produces_unique_output(self) -> None:
        f = DataFactory()
        emails = {f.email() for _ in range(50)}
        assert len(emails) == 50
