# recommender/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .utils import hybrid_recommendation
from .serializers import MenuItemMiniSerializer
from django.contrib.auth import get_user_model


class RecommendationAPIView(APIView):
    """
    GET /api/recommend/me/   →  current logged‑in user
    GET /api/recommend/<int:user_id>/  →  specific user (staff only)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        # Which user to recommend for?
        target_user = request.user
        if user_id:
            if not request.user.is_staff:
                return Response({"detail": "Only staff can query others."}, status=403)
            try:
                target_user = get_user_model().objects.get(id=user_id)
            except get_user_model().DoesNotExist:
                return Response({"detail": "User not found"}, status=404)

        items = hybrid_recommendation(target_user, top_n=5)
        data = MenuItemMiniSerializer(items, many=True).data
        return Response({"user": target_user.id, "recommendations": data})
