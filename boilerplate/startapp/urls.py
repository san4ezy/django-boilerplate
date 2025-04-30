from django.urls import path

from rest_framework import routers

from . import views


urlpatterns = [
]

router = routers.DefaultRouter()
router.register("mymodel", views.MyModelViewSet, basename="mymodel")

urlpatterns += router.urls
