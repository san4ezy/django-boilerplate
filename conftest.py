from dataclasses import dataclass
from typing import Type

from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from django.db.models import Model
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


class Perm:
    VIEW, ADD, CHANGE, DELETE = "view", "add", "change", "delete"


@pytest.fixture
def set_permissions():
    def wrapper(current_user, permissions: tuple[Model, str]):
        def set_perm(m: Type[Model], mt: str):
            if isinstance(current_user, AnonymousUser):
                return current_user
            content_type = ContentType.objects.get_for_model(m)
            perm, _ = Permission.objects.get_or_create(
                codename=f"{mt}_{m.__name__.lower()}",
                name=f"Can {mt} {m.__name__.lower()}",
                content_type=content_type,
            )
            current_user.user_permissions.add(perm)

        for model, method in permissions:
            set_perm(model, method)
        return current_user
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
