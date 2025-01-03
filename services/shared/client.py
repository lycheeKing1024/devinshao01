from typing import Dict, Any, Optional
import httpx
import os
import jwt
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceClient:
    """Client for inter-service communication."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.base_urls = {
            'user': os.getenv('USER_SERVICE_URL', 'http://user-service:8001'),
            'order': os.getenv('ORDER_SERVICE_URL', 'http://order-service:8002'),
            'ai': os.getenv('AI_SERVICE_URL', 'http://ai-service:8003'),
            'live': os.getenv('LIVE_SERVICE_URL', 'http://live-service:8004')
        }
        self.secret_key = os.getenv('INTER_SERVICE_SECRET', 'your-secret-key')
        
    def _generate_service_token(self) -> str:
        """Generate JWT token for service-to-service auth."""
        payload = {
            'service': self.service_name,
            'exp': datetime.utcnow() + timedelta(minutes=5)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
        
    async def _make_request(
        self,
        method: str,
        service: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to another service."""
        if service not in self.base_urls:
            raise ValueError(f"Unknown service: {service}")
            
        url = f"{self.base_urls[service]}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self._generate_service_token()}',
            'X-Service-Name': self.service_name
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during service communication: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during service communication: {str(e)}")
            raise
            
    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile from user service."""
        return await self._make_request('GET', 'user', f'/users/{user_id}/profile')
        
    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences from user service."""
        return await self._make_request('GET', 'user', f'/users/{user_id}/preferences')
        
    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content using AI service."""
        return await self._make_request('POST', 'ai', '/moderate/text', {'text': content})
        
    async def get_recommendations(
        self,
        user_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get drink recommendations from order service."""
        return await self._make_request(
            'POST',
            'order',
            '/recommendations',
            {
                'user_id': user_id,
                'context': context or {}
            }
        )
        
    async def create_room(
        self,
        name: str,
        owner_id: int,
        room_type: str
    ) -> Dict[str, Any]:
        """Create a new room in live service."""
        return await self._make_request(
            'POST',
            'live',
            '/rooms',
            {
                'name': name,
                'owner_id': owner_id,
                'room_type': room_type
            }
        )
