from datetime import timezone
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
    average_rating = serializers.FloatField(read_only=True)  # Shows average rating (calculated)
    review_count = serializers.IntegerField(read_only=True)  # Shows number of reviews
    reviews = ReviewSerializer(many=True, read_only=True)    # Nested list of reviews  
    active_offer = serializers.SerializerMethodField()        # Shows current active offer

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
            "active_offer",   # Add active_offer to the serialized output
            "reviews",
            "is_available",
        ]

    def get_active_offer(self, obj):
        """
        Returns the first active offer for this menu item, if any.
        An offer is active if the current time is within the valid date range.
        """
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
        return None  # No active offer available
class SpecialOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOffer
        fields = "__all__"
