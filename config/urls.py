from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="REST API",
        default_version="v1",
        description="",
        terms_of_service="...",
        contact=openapi.Contact(email="san4ezy@gmail.com"),
    ),
    public=True,
    permission_classes=[
        # permissions.AllowAny,
        permissions.IsAdminUser,
    ],
)


urlpatterns = [
    # Specification
    re_path(
        r"^doc(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "doc/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.users.urls")),
]

if settings.DEBUG:
    urlpatterns += [] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
