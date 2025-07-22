from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import FavoriteRecipe
from .api import get_recipes, get_recipe_details
from django.views.decorators.http import require_POST
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
import re
from django.contrib import messages

def register(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Email validation pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not username or not password or not confirm_password or not email:
            error_message = 'All fields are required.'
        elif len(password) < 6:
            error_message = 'Password must be at least 6 characters.'
        elif password != confirm_password:
            error_message = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error_message = 'Username is already taken.'
        elif User.objects.filter(email=email).exists():
            error_message = 'Email address is already registered.'
        elif not re.match(email_pattern, email):
            error_message = 'Please enter a valid email address.'
        else:
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('login')
    return render(request, 'recipes/register.html', {'error_message': error_message})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('recipe_list')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['stay_logged_in'] = True  # Set flag to keep user logged in
            return redirect('recipe_list')
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'recipes/login.html')

def recipe_list(request):
    ingredients = ''
    recipes = []
    
    if request.method == 'POST':
        ingredients = request.POST.get('ingredients', '').strip()
        if ingredients:
            # Split ingredients by comma and clean them
            ingredient_list = [i.strip() for i in ingredients.split(',') if i.strip()]
            
            if not ingredient_list:
                messages.error(request, 'Please enter at least one ingredient')
                return render(request, 'recipes/recipe_list.html', {
                    'recipes': [],
                    'ingredients': ingredients,
                })
            
            recipes, error = get_recipes(ingredient_list)

            if error:
                messages.error(request, error)
            elif not recipes:
                messages.info(request, 'No recipes found for these ingredients. Try different ingredients!')
            
            # Add favorite status for authenticated users
            if request.user.is_authenticated and recipes:
                favorite_recipe_ids = set(FavoriteRecipe.objects.filter(
                    user=request.user,
                    recipe_id__in=[recipe['id'] for recipe in recipes]
                ).values_list('recipe_id', flat=True))
                
                for recipe in recipes:
                    recipe['is_favorite'] = recipe['id'] in favorite_recipe_ids

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'ingredients': ingredients,
    })

def recipe_detail(request, recipe_id):
    recipe, error = get_recipe_details(recipe_id)
    is_favorite = False
    
    if error:
        messages.error(request, error)
        return redirect('recipe_list')
    
    if not recipe:
        messages.error(request, 'Recipe not found or error fetching recipe details')
        return redirect('recipe_list')
    
    if request.user.is_authenticated:
        is_favorite = FavoriteRecipe.objects.filter(
            user=request.user,
            recipe_id=recipe_id
        ).exists()
    
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'is_favorite': is_favorite
    })

@login_required
@require_POST
def toggle_favorite(request):
    recipe_id = request.POST.get('recipe_id')
    recipe_title = request.POST.get('recipe_title')
    recipe_image = request.POST.get('recipe_image')
    
    try:
        favorite = FavoriteRecipe.objects.get(user=request.user, recipe_id=recipe_id)
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    except FavoriteRecipe.DoesNotExist:
        FavoriteRecipe.objects.create(
            user=request.user,
            recipe_id=recipe_id,
            recipe_title=recipe_title,
            recipe_image=recipe_image
        )
        return JsonResponse({'status': 'added'})

@login_required
def favorite_recipes(request):
    favorites = FavoriteRecipe.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'recipes/favorites.html', {'favorites': favorites})
