from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg, Count

# ---------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------
class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# ---------------------------------------------------------------------
# MenuItem
# ---------------------------------------------------------------------
class MenuItem(models.Model):
    category     = models.ForeignKey(Category, on_delete=models.CASCADE)
    name         = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    image        = models.ImageField(upload_to="menu_images/", blank=True, null=True)
    price        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    @property
    def review_count(self):
        return self.reviews.aggregate(cnt=Count("id"))["cnt"]

    def __str__(self):
        return self.name

# ---------------------------------------------------------------------
# Ingredient
# ---------------------------------------------------------------------
class Ingredient(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# ---------------------------------------------------------------------
# Recipe
# ---------------------------------------------------------------------
class Recipe(models.Model):
    menu_item   = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient")
    steps       = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recipe for {self.menu_item.name}"

# ---------------------------------------------------------------------
# RecipeIngredient
# ---------------------------------------------------------------------
class RecipeIngredient(models.Model):
    recipe      = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient  = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity    = models.CharField(max_length=50)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} of {self.ingredient.name}"

# ---------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------
class Review(models.Model):
    menu_item  = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="reviews")
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating     = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "menu_item")

    def __str__(self):
        return f"{self.user} → {self.menu_item} ({self.rating})"

# ---------------------------------------------------------------------
# SpecialOffer
# ---------------------------------------------------------------------
class SpecialOffer(models.Model):
    menu_item           = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="offers")
    description         = models.CharField(max_length=200)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    valid_from  = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("menu_item", "valid_from", "valid_until")

    def clean(self):
        if self.valid_until <= self.valid_from:
            raise ValidationError("valid_until must be after valid_from")

    @property
    def is_active(self):
        now = timezone.now()
        return self.valid_from <= now <= self.valid_until

    def __str__(self):
        return f"{self.menu_item.name} – {self.discount_percentage}% OFF"
