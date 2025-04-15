from django.contrib.auth import get_user_model

from gears.viewsets.serializers import SerializersMixin
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers


User = get_user_model()


class AuthViewSet(
    SerializersMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializers = {
        "default": serializers.UserSerializer,
        "signup": serializers.SignupUserSerializer,
    }

    @action(methods=["post"], detail=False, permission_classes=(AllowAny,))
    def signup(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data.get("password"))
        data = self.get_serializer(user, serializer_name="default").data
        data.update(
            {
                "token": user.get_tokens_pair(),
            }
        )
        return Response(data, status=status.HTTP_201_CREATED)


class UsersViewSet(
    SerializersMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializers = {
        None: serializers.UserSerializer,
    }
    pagination_class = LimitOffsetPagination
    parser_classes = (
        MultiPartParser,
        FormParser,
        JSONParser,
    )

    def get_queryset(self):
        return super().get_queryset().filter(id=self.request.user.id)

    @action(
        methods=(
            "get",
            "patch",
        ),
        detail=False,
    )
    def me(self, request, *args, **kwargs):
        if request.method == "GET":
            serializer = self.get_serializer(instance=request.user)
            return Response(serializer.data)
        if request.method == "PATCH":
            data = request.data
            serializer = self.get_serializer(
                instance=request.user, data=data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
