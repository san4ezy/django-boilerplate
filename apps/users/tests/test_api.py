import string
from random import choice

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.helpers import PytestBase
from apps.users.models import User
from apps.users.tests.factories import DEFAULT_PASSWORD
from apps.users.tests.factories import NEW_PASSWORD
from apps.users.tests.factories import UserFactory
from apps.users.tests.factories import make_phone_number


class TestObtainToken(PytestBase):
    @property
    def url(self):
        return reverse("obtain-token")

    def test_normal(self, api, guest, user):
        response = api(guest).post(
            self.url,
            {
                "phone_number": user.phone_number,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_wrong_password(self, api, guest, user):
        response = api(guest).post(
            self.url,
            {
                "phone_number": user.phone_number,
                "password": "wrong-password",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data
        assert "refresh" not in response.data

    def test_unknown_phone_number(self, api, guest):
        # existing users have numbers starting with 1
        phone_number = make_phone_number(start_with=2000)
        response = api(guest).post(
            self.url,
            {
                "phone_number": phone_number,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data
        assert "refresh" not in response.data

    def test_inactive_user(self, api, guest, user):
        user.is_active = False
        user.save()
        response = api(guest).post(
            self.url,
            {
                "phone_number": user.phone_number,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "access" not in response.data
        assert "refresh" not in response.data

    def test_without_password(self, api, guest, user):
        response = api(guest).post(
            self.url,
            {
                "phone_number": user.phone_number,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "access" not in response.data
        assert "refresh" not in response.data


class TestSignup(PytestBase):
    @property
    def url(self):
        return reverse("auth-signup")

    def test_normal(self, api, guest, user_factory):
        user = user_factory.build()
        response = api(guest).post(
            self.url,
            {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data["token"]
        assert "refresh" in response.data["token"]

    def test_without_phone_number(self, api, guest):
        response = api(guest).post(
            self.url,
            {
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" not in response.data

    def test_without_password(self, api, guest):
        response = api(guest).post(
            self.url,
            {
                "phone_number": make_phone_number(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" not in response.data

    def test_with_existing_phone_number(self, api, guest, user):
        response = api(guest).post(
            self.url,
            {
                "phone_number": user.phone_number,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" not in response.data

    def test_with_wrong_phone_number(self, api, guest):
        response = api(guest).post(
            self.url,
            {
                "phone_number": "111",  # too short phone number
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" not in response.data

    def test_inactive_user(self, api, guest, user):
        response = api(guest).post(
            self.url,
            {
                "phone_number": user.phone_number,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" not in response.data

    def test_as_logged_in(self, api, user):
        response = api(user).post(
            self.url,
            {
                "phone_number": user.phone_number,
                "password": DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" not in response.data


class TestRefreshToken(PytestBase):
    @property
    def url(self):
        return reverse("refresh-token")

    def test_normal(self, api, guest, user):
        refresh = RefreshToken.for_user(user)
        response = api(guest).post(
            self.url,
            {
                "refresh": str(refresh),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    @pytest.mark.parametrize(
        "token,status_code",
        (
            ("random", status.HTTP_401_UNAUTHORIZED),
            ("inactive", status.HTTP_401_UNAUTHORIZED),
            # ('deleted', status.HTTP_401_UNAUTHORIZED),
        ),
    )
    def test_random_token(self, api, guest, user, token, status_code):
        refresh = RefreshToken.for_user(user)
        match token:
            case "random":
                refresh = "".join(choice(string.ascii_lowercase) for _ in range(200))
            case "inactive":
                user.is_active = False
                user.save()
            case "deleted":
                user.delete()  # not working properly

        response = api(guest).post(
            self.url,
            {
                "refresh": str(refresh),
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data
        assert "refresh" not in response.data


class TestUsers(PytestBase):
    @property
    def list_url(self):
        return reverse("users-list")

    def detail_url(self, instance_id):
        return reverse("users-detail", args=(str(instance_id),))

    @property
    def me_url(self):
        return reverse("users-me")

    @pytest.mark.parametrize(
        "current_user, expected_status",
        (
            ("guest", status.HTTP_403_FORBIDDEN),
            ("user", status.HTTP_200_OK),
        ),
    )
    def test_me(self, api, dynamic_fixture, current_user, expected_status):
        current_user: User = dynamic_fixture(current_user)
        response = api(current_user).get(self.me_url)
        assert response.status_code == expected_status
        if status.is_success(expected_status):
            assert response.data["id"] == str(current_user.pk)
            assert response.data["phone_number"] == current_user.phone_number
            assert "password" not in response.data

    @pytest.mark.parametrize(
        "current_user, expected_status",
        (
            ("guest", status.HTTP_403_FORBIDDEN),
            ("user", status.HTTP_200_OK),
        ),
    )
    def test_me_update(self, api, dynamic_fixture, current_user, expected_status):
        current_user: User = dynamic_fixture(current_user)
        new_number = make_phone_number()
        response = api(current_user).patch(
            self.me_url,
            data={
                "phone_number": new_number,
            },
        )
        assert response.status_code == expected_status
        if status.is_success(expected_status):
            current_user.refresh_from_db()
            assert response.data["id"] == str(current_user.pk)
            assert response.data["phone_number"] == new_number
            assert current_user.phone_number == new_number

    def test_me_set_new_password(self, api, user):
        response = api(user).patch(
            self.me_url,
            data={
                "password": NEW_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password(NEW_PASSWORD) == True

    @pytest.mark.parametrize(
        "current_user, expected_status",
        (
            ("guest", status.HTTP_403_FORBIDDEN),
            ("user", status.HTTP_200_OK),
        ),
    )
    def test_list(self, api, dynamic_fixture, current_user, expected_status):
        current_user: User = dynamic_fixture(current_user)
        UserFactory.create_batch(3)
        response = api(current_user).get(self.list_url)
        assert response.status_code == expected_status
        if status.is_success(expected_status):
            assert response.data["count"] == 1  # only current_user
            first_user_data = response.data["results"][0]
            assert first_user_data["id"] == str(current_user.id)
            assert first_user_data["phone_number"] == current_user.phone_number
            assert first_user_data["email"] == current_user.email
            assert first_user_data["first_name"] == current_user.first_name
            assert first_user_data["last_name"] == current_user.last_name
            assert "password" not in response.data

    @pytest.mark.parametrize(
        "current_user, editing_user, expected_status",
        (
            ("guest", "user", status.HTTP_403_FORBIDDEN),
            ("user", "user", status.HTTP_200_OK),
            ("user", "another_user", status.HTTP_404_NOT_FOUND),
        ),
    )
    def test_update(
        self,
        api,
        dynamic_fixture,
        current_user,
        editing_user,
        expected_status,
    ):
        current_user: User = dynamic_fixture(current_user)
        editing_user: User = dynamic_fixture(editing_user)
        new_number = make_phone_number()
        response = api(current_user).patch(
            self.detail_url(editing_user.id),
            data={
                "phone_number": new_number,
            },
        )
        assert response.status_code == expected_status
        if status.is_success(expected_status):
            editing_user.refresh_from_db()
            assert response.data["id"] == str(editing_user.pk)
            assert response.data["phone_number"] == new_number
            assert editing_user.phone_number == new_number

    def test_new_password_for_another_user(self, api, user, another_user):
        response = api(user).patch(
            self.detail_url(another_user.id),
            data={
                "password": NEW_PASSWORD,
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        user.refresh_from_db()
        another_user.refresh_from_db()
        assert user.check_password(DEFAULT_PASSWORD) == True
        assert another_user.check_password(DEFAULT_PASSWORD) == True
