"""Business constraints and rules for the bar recommendation system."""
from typing import List, Dict, Any
from .models import Drink, Customer


def check_legal_restrictions(customer: Customer, drink: Drink) -> bool:
    """Check if a drink can be legally served to a customer.

    Args:
        customer: Customer object
        drink: Drink object

    Returns:
        bool: True if the drink can be legally served
    """
    # Age verification
    if customer.age < 21 and drink.abv > 0:
        return False
    return True


def check_health_safety(customer: Customer, drink: Drink,
                       consumption_history: List[Dict[str, Any]]) -> bool:
    """Check health and safety constraints for serving a drink.

    Args:
        customer: Customer object
        drink: Drink object
        consumption_history: List of customer's recent drink orders

    Returns:
        bool: True if the drink is safe to serve
    """
    # Check for allergens
    customer_allergens = customer.restrictions.get('allergies', [])
    if any(allergen in drink.allergens for allergen in customer_allergens):
        return False

    # Calculate total alcohol units consumed recently
    recent_alcohol_units = sum(
        order.get('alcohol_units', 0) for order in consumption_history
    )
    
    # Avoid high-proof drinks if customer has had multiple drinks
    if recent_alcohol_units > 3 and drink.abv > 30:
        return False
    
    return True


def apply_brand_strategy(drinks: List[Drink],
                        brand_priorities: Dict[str, float]) -> List[Drink]:
    """Apply brand partnership and marketing strategy to drink recommendations.

    Args:
        drinks: List of drink objects
        brand_priorities: Dictionary mapping brands to priority scores

    Returns:
        List[Drink]: Sorted list of drinks based on brand priorities
    """
    def get_priority_score(drink: Drink) -> float:
        # Get brand from drink name or category
        for brand in brand_priorities:
            if brand.lower() in drink.name.lower():
                return brand_priorities[brand]
        return 0.0
    
    # Sort drinks by brand priority
    return sorted(drinks, key=get_priority_score, reverse=True)


def apply_profit_optimization(drinks: List[Drink],
                            costs: Dict[str, float],
                            inventory: Dict[str, int],
                            min_profit_margin: float = 0.3,
                            min_stock: int = 5) -> List[Drink]:
    """Filter and sort drinks based on profit margins and inventory levels.

    Args:
        drinks: List of drink objects
        costs: Dictionary mapping drink names to their cost prices
        inventory: Dictionary mapping drink names to stock levels
        min_profit_margin: Minimum acceptable profit margin
        min_stock: Minimum stock level for recommendation

    Returns:
        List[Drink]: Filtered and sorted list of drinks
    """
    profitable_drinks = []
    
    for drink in drinks:
        # Skip if insufficient stock
        if inventory.get(drink.name, 0) < min_stock:
            continue
            
        # Calculate profit margin
        cost = costs.get(drink.name, 0)
        if cost == 0:  # Avoid division by zero
            continue
            
        margin = (drink.price - cost) / drink.price
        
        # Only include drinks with acceptable margin
        if margin >= min_profit_margin:
            profitable_drinks.append((drink, margin))
    
    # Sort by profit margin (highest first)
    profitable_drinks.sort(key=lambda x: x[1], reverse=True)
    
    return [drink for drink, _ in profitable_drinks]


def apply_customer_satisfaction(customer: Customer,
                              drinks: List[Drink],
                              feedback_history: Dict[str, float],
                              rejection_history: List[str],
                              min_rating: float = 4.0) -> List[Drink]:
    """Filter drinks based on customer satisfaction metrics.

    Args:
        customer: Customer object
        drinks: List of drink objects
        feedback_history: Dictionary mapping drink names to average ratings
        rejection_history: List of recently rejected drink recommendations
        min_rating: Minimum acceptable rating

    Returns:
        List[Drink]: Filtered list of drinks
    """
    # Remove recently rejected recommendations
    filtered_drinks = [
        drink for drink in drinks
        if drink.name not in rejection_history
    ]
    
    # Filter by minimum rating threshold
    rated_drinks = [
        drink for drink in filtered_drinks
        if feedback_history.get(drink.name, 5.0) >= min_rating
    ]
    
    # If too few options, include some drinks just above minimum rating
    if len(rated_drinks) < 3:
        min_rating -= 0.5
        rated_drinks = [
            drink for drink in filtered_drinks
            if feedback_history.get(drink.name, 5.0) >= min_rating
        ]
    
    return rated_drinks
