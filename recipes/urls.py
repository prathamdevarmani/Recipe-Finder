from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_recipes, name='favorite_recipes'),
    path('register/', views.register, name='register'),
]
