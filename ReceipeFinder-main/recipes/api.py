import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from typing import List, Dict, Optional, Tuple
from django.conf import settings

# Get API key from environment variable or settings
API_KEY = 'fc67a2d1d5664b128bb784fce35e4e09'

# Base URL for Spoonacular API
BASE_URL = "https://api.spoonacular.com"

# Create a session with retry logic
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods=["GET"]  # HTTP methods to retry
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Create a session to be reused
session = create_session()

def get_recipes(ingredients: str | List[str]) -> Tuple[List[Dict], Optional[str]]:
    """
    Get recipes based on ingredients.
    Args:
        ingredients: String of comma-separated ingredients or list of ingredients
    Returns:
        Tuple of (list of recipe dictionaries, error message if any)
    """
    # Convert string input to list
    if isinstance(ingredients, str):
        ingredients = [i.strip() for i in ingredients.split(',')]
    
    # API parameters
    params = {
        'ingredients': ','.join(ingredients),
        'apiKey': API_KEY,
        'number': 12,
        'ranking': 2,
        'ignorePantry': True
    }
    
    try:
        response = session.get(
            f"{BASE_URL}/recipes/findByIngredients",
            params=params,
            timeout=(5, 15)  # (connect timeout, read timeout)
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.Timeout:
        return [], "Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        if response.status_code == 402:
            return [], "API quota exceeded. Please try again later."
        elif response.status_code == 401:
            return [], "Invalid API key. Please check your configuration."
        else:
            return [], f"API error: {response.status_code}"
    except requests.exceptions.ConnectionError as e:
        return [], "Connection error. Please check your internet connection."
    except requests.RequestException as e:
        return [], f"Error: {str(e)}"

def get_recipe_details(recipe_id: int) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Get detailed information about a specific recipe.
    Args:
        recipe_id: ID of the recipe
    Returns:
        Tuple of (recipe details dictionary or None, error message if any)
    """
    params = {'apiKey': API_KEY}
    
    try:
        response = session.get(
            f"{BASE_URL}/recipes/{recipe_id}/information",
            params=params,
            timeout=(5, 15)  # (connect timeout, read timeout)
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        if response.status_code == 402:
            return None, "API quota exceeded. Please try again later."
        elif response.status_code == 401:
            return None, "Invalid API key. Please check your configuration."
        else:
            return None, f"API error: {response.status_code}"
    except requests.exceptions.ConnectionError as e:
        return None, "Connection error. Please check your internet connection."
    except requests.RequestException as e:
        return None, f"Error: {str(e)}"
