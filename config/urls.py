from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
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
        contact=openapi.Contact(email=getattr(settings, "SWAGGER_CONTACT_EMAIL", "")),
    ),
    public=True,
    permission_classes=[
        # permissions.AllowAny,
        permissions.IsAdminUser,
    ],
)


def health_check(request):
    """
    Health check endpoint for Docker container healthcheck routine.
    Returns HTTP 200 OK with JSON status payload.
    """
    if request.META.get('REMOTE_ADDR') not in ['127.0.0.1', '::1']:
        return JsonResponse({"error": "Forbidden"}, status=403)
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # Health check
    path(
        "health/",
        health_check,
        name="health_check"
    ),
    # Specification
    path(
        "doc/api.json",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "doc/api.yaml",
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
