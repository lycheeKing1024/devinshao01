"""Basic functionality test script for the bar recommendation system."""
import unittest
from devinshao01.agent import Agent
from devinshao01.models import Customer, Drink


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of the recommendation system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test drinks
        self.drinks = [
        Drink(
            name="Sweet Martini",
            category="cocktail",
            abv=20.0,
            flavor_profile=["sweet", "fruity"],
            price=14.99
        ),
        Drink(
            name="Nutty Alexander",
            category="cocktail",
            abv=15.0,
            flavor_profile=["sweet", "nutty"],
            price=13.99,
            allergens=["nuts"]
        ),
        Drink(
            name="Virgin Smoothie",
            category="mocktail",
            abv=0.0,
            flavor_profile=["sweet", "fruity"],
            price=8.99
        )
    ]

        # Test data
        self.inventory = {
        "Sweet Martini": 10,
        "Nutty Alexander": 5,
        "Virgin Smoothie": 8
    }
    
        self.costs = {
        "Sweet Martini": 5.99,
        "Nutty Alexander": 6.99,
        "Virgin Smoothie": 3.99
    }
    
        self.brand_priorities = {
        "Premium": 1.0,
        "Standard": 0.5
    }
    
        self.combo_definitions = {
        "Sweet Duo": {
            "drinks": ["Sweet Martini", "Virgin Smoothie"],
            "description": "Sweet combination",
            "price": 19.99,
            "allergens": []
        }
    }

        # Create test customers
        self.adult_customer = Customer(
        customer_id="TEST001",
        age=25,
        preferences={"flavor": ["sweet", "fruity"]},
        restrictions={"allergies": []}
    )
    
        self.underage_customer = Customer(
        customer_id="TEST002",
        age=18,
        preferences={"flavor": ["sweet"]},
        restrictions={"allergies": []}
    )
    
        self.allergic_customer = Customer(
        customer_id="TEST003",
        age=30,
        preferences={"flavor": ["sweet"]},
        restrictions={"allergies": ["nuts"]}
    )

        # Create agent
        self.agent = Agent("TestAgent")

    def test_adult_recommendations(self):
        """Test recommendations for adult customers."""
        adult_recommendations = self.agent.get_recommendations(
            customer=self.adult_customer,
            drinks=self.drinks,
            inventory=self.inventory,
            costs=self.costs,
            brand_priorities=self.brand_priorities,
            feedback_history={},
            rejection_history=[],
            consumption_history=[],
            combo_definitions=self.combo_definitions
        )
        print("Adult recommendations:", adult_recommendations)
        self.assertIn("Sweet Martini", adult_recommendations["cocktails"],
                     "Adult should get cocktail recommendations")

    def test_underage_recommendations(self):
        """Test recommendations for underage customers."""
        underage_recommendations = self.agent.get_recommendations(
            customer=self.underage_customer,
            drinks=self.drinks,
            inventory=self.inventory,
            costs=self.costs,
            brand_priorities=self.brand_priorities,
            feedback_history={},
            rejection_history=[],
            consumption_history=[],
            combo_definitions=self.combo_definitions
        )
        print("Underage recommendations:", underage_recommendations)
        self.assertTrue(all(drink.startswith("Virgin") 
                          for drink in underage_recommendations["cocktails"]),
                       "Underage should only get non-alcoholic recommendations")

    def test_allergic_recommendations(self):
        """Test recommendations for customers with allergies."""
        allergic_recommendations = self.agent.get_recommendations(
            customer=self.allergic_customer,
            drinks=self.drinks,
            inventory=self.inventory,
            costs=self.costs,
            brand_priorities=self.brand_priorities,
            feedback_history={},
            rejection_history=[],
            consumption_history=[],
            combo_definitions=self.combo_definitions
        )
        print("Allergic customer recommendations:", allergic_recommendations)
        self.assertNotIn("Nutty Alexander", allergic_recommendations["cocktails"],
                        "Allergic customer should not get recommendations with allergens")


if __name__ == "__main__":
    unittest.main()
