import pytest
from ..qr_service import QRService
import json
import base64
from PIL import Image
from io import BytesIO

@pytest.fixture
def qr_service():
    return QRService()


def test_generate_qr():
    """Test QR code generation."""
    test_data = {"test": "data", "number": 123}
    qr_code = QRService.generate_qr(test_data)
    
    # Verify it's a valid base64 PNG
    assert qr_code.startswith("data:image/png;base64,")
    
    # Extract and decode base64 data
    base64_data = qr_code.split(",")[1]
    image_data = base64.b64decode(base64_data)
    
    # Verify it's a valid image
    image = Image.open(BytesIO(image_data))
    assert image.format == "PNG"

def test_generate_and_scan_qr():
    """Test QR code generation and scanning."""
    test_data = {"test": "data", "number": 123}
    
    # Generate QR code
    qr_code = QRService.generate_qr(test_data)
    
    # Convert base64 to bytes
    image_data = base64.b64decode(qr_code.split(",")[1])
    
    # Scan QR code
    decoded_data = QRService.scan_qr(image_data)
    
    assert decoded_data == test_data

def test_generate_table_qr():
    """Test table QR code generation."""
    table_id = 1
    venue_id = 2
    additional_data = {"section": "outdoor"}
    
    qr_code = QRService.generate_table_qr(table_id, venue_id, additional_data)
    
    # Convert and scan
    image_data = base64.b64decode(qr_code.split(",")[1])
    decoded_data = QRService.scan_qr(image_data)
    
    assert decoded_data["type"] == "table"
    assert decoded_data["table_id"] == table_id
    assert decoded_data["venue_id"] == venue_id
    assert decoded_data["section"] == "outdoor"

def test_generate_menu_item_qr():
    """Test menu item QR code generation."""
    item_id = 1
    venue_id = 2
    additional_data = {"category": "drinks"}
    
    qr_code = QRService.generate_menu_item_qr(item_id, venue_id, additional_data)
    
    # Convert and scan
    image_data = base64.b64decode(qr_code.split(",")[1])
    decoded_data = QRService.scan_qr(image_data)
    
    assert decoded_data["type"] == "menu_item"
    assert decoded_data["item_id"] == item_id
    assert decoded_data["venue_id"] == venue_id
    assert decoded_data["category"] == "drinks"
