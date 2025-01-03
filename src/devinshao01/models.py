"""Data models for the bar order recommendation system."""
from typing import List, Dict, Any, Optional


class Drink:
    """Represents a drink item in the bar's menu."""

    def __init__(self, name: str, category: str, abv: float, 
                 flavor_profile: List[str], price: float, allergens: Optional[List[str]] = None):
        """Initialize a drink with its properties.

        Args:
            name: Name of the drink
            category: Type of drink (e.g., 'cocktail', 'beer', 'spirit')
            abv: Alcohol by volume percentage
            flavor_profile: List of flavor characteristics
            price: Price of the drink
            allergens: List of allergens in the drink (optional)
        """
        self.name = name
        self.category = category
        self.abv = abv
        self.flavor_profile = flavor_profile
        self.price = price
        self.allergens = allergens or []


class Customer:
    """Represents a customer with their preferences and restrictions."""

    def __init__(self, customer_id: str, age: int,
                 preferences: Dict[str, Any], restrictions: Dict[str, List[str]]):
        """Initialize a customer with their details.

        Args:
            customer_id: Unique identifier for the customer
            age: Customer's age for legal drinking verification
            preferences: Dictionary of customer preferences (e.g., {'flavor': 'sweet'})
            restrictions: Dictionary of restrictions (e.g., {'allergies': ['nuts']})
        """
        self.customer_id = customer_id
        self.age = age
        self.preferences = preferences
        self.restrictions = restrictions


class Order:
    """Represents an order placed by a customer."""

    def __init__(self, customer: Customer, items: List[Drink]):
        """Initialize an order with customer and items.

        Args:
            customer: Customer object placing the order
            items: List of Drink objects being ordered
        """
        self.customer = customer
        self.items = items
