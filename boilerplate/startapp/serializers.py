from rest_framework.serializers import ModelSerializer


class MyModelSerializer(ModelSerializer):
    class Meta:
        model = "MyModel"
        fields = "__all__"
        read_only_fields = ("id",)
