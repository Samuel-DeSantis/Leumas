import pytest
from django.db import IntegrityError

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_create_user_normalizes_email():
    user = User.objects.create_user(email="Test@Example.com", password="pw")
    assert user.email == "Test@example.com"
    assert user.check_password("pw")
    assert not user.is_staff


def test_create_superuser_sets_flags():
    user = User.objects.create_superuser(email="admin@example.com", password="pw")
    assert user.is_staff
    assert user.is_superuser


def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="pw")


def test_email_is_unique():
    User.objects.create_user(email="dup@example.com", password="pw")
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="dup@example.com", password="pw")


def test_get_full_name_and_short_name():
    user = User.objects.create_user(email="ada@example.com", password="pw", first_name="Ada", last_name="Lovelace")
    assert user.get_full_name() == "Ada Lovelace"
    assert user.get_short_name() == "Ada"


def test_str_falls_back_to_email_without_name():
    user = User.objects.create_user(email="noname@example.com", password="pw")
    assert str(user) == "noname@example.com"
