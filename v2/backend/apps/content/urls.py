from django.urls import path

from apps.content.views import GrainsGuideView, MeatGuideView, TipsGuideView

urlpatterns = [
    path("guides/grains/", GrainsGuideView.as_view(), name="guide-grains"),
    path("guides/tips/", TipsGuideView.as_view(), name="guide-tips"),
    path("guides/meat/<slug:cut>/", MeatGuideView.as_view(), name="guide-meat"),
]
