from typing import Dict, Any, Optional
import qrcode
from io import BytesIO
import base64
import json
import logging
from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QRService:
    """Service for handling QR code generation and scanning."""
    
    @staticmethod
    def generate_qr(
        data: Dict[str, Any],
        size: int = 10,
        border: int = 4
    ) -> str:
        """
        Generate QR code from data.
        
        Args:
            data: Dictionary containing data to encode
            size: Size of QR code
            border: Border size
            
        Returns:
            Base64 encoded QR code image
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data)
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
            qr.add_data(json_data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise
            
    @staticmethod
    def scan_qr(image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Scan QR code from image data.
        
        Args:
            image_data: Raw image data
            
        Returns:
            Dictionary containing decoded data or None if no QR code found
        """
        try:
            # Convert bytes to image
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # Decode QR code
            decoded_objects = decode(pil_image)
            
            if not decoded_objects:
                return None
                
            # Get first QR code
            qr_data = decoded_objects[0].data.decode('utf-8')
            
            try:
                # Parse JSON data
                return json.loads(qr_data)
            except json.JSONDecodeError:
                # Return raw string if not JSON
                return {"raw_data": qr_data}
                
        except Exception as e:
            logger.error(f"Error scanning QR code: {str(e)}")
            return None
            
    @staticmethod
    def generate_table_qr(
        table_id: int,
        venue_id: int,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate QR code for a specific table.
        
        Args:
            table_id: ID of the table
            venue_id: ID of the venue
            additional_data: Additional data to include
            
        Returns:
            Base64 encoded QR code image
        """
        data = {
            "type": "table",
            "table_id": table_id,
            "venue_id": venue_id,
            **(additional_data or {})
        }
        return QRService.generate_qr(data)
        
    @staticmethod
    def generate_menu_item_qr(
        item_id: int,
        venue_id: int,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate QR code for a menu item.
        
        Args:
            item_id: ID of the menu item
            venue_id: ID of the venue
            additional_data: Additional data to include
            
        Returns:
            Base64 encoded QR code image
        """
        data = {
            "type": "menu_item",
            "item_id": item_id,
            "venue_id": venue_id,
            **(additional_data or {})
        }
        return QRService.generate_qr(data)
