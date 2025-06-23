from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from django.contrib.auth import get_user_model
from .utils import hybrid_recommendation
from .serializers import MenuItemMiniSerializer


class RecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        # Get the user to recommend for
        target = request.user
        if user_id is not None:
            if not request.user.is_staff:
                return Response({"detail": "Only staff can access others."}, status=403)
            target = self._get_user(user_id)

        # Get number of recommendations from query parameter
        raw_n = request.query_params.get("n")
        if raw_n in (None, "", "all"):
            n = None  # Return all items
        else:
            try:
                n = int(raw_n)
            except ValueError:
                raise ParseError("Please enter a number or 'all' for n.")

        # Generate hybrid recommendations
        items = hybrid_recommendation(target, top_n=n)
        data = MenuItemMiniSerializer(items, many=True).data

        return Response({
            "user": target.id,
            "count": len(data),
            "recommendations": data
        })

    def _get_user(self, uid):
        # Helper function to get a user by ID
        User = get_user_model()
        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            raise NotFound("User not found.")
