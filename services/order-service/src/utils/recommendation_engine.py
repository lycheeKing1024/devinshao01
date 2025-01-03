import logging
from typing import List, Dict, Optional, Any, TypedDict, Union, Tuple
from sqlalchemy.orm import Session
from ..models.order import MenuItem
from devinshao01.recommendations import recommend_cocktail, recommend_by_preferences
from devinshao01.models import Customer, Drink

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MenuItemDict(TypedDict):
    name: str
    category: str
    flavor_profile: Union[List[str], str]
    abv: float
    price: float
    allergens: Optional[List[str]]

def filter_by_constraints(items: List[MenuItem], constraints: Dict[str, Any]) -> List[MenuItem]:
    """
    Filter menu items based on constraints.
    
    Args:
        items: List of menu items to filter
        constraints: Dictionary of constraints including:
            - age: int, customer's age
            - max_alcohol_content: float, maximum alcohol content
            - max_price: float, maximum price
            - dietary_restrictions: List[str], dietary restrictions
    
    Returns:
        List[MenuItem]: Filtered list of menu items
    """
    filtered_items = []
    
    for item in items:
        # Check age restriction
        if constraints.get('age', 21) < 21 and item.alcohol_content and item.alcohol_content > 0:
            continue
            
        # Check alcohol content
        if 'max_alcohol_content' in constraints and item.alcohol_content:
            if item.alcohol_content > constraints['max_alcohol_content']:
                continue
                
        # Check price
        if 'max_price' in constraints:
            if item.price > constraints['max_price']:
                continue
                
        # Check dietary restrictions
        if 'dietary_restrictions' in constraints and item.allergens: 
            allergens = item.allergens.split(',') if isinstance(item.allergens, str) else item.allergens
            if any(restriction in allergens for restriction in constraints['dietary_restrictions']):
                continue
                
        filtered_items.append(item)
    
    return filtered_items
    filtered_items = items
    
    # Filter by age restriction
    if "age" in constraints:
        filtered_items = [
            item for item in filtered_items
            if not item.alcohol_content or constraints["age"] >= 21
        ]
    
    # Filter by alcohol content
    if "max_alcohol_content" in constraints:
        filtered_items = [
            item for item in filtered_items
            if not item.alcohol_content or item.alcohol_content <= constraints["max_alcohol_content"]
        ]
    
    # Filter by price range
    if "max_price" in constraints:
        filtered_items = [
            item for item in filtered_items
            if item.price <= constraints["max_price"]
        ]
    
    return filtered_items

def get_personalized_recommendations(
    user_id: int,
    preferences: Dict[str, Any],
    available_items: List[MenuItem],
    limit: int = 5
) -> List[MenuItem]:
    """
    Get personalized drink recommendations using the recommendation system.
    
    Args:
        user_id: User ID for tracking recommendations
        preferences: Dictionary containing user preferences:
            - preferred_categories: List[str], preferred drink categories
            - preferred_flavors: List[str], preferred flavors
            - preferred_price_range: Tuple[float, float], min and max price
            - alcohol_preference: str, preferred alcohol content level
        available_items: List of available menu items
        limit: Maximum number of recommendations to return
    
    Returns:
        List[MenuItem]: List of recommended menu items
    """
    try:
        # Convert MenuItem objects to format expected by recommendation system
        drink_list: List[Drink] = [
            Drink(
                name=item.name,
                category=item.category,
                abv=item.alcohol_content or 0.0,
                flavor_profile=item.flavor_profile.split(',') if isinstance(item.flavor_profile, str) else item.flavor_profile,
                price=item.price,
                allergens=item.allergens.split(',') if isinstance(item.allergens, str) else (item.allergens or [])
            )
            for item in available_items
        ]
        
        
        # Create customer object expected by recommendation system
        customer = Customer(
            customer_id=str(user_id),
            age=preferences.get('age', 21),
            preferences={
                'flavor': preferences.get('preferred_flavors', []),
                'category': preferences.get('preferred_categories', []),
                'price_range': preferences.get('preferred_price_range'),
                'alcohol': preferences.get('alcohol_preference', 'any')
            },
            restrictions={
                'allergies': preferences.get('allergies', []),
                'dietary': preferences.get('dietary_restrictions', [])
            }
        )
        
        # Use existing recommendation logic
        recommended_drinks = recommend_cocktail(customer, drink_list)
        
        # Map recommended drinks back to MenuItem objects
        recommended_items = [
            item for item in available_items
            if item.name in recommended_drinks
        ]
        
        return recommended_items[:limit]
    except Exception as e:
        print(f"Error in recommendation system: {e}")
        # Fallback to basic scoring system if recommendation fails
        return _fallback_recommendations(preferences, available_items, limit)

