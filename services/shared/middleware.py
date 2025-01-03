from fastapi import Request, HTTPException, status
import jwt
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceAuthMiddleware:
    """Middleware for service-to-service authentication."""
    
    def __init__(self):
        self.secret_key = os.getenv('INTER_SERVICE_SECRET', 'your-secret-key')
        self.allowed_services = {'user', 'order', 'ai', 'live'}
        
    async def __call__(self, request: Request, call_next):
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
            
        try:
            # Verify service token
            token = self._extract_token(request)
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing service token"
                )
                
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            service_name = payload.get('service')
            
            if service_name not in self.allowed_services:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid service"
                )
                
            # Add service info to request state
            request.state.service_name = service_name
            return await call_next(request)
            
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service token"
            )
        except Exception as e:
            logger.error(f"Error in service auth middleware: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
            
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from Authorization header."""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        return auth_header.split(' ')[1]
        
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)."""
        public_paths = {
            '/health',
            '/metrics',
            '/docs',
            '/openapi.json'
        }
        return any(path.startswith(p) for p in public_paths)
