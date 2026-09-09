from django.urls import path

from apps.prep.views import PrepKitDetailView, PrepKitListView

urlpatterns = [
    path("prep-kits/", PrepKitListView.as_view(), name="prep-kit-list"),
    path("prep-kits/<slug:slug>/", PrepKitDetailView.as_view(), name="prep-kit-detail"),
]