def _fallback_recommendations(
    preferences: Dict[str, Any],
    available_items: List[MenuItem],
    limit: int = 5
) -> List[MenuItem]:
    """
    Fallback recommendation system using basic scoring when the main system fails.
    
    Args:
        preferences: Dictionary containing user preferences
        available_items: List of available menu items
        limit: Maximum number of recommendations to return
    
    Returns:
        List[MenuItem]: List of recommended menu items
    """
    scored_items = []
    
    for item in available_items:
        score = 0
        
        # Score based on category preference
        if "preferred_categories" in preferences:
            if item.category in preferences["preferred_categories"]:
                score += 2
        
        # Score based on flavor preferences
        if "preferred_flavors" in preferences and item.flavor_profile:
            item_flavors = item.flavor_profile.split(',') if isinstance(item.flavor_profile, str) else item.flavor_profile
            matching_flavors = set(preferences["preferred_flavors"]) & set(item_flavors)
            score += len(matching_flavors)
        
        # Score based on price preference
        if "preferred_price_range" in preferences and preferences["preferred_price_range"]:
            min_price, max_price = preferences["preferred_price_range"]
            if min_price <= item.price <= max_price:
                score += 1
        
        # Score based on alcohol preference
        if "alcohol_preference" in preferences:
            pref = preferences["alcohol_preference"]
            if pref == "low" and item.alcohol_content and item.alcohol_content <= 5:
                score += 1
            elif pref == "medium" and item.alcohol_content and 5 < item.alcohol_content <= 12:
                score += 1
            elif pref == "high" and item.alcohol_content and item.alcohol_content > 12:
                score += 1
        
        scored_items.append((score, item))
    
    # Sort by score and return top N items
    scored_items.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored_items[:limit]]


def _fallback_similar_items(
    reference_item: MenuItem,
    available_items: List[MenuItem],
    limit: int = 3
) -> List[MenuItem]:
    """
    Fallback similar items system using basic scoring when the main system fails.
    
    Args:
        reference_item: The item to find similar items for
        available_items: List of available menu items
        limit: Maximum number of similar items to return
    
    Returns:
        List[MenuItem]: List of similar menu items
    """
    scored_items = []
    
    for item in available_items:
        if item.id == reference_item.id:
            continue
        
        score = 0
        
        # Same category
        if item.category == reference_item.category:
            score += 2
        
        # Similar price range (within 20%)
        price_diff = abs(item.price - reference_item.price) / reference_item.price
        if price_diff <= 0.2:
            score += 1
        
        # Similar alcohol content
        if item.alcohol_content and reference_item.alcohol_content:
            alcohol_diff = abs(item.alcohol_content - reference_item.alcohol_content)
            if alcohol_diff <= 2:  # Within 2% ABV
                score += 1
        
        # Matching flavors
        if item.flavor_profile and reference_item.flavor_profile:
            item_flavors = item.flavor_profile.split(',') if isinstance(item.flavor_profile, str) else item.flavor_profile
            ref_flavors = reference_item.flavor_profile.split(',') if isinstance(reference_item.flavor_profile, str) else reference_item.flavor_profile
            matching_flavors = set(item_flavors) & set(ref_flavors)
            score += len(matching_flavors)
        
        scored_items.append((score, item))
    
    # Sort by score and return top N items
    scored_items.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored_items[:limit]]


def get_similar_items(
    reference_item: MenuItem,
    available_items: List[MenuItem],
    limit: int = 3
) -> List[MenuItem]:
    """
    Find items similar to a reference item using the recommendation system.
    
    Args:
        reference_item: The item to find similar items for
        available_items: List of available menu items
        limit: Maximum number of similar items to return
    
    Returns:
        List[MenuItem]: List of similar menu items
    """
    try: 
        # Convert reference item to preferences
        preferences = {
            'flavor': reference_item.flavor_profile.split(',') if isinstance(reference_item.flavor_profile, str) else reference_item.flavor_profile,
            'category': [reference_item.category],
            'price_range': [
                reference_item.price * 0.8,  # 20% price range
                reference_item.price * 1.2
            ],
            'alcohol': str(reference_item.alcohol_content) if reference_item.alcohol_content else 'any'
        }
        
        # Convert available items to format expected by recommendation system
        drink_list: List[Drink] = [
            Drink(
                name=item.name,
                category=item.category,
                abv=item.alcohol_content or 0.0,
                flavor_profile=item.flavor_profile.split(',') if isinstance(item.flavor_profile, str) else item.flavor_profile,
                price=item.price,
                allergens=item.allergens.split(',') if isinstance(item.allergens, str) else (item.allergens or [])
            )
            for item in available_items
            if item.id != reference_item.id  # Exclude reference item
        ]
        
        # Create a dummy customer with the reference item's preferences
        customer = Customer(
            customer_id='similar_items',
            age=21,  # Default to adult for similar items
            preferences=preferences,
            restrictions={'allergies': [], 'dietary': []}  # No restrictions for similar items
        )
        
        # Use existing recommendation logic
        recommended_drinks = recommend_cocktail(customer, drink_list)
        
        # Map recommended drinks back to MenuItem objects
        similar_items = [
            item for item in available_items
            if item.name in recommended_drinks and item.id != reference_item.id
        ]
        
        return similar_items[:limit]
    except Exception as e:
        logger.error(f"Error in recommendation system: {e}")
        # Fallback to basic similarity scoring if recommendation fails
        return _fallback_similar_items(reference_item, available_items, limit)
