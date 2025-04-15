from dataclasses import dataclass

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from gears.models.jwt import JWTUserModelMixin
from pytest_factoryboy import register
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.tests.factories import UserFactory


@dataclass
class FakeJWTUserModelMixin(JWTUserModelMixin):
    user: User

    def get_public_jwt_data(self):
        return dict(
            # Customized public payload goes here
        )

    def get_private_jwt_data(self):
        return dict(
            # Customized private payload goes here
        )


@pytest.fixture
def guest():
    return AnonymousUser()


@pytest.fixture
def token():
    def wrapper(user):
        jwt_model = FakeJWTUserModelMixin(user=user)
        token = RefreshToken.for_user(user)
        token = jwt_model.extend_token(token)
        return token

    return wrapper


@pytest.fixture
def api(token, dynamic_fixture):
    def wrapper(user: str | User):
        if isinstance(user, str):
            user = dynamic_fixture(user)
        client = APIClient()
        client.user = user
        if user and not isinstance(user, AnonymousUser):
            _token = token(user)
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {_token.access_token}")
        return client

    return wrapper


@pytest.fixture
def dynamic_fixture(request):
    def wrapper(name):
        return request.getfixturevalue(name)

    return wrapper


@pytest.fixture
def _file_factory(faker):
    def wrapper(suffix: str = ".txt"):
        fake_data = faker.text()
        file = SimpleUploadedFile(f"file{suffix}", bytes(fake_data, encoding="utf-8"))
        return file

    return wrapper


# Users
register(UserFactory, "user")

# Different users
register(UserFactory, "another_user")
