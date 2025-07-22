from django.db import models
from django.contrib.auth.models import User

class FavoriteRecipe(models.Model):
    """
    Model to store user's favorite recipes.
    Each recipe is uniquely identified by user and recipe_id combination.
    """
    # Link to Django's built-in User model
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who favorited the recipe"
    )
    
    # Recipe information from Spoonacular API
    recipe_id = models.IntegerField(
        help_text="Spoonacular recipe ID"
    )
    recipe_title = models.CharField(
        max_length=255,
        help_text="Title of the recipe"
    )
    recipe_image = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL of recipe image"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the recipe was favorited"
    )

    class Meta:
        # Ensure a user can't favorite the same recipe twice
        unique_together = ('user', 'recipe_id')
        # Order by most recently favorited
        ordering = ['-created_at']
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'

    def __str__(self):
        """String representation of the favorite recipe"""
        return f"{self.user.username} - {self.recipe_title}"
