from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "phone_number", "first_name", "last_name",)

    def create(self, validated_data):
        model = self.Meta.model
        user = model.objects.create(**validated_data)
        password = validated_data.pop("password")
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password") if "password" in validated_data else None
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class SignupUserSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "phone_number", "password", "first_name", "last_name",)
        extra_kwargs = {
            "phone_number": {"required": True, "allow_null": False},
            "password": {"required": True, "allow_null": False},
        }