from django.urls import path
from gears.views.jwt import JWTObtainPairView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views


urlpatterns = [
    path('auth/token/obtain/', JWTObtainPairView.as_view(), name='obtain-token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('auth/token/verification/', TokenVerifyView.as_view(), name='verify-token'),
]

router = routers.DefaultRouter()
router.register('auth', views.AuthViewSet, basename='auth')
router.register('users', views.UsersViewSet, basename='users')

urlpatterns += router.urls
