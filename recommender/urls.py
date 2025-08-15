from django.urls import path
from .views import RecommendationAPIView, MenuItemListAPIView

urlpatterns = [
    path("recommend/me/", RecommendationAPIView.as_view()),
    path("recommend/<int:user_id>/", RecommendationAPIView.as_view()),
    path("menu-items/", MenuItemListAPIView.as_view()),
]
