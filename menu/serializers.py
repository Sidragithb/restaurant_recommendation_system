from django.utils import timezone
from rest_framework import serializers
from .models import (
    Category,
    MenuItem,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Review,
    SpecialOffer,
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = "__all__"

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ("id", "menu_item", "ingredients", "steps")

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("user", "created_at")

    def validate(self, data):
        if Review.objects.filter(
            menu_item=data["menu_item"], user=self.context["request"].user
        ).exists():
            raise serializers.ValidationError("You have already reviewed this item.")
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class MenuItemSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count   = serializers.SerializerMethodField()
    reviews        = ReviewSerializer(many=True, read_only=True)
    active_offer   = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "category",
            "name",
            "description",
            "image",
            "price",
            "average_rating",
            "review_count",
            "active_offer",
            "reviews",
            "is_available",
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 2)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_active_offer(self, obj):
        offer = obj.offers.filter(
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        ).first()
        if offer:
            return {
                "description": offer.description,
                "discount_percentage": offer.discount_percentage,
                "valid_from": offer.valid_from,
                "valid_until": offer.valid_until,
            }
        return None

class SpecialOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOffer
        fields = "__all__"
