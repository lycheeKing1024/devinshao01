"""Unit tests for the bar recommendation system."""
import unittest
from typing import List

from devinshao01.models import Customer, Drink
from devinshao01.recommendations import (
    recommend_cocktail,
    recommend_combo,
    recommend_by_inventory,
    get_seasonal_recommendations
)


class TestRecommendations(unittest.TestCase):
    """Test cases for recommendation functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample drinks
        self.mojito = Drink(
            name="Mojito",
            category="cocktail",
            abv=12.0,
            flavor_profile=["refreshing", "minty", "sweet"],
            price=12.99
        )
        
        self.margarita = Drink(
            name="Margarita",
            category="cocktail",
            abv=15.0,
            flavor_profile=["citrus", "sour", "refreshing"],
            price=11.99
        )
        
        self.mocktail = Drink(
            name="Virgin Colada",
            category="mocktail",
            abv=0.0,
            flavor_profile=["sweet", "tropical", "creamy"],
            price=8.99
        )
        
        self.drink_list: List[Drink] = [
            self.mojito,
            self.margarita,
            self.mocktail
        ]
        
        # Sample customers
        self.adult_customer = Customer(
            customer_id="C001",
            age=25,
            preferences={"flavor": ["sweet", "refreshing"]},
            restrictions={"allergies": []}
        )
        
        self.underage_customer = Customer(
            customer_id="C002",
            age=18,
            preferences={"flavor": ["sweet", "tropical"]},
            restrictions={"allergies": []}
        )

    def test_recommend_cocktail_for_adult(self):
        """Test cocktail recommendations for adult customer."""
        recommendations = recommend_cocktail(
            self.adult_customer,
            self.drink_list
        )
        
        # Should recommend Mojito due to matching preferences
        self.assertIn("Mojito", recommendations)
        self.assertEqual(len(recommendations), 1)

    def test_recommend_cocktail_for_underage(self):
        """Test cocktail recommendations for underage customer."""
        recommendations = recommend_cocktail(
            self.underage_customer,
            self.drink_list
        )
        
        # Should only recommend mocktails
        self.assertNotIn("Mojito", recommendations)
        self.assertNotIn("Margarita", recommendations)
        self.assertTrue(all(drink.startswith("Mocktail") 
                          for drink in recommendations))

    def test_recommend_by_inventory(self):
        """Test inventory-based recommendations."""
        inventory = {
            "Mojito": 10,
            "Margarita": 3,
            "Virgin Colada": 8
        }
        
        recommendations = recommend_by_inventory(
            self.adult_customer,
            self.drink_list,
            inventory,
            min_stock=5
        )
        
        # Should recommend drinks with stock > 5
        self.assertIn("Mojito", recommendations)
        self.assertIn("Virgin Colada", recommendations)
        self.assertNotIn("Margarita", recommendations)

    def test_seasonal_recommendations_summer(self):
        """Test seasonal recommendations for summer."""
        recommendations = get_seasonal_recommendations(
            self.adult_customer,
            self.drink_list,
            "summer"
        )
        
        # Should recommend refreshing drinks
        self.assertIn("Mojito", recommendations)
        self.assertIn("Margarita", recommendations)

    def test_combo_recommendations(self):
        """Test combo recommendations."""
        combo_definitions = {
            "Tropical Paradise": {
                "drinks": ["Mojito", "Virgin Colada"],
                "description": "Refreshing tropical combo",
                "price": 19.99,
                "allergens": []
            }
        }
        
        recommendations = recommend_combo(
            self.adult_customer,
            self.drink_list,
            combo_definitions
        )
        
        # Should recommend the combo
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["name"], "Tropical Paradise")


if __name__ == '__main__':
    unittest.main()
