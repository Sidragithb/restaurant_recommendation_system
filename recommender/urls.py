from django.urls import path
from .views import RecommendationAPIView

urlpatterns = [
    path("recommend/me/", RecommendationAPIView.as_view()),
    path("recommend/<int:user_id>/", RecommendationAPIView.as_view()),
]
