import pytest
from unittest.mock import patch, AsyncMock
from ..client import ServiceClient
import jwt
from datetime import datetime, timedelta

@pytest.fixture
def service_client():
    return ServiceClient('test-service')

@pytest.mark.asyncio
async def test_generate_service_token(service_client):
    """Test service token generation."""
    token = service_client._generate_service_token()
    payload = jwt.decode(token, service_client.secret_key, algorithms=['HS256'])
    
    assert payload['service'] == 'test-service'
    assert datetime.fromtimestamp(payload['exp']) > datetime.utcnow()

@pytest.mark.asyncio
async def test_make_request_success(service_client):
    """Test successful service request."""
    mock_response = {'data': 'test'}
    
    with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value.json.return_value = mock_response
        mock_request.return_value.raise_for_status = AsyncMock()
        
        response = await service_client._make_request(
            'GET',
            'user',
            '/test',
            {'param': 'value'}
        )
        
        assert response == mock_response
        mock_request.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_profile(service_client):
    """Test get user profile request."""
    mock_profile = {'id': 1, 'name': 'Test User'}
    
    with patch.object(
        service_client,
        '_make_request',
        new_callable=AsyncMock
    ) as mock_request:
        mock_request.return_value = mock_profile
        
        profile = await service_client.get_user_profile(1)
        
        assert profile == mock_profile
        mock_request.assert_called_with('GET', 'user', '/users/1/profile')

@pytest.mark.asyncio
async def test_moderate_content(service_client):
    """Test content moderation request."""
    mock_result = {'is_appropriate': True}
    
    with patch.object(
        service_client,
        '_make_request',
        new_callable=AsyncMock
    ) as mock_request:
        mock_request.return_value = mock_result
        
        result = await service_client.moderate_content('test content')
        
        assert result == mock_result
        mock_request.assert_called_with(
            'POST',
            'ai',
            '/moderate/text',
            {'text': 'test content'}
        )
