from typing import Dict, List


class PromptTemplates:
    """Collection of prompt templates for different conversation scenarios."""
    
    @staticmethod
    def get_drink_recommendation_prompt(preferences: Dict) -> List[Dict[str, str]]:
        """Generate prompt for drink recommendations."""
        return [
            {
                "role": "system",
                "content": """You are a knowledgeable bartender who understands various drinks and can make personalized recommendations. 
                Consider the customer's preferences and any restrictions when making suggestions."""
            },
            {
                "role": "user",
                "content": f"""Based on these preferences: {preferences},
                suggest 3 drinks that would be perfect for this customer. 
                For each drink, explain why it matches their preferences."""
            }
        ]
    
    @staticmethod
    def get_drink_info_prompt(drink_name: str) -> List[Dict[str, str]]:
        """Generate prompt for detailed drink information."""
        return [
            {
                "role": "system",
                "content": """You are a knowledgeable bartender who can explain drinks in detail. 
                Include information about ingredients, preparation method, and interesting facts."""
            },
            {
                "role": "user",
                "content": f"Tell me about the drink '{drink_name}'. What's in it and how is it made?"
            }
        ]
    
    @staticmethod
    def get_pairing_suggestion_prompt(drink: str, context: str = "") -> List[Dict[str, str]]:
        """Generate prompt for food pairing suggestions."""
        return [
            {
                "role": "system",
                "content": """You are a culinary expert who understands drink and food pairings. 
                Suggest complementary food items that would enhance the drinking experience."""
            },
            {
                "role": "user",
                "content": f"""What food would pair well with {drink}? {context}
                Suggest 2-3 specific items and explain why they would work well together."""
            }
        ]
    
    @staticmethod
    def get_social_suggestion_prompt(context: Dict) -> List[Dict[str, str]]:
        """Generate prompt for social interaction suggestions."""
        return [
            {
                "role": "system",
                "content": """You are a social expert who can suggest ways to enhance the bar experience. 
                Consider the context and provide relevant social suggestions."""
            },
            {
                "role": "user",
                "content": f"""Given this context: {context},
                suggest some ways to make the experience more enjoyable. 
                Consider both drink choices and social interaction opportunities."""
            }
        ]
