from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Category, MenuItem, Ingredient, Recipe,  Review, SpecialOffer
from .serializers import CategorySerializer, MenuItemSerializer, IngredientSerializer, RecipeSerializer,  ReviewSerializer, SpecialOfferSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import SAFE_METHODS, BasePermission
from django.db.models import Avg, Count


class IsStaffOrReadOnly(BasePermission):
    """
    • Anyone can read (GET / HEAD / OPTIONS).
    • Only staff or super-users can write (POST / PUT / PATCH / DELETE).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:          # read‑only
            return True
        return request.user and request.user.is_staff

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] 


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    serializer_class = MenuItemSerializer
    permission_classes = [IsStaffOrReadOnly]

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsStaffOrReadOnly] # Only staff can create/update/delete, but anyone can read

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsStaffOrReadOnly] # Only staff can create/update/delete, but anyone can read

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

class SpecialOfferViewSet(viewsets.ModelViewSet):
    queryset           = SpecialOffer.objects.all()
    serializer_class   = SpecialOfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]