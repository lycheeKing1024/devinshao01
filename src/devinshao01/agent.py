"""Basic agent implementation module."""

class Agent:
    """Base agent class for the DevinShao01 project."""
    
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
