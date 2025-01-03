"""Recommendation system for the bar order management."""
from typing import List, Dict, Any
from .models import Customer, Drink


def recommend_cocktail(customer: Customer, drink_list: List[Drink]) -> List[str]:
    """Generate personalized cocktail recommendations for a customer.

    Args:
        customer: Customer object containing preferences and restrictions
        drink_list: List of available drinks

    Returns:
        List of recommended drink names
    """
    # Filter drinks based on age restriction and preferences
    recommendations = []
    
    if customer.age < 21:
        # For underage customers, only recommend Virgin drinks
        recommendations = [
            drink for drink in drink_list
            if drink.name.startswith("Virgin") and
            any(pref in drink.flavor_profile 
                for pref in customer.preferences.get('flavor', []))
        ]
    else:
        # For adult customers, recommend cocktails based on preferences
        recommendations = [
            drink for drink in drink_list
            if drink.category == 'cocktail' and
            any(pref in drink.flavor_profile 
                for pref in customer.preferences.get('flavor', []))
        ]
    
    return [drink.name for drink in recommendations]


def recommend_combo(customer: Customer, 
                   drink_list: List[Drink],
                   combo_definitions: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate combo recommendations based on customer preferences and restrictions.

    Args:
        customer: Customer object
        drink_list: List of available drinks
        combo_definitions: Dictionary defining available combos and their components

    Returns:
        List of recommended combo dictionaries
    """
    valid_combos = []
    
    for combo_name, combo_info in combo_definitions.items():
        # Check if combo matches customer restrictions
        if any(restriction in combo_info.get('allergens', [])
               for restriction in customer.restrictions.get('allergies', [])):
            continue
            
        # Check if all drinks in combo are appropriate for customer
        drinks_valid = True
        for drink_name in combo_info.get('drinks', []):
            drink = next((d for d in drink_list if d.name == drink_name), None)
            if drink and customer.age < 21 and drink.abv > 0:
                drinks_valid = False
                break
                
        if drinks_valid:
            valid_combos.append({
                'name': combo_name,
                'description': combo_info.get('description', ''),
                'price': combo_info.get('price', 0.0)
            })
    
    return valid_combos


def recommend_by_inventory(customer: Customer,
                         drink_list: List[Drink],
                         inventory: Dict[str, int],
                         min_stock: int = 5) -> List[str]:
    """Generate recommendations based on inventory levels.

    Args:
        customer: Customer object
        drink_list: List of available drinks
        inventory: Dictionary mapping drink names to stock levels
        min_stock: Minimum stock level to consider for promotion

    Returns:
        List of recommended drink names
    """
    # Filter drinks with high inventory
    high_stock_drinks = [
        drink for drink in drink_list
        if inventory.get(drink.name, 0) > min_stock
    ]
    
    # Apply customer preferences and restrictions
    if customer.age < 21:
        high_stock_drinks = [d for d in high_stock_drinks if d.abv == 0]
        
    # Sort by inventory level (descending) to prioritize items with highest stock
    high_stock_drinks.sort(
        key=lambda x: inventory.get(x.name, 0),
        reverse=True
    )
    
    return [drink.name for drink in high_stock_drinks]


def recommend_group_package(group_size: int,
                          customer: Customer,
                          drink_list: List[Drink],
                          packages: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate package recommendations for group orders.

    Args:
        group_size: Number of people in the group
        customer: Customer object (group representative)
        drink_list: List of available drinks
        packages: Dictionary of available group packages

    Returns:
        List of recommended package dictionaries
    """
    valid_packages = []
    
    for pkg_name, pkg_info in packages.items():
        # Check if package size matches group size
        min_size = pkg_info.get('min_size', 1)
        max_size = pkg_info.get('max_size', float('inf'))
        
        if min_size <= group_size <= max_size:
            # Verify package contents against customer restrictions
            if not any(restriction in pkg_info.get('allergens', [])
                      for restriction in customer.restrictions.get('allergies', [])):
                valid_packages.append({
                    'name': pkg_name,
                    'description': pkg_info.get('description', ''),
                    'price': pkg_info.get('price', 0.0),
                    'serves': pkg_info.get('serves', group_size)
                })
    
    return valid_packages


def get_seasonal_recommendations(customer: Customer,
                               drink_list: List[Drink],
                               current_season: str) -> List[str]:
    """Generate seasonal drink recommendations.

    Args:
        customer: Customer object
        drink_list: List of available drinks
        current_season: Current season ('summer', 'winter', etc.)

    Returns:
        List of recommended seasonal drink names
    """
    # Map seasons to preferred drink characteristics
    season_preferences = {
        'summer': ['refreshing', 'light', 'fruity'],
        'winter': ['warm', 'spiced', 'rich'],
        'spring': ['floral', 'light', 'fresh'],
        'fall': ['spiced', 'rich', 'warm']
    }
    
    seasonal_traits = season_preferences.get(current_season.lower(), [])
    
    # Filter drinks based on seasonal characteristics
    seasonal_drinks = [
        drink for drink in drink_list
        if any(trait in drink.flavor_profile for trait in seasonal_traits)
    ]
    
    # Apply age restrictions
    if customer.age < 21:
        seasonal_drinks = [drink for drink in seasonal_drinks if drink.abv == 0]
    
    return [drink.name for drink in seasonal_drinks]
