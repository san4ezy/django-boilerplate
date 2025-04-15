from random import randint

from django.contrib.auth import get_user_model

import factory
import factory.fuzzy


User = get_user_model()

DEFAULT_PASSWORD = "password"
WRONG_PASSWORD = "wrong-password"
NEW_PASSWORD = "new-password"


def make_phone_number(*args, **kwargs):
    n = randint(1000001, 9999999)
    start_with = kwargs.get("start_with", 1000)
    return f"{start_with}{n}"


def make_text(*args, **kwargs):
    return "TEXT"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.User"
        django_get_or_create = ("phone_number",)
        skip_postgeneration_save = True

    phone_number = factory.LazyAttribute(make_phone_number)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        if create:
            self.set_password(DEFAULT_PASSWORD)
            self.save()


class SuperAdminFactory(UserFactory):
    is_superuser = True
