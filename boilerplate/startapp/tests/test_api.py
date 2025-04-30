import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from apps.core.helpers import PytestBase


User = get_user_model()


class TestMyModel(PytestBase):
    @property
    def list_url(self):
        return reverse("mymodel-list")

    def detail_url(self, instance_id):
        return reverse("mymodel-detail", args=(str(instance_id),))

    @pytest.mark.parametrize(
        "current_user, expected_status",
        (
                ("guest", status.HTTP_403_FORBIDDEN),
                ("user", status.HTTP_200_OK),
        ),
    )
    def test_list(self, api, dynamic_fixture, current_user, expected_status):
        current_user: User = dynamic_fixture(current_user)
        MyModelFactory.create_batch(3)
        response = api(current_user).get(self.list_url)
        assert response.status_code == expected_status
        if status.is_success(expected_status):
            assert response.data["count"] == 1
            first_user_data = response.data["results"][0]
            assert first_user_data["id"] == str(current_user.id)
