import pytest
from django.urls import reverse

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_signup_creates_user_and_logs_in(client):
    url = reverse("accounts:signup")
    resp = client.post(
        url,
        {
            "email": "new.engineer@example.com",
            "first_name": "New",
            "last_name": "Engineer",
            "password1": "correct-horse-1",
            "password2": "correct-horse-1",
        },
    )
    assert resp.status_code == 302
    assert User.objects.filter(email="new.engineer@example.com").exists()
    # Signed in: hitting a login-required page should not redirect to login
    resp = client.get(reverse("organizations:select"))
    assert resp.status_code == 200


def test_signup_rejects_duplicate_email(client, owner_user):
    url = reverse("accounts:signup")
    resp = client.post(
        url,
        {
            "email": owner_user.email,
            "first_name": "Dup",
            "last_name": "User",
            "password1": "correct-horse-1",
            "password2": "correct-horse-1",
        },
    )
    assert resp.status_code == 200
    assert "already exists" in str(resp.context["form"].errors)


def test_signup_rejects_mismatched_passwords(client):
    url = reverse("accounts:signup")
    resp = client.post(
        url,
        {
            "email": "mismatch@example.com",
            "first_name": "A",
            "last_name": "B",
            "password1": "correct-horse-1",
            "password2": "different-horse-2",
        },
    )
    assert resp.status_code == 200
    assert not User.objects.filter(email="mismatch@example.com").exists()


def test_login_with_correct_credentials(client, make_user):
    make_user(email="login-test@example.com")
    url = reverse("accounts:login")
    resp = client.post(url, {"username": "login-test@example.com", "password": "test-pass-123"})
    assert resp.status_code == 302


def test_login_with_wrong_password_fails(client, make_user):
    make_user(email="login-test2@example.com")
    url = reverse("accounts:login")
    resp = client.post(url, {"username": "login-test2@example.com", "password": "wrong-password"})
    assert resp.status_code == 200
    assert not resp.wsgi_request.user.is_authenticated


def test_logout(client, owner_user):
    client.force_login(owner_user)
    resp = client.post(reverse("accounts:logout"))
    assert resp.status_code == 302
    resp = client.get(reverse("organizations:select"))
    assert resp.status_code == 302  # redirected to login again
