"""Bar recommendation agent implementation module."""
from typing import List, Dict, Any, Optional

from .models import Customer, Drink
from .recommendations import (
    recommend_cocktail,
    recommend_combo,
    recommend_by_inventory,
    recommend_group_package,
    get_seasonal_recommendations
)
from .constraints import (
    check_legal_restrictions,
    check_health_safety,
    apply_brand_strategy,
    apply_profit_optimization,
    apply_customer_satisfaction
)

class Agent:
    """Bar recommendation agent for the DevinShao01 project."""
    
    def __init__(self, name: str):
        """Initialize the agent with a name.
        
        Args:
            name: The name of the agent.
        """
        self.name = name
    
    def greet(self) -> str:
        """Return a greeting from the agent.
        
        Returns:
            str: A greeting message including the agent's name.
        """
        return f"Hello! I am {self.name}, an agent in the DevinShao01 project."

    def get_recommendations(
        self,
        customer: Customer,
        drinks: List[Drink],
        inventory: Dict[str, int],
        costs: Dict[str, float],
        brand_priorities: Dict[str, float],
        feedback_history: Dict[str, float],
        rejection_history: List[str],
        consumption_history: List[Dict[str, Any]],
        combo_definitions: Optional[Dict[str, Dict[str, Any]]] = None,
        packages: Optional[Dict[str, Dict[str, Any]]] = None,
        group_size: int = 1,
        current_season: Optional[str] = None
    ) -> Dict[str, List[Any]]:
        """Generate comprehensive drink recommendations for a customer.

        Args:
            customer: Customer object with preferences and restrictions
            drinks: List of available drinks
            inventory: Current inventory levels
            costs: Production costs for drinks
            brand_priorities: Brand partnership priority scores
            feedback_history: Customer ratings for drinks
            rejection_history: Recently rejected recommendations
            consumption_history: Recent drink consumption
            combo_definitions: Available combo definitions
            packages: Available group packages
            group_size: Number of people (for group orders)
            current_season: Current season for seasonal recommendations

        Returns:
            Dict containing different types of recommendations
        """
        # Apply business constraints
        legal_drinks = [
            drink for drink in drinks
            if check_legal_restrictions(customer, drink)
        ]
        
        safe_drinks = [
            drink for drink in legal_drinks
            if check_health_safety(customer, drink, consumption_history)
        ]
        
        # Apply brand strategy
        prioritized_drinks = apply_brand_strategy(safe_drinks, brand_priorities)
        
        # Apply profit optimization
        profitable_drinks = apply_profit_optimization(
            prioritized_drinks,
            costs,
            inventory
        )
        
        # Apply customer satisfaction rules
        recommended_drinks = apply_customer_satisfaction(
            customer,
            profitable_drinks,
            feedback_history,
            rejection_history
        )

        # Generate different types of recommendations
        recommendations = {
            "cocktails": recommend_cocktail(customer, recommended_drinks),
            "inventory_based": recommend_by_inventory(
                customer,
                recommended_drinks,
                inventory
            )
        }

        # Add seasonal recommendations if season is specified
        if current_season:
            recommendations["seasonal"] = get_seasonal_recommendations(
                customer,
                recommended_drinks,
                current_season
            )

        # Add combo recommendations if definitions are provided
        if combo_definitions:
            recommendations["combos"] = recommend_combo(
                customer,
                recommended_drinks,
                combo_definitions
            )

        # Add group packages if applicable
        if packages and group_size > 1:
            recommendations["group_packages"] = recommend_group_package(
                group_size,
                customer,
                recommended_drinks,
                packages
            )

        return recommendations
