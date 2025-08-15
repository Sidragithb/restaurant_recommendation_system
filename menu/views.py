from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, SAFE_METHODS, BasePermission
from django.db.models import Avg, Count

from .models import Category, MenuItem, Ingredient, Recipe, Review, SpecialOffer
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ReviewSerializer,
    SpecialOfferSerializer
)

# -----------------------------
# Custom Permission
# -----------------------------
class IsStaffOrReadOnly(BasePermission):
    """
    • Anyone can read (GET / HEAD / OPTIONS).
    • Only staff can create/update/delete.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

# -----------------------------
# ViewSets
# -----------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsStaffOrReadOnly]

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsStaffOrReadOnly]

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsStaffOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

class SpecialOfferViewSet(viewsets.ModelViewSet):
    queryset = SpecialOffer.objects.all()
    serializer_class = SpecialOfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
