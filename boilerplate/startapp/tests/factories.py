import factory.fuzzy


class MyModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.Model"
        # django_get_or_create = ("unique",)
        skip_postgeneration_save = True

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        pass
