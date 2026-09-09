from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from apps.content.urls import urlpatterns as content_urlpatterns
from apps.prep.urls import urlpatterns as prep_urlpatterns
from apps.recipes.urls import urlpatterns as recipes_urlpatterns


def healthz(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("healthz", healthz),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/", include(recipes_urlpatterns)),
    path("api/", include(content_urlpatterns)),
    path("api/", include(prep_urlpatterns)),
]
