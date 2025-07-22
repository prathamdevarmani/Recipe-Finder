from django.contrib import admin
from .models import FavoriteRecipe

# Register your models here.
@admin.register(FavoriteRecipe)     
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe_title', 'recipe_id', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('recipe_title', 'user__username')
