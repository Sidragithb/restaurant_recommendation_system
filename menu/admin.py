from django.contrib import admin
from .models import Category, MenuItem, Ingredient, Recipe, Review , SpecialOffer, RecipeIngredient

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description', 'image']  # Display name, category, description, and image
    list_filter = ['category']  # Add filter by category
    search_fields = ['name', 'description']  # Search by name or description
    readonly_fields = ['image']  # Make the image field readonly in the admin (optional)

admin.site.register(Category)
admin.site.register(MenuItem, MenuItemAdmin)  # Register with custom admin
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Review)
admin.site.register(SpecialOffer)
admin.site.register(RecipeIngredient)



