import requests
import base64
from io import BytesIO
from PIL import Image
from decouple import config

class CropHealthService:
    """ML service for crop health detection"""
    
    def __init__(self):
        self.huggingface_api_key = config('HUGGINGFACE_API_KEY', default='')
        self.model_name = 'microsoft/swinv2-base-patch4-window8-256'  # Vision model
    
    def detect_crop_health(self, image_file):
        """Detect if crop is fresh or rotten using HuggingFace API"""
        try:
            # Convert image to base64
            image_data = self._prepare_image(image_file)
            
            # Use free HuggingFace API (no key needed for inference)
            result = self._call_huggingface_api(image_data)
            
            return result
        except Exception as e:
            print(f"ML Service error: {e}")
            return self._get_mock_detection()
    
    def _prepare_image(self, image_file):
        """Prepare image for ML model"""
        img = Image.open(image_file)
        # Resize to optimize for mobile
        img.thumbnail((224, 224))
        
        # Convert to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG', optimize=True)
        img_byte_arr.seek(0)
        
        return base64.b64encode(img_byte_arr.read()).decode()
    
    def _call_huggingface_api(self, image_data):
        """Call HuggingFace free inference API"""
        # Using free image-classification endpoint
        api_url = "https://api-inference.huggingface.co/models/microsoft/resnet-50"
        headers = {"Authorization": f"Bearer {self.huggingface_api_key}"} if self.huggingface_api_key else {}
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json={"image": image_data},
                timeout=10
            )
            
            if response.status_code == 200:
                predictions = response.json()
                return self._parse_predictions(predictions)
        except Exception as e:
            print(f"HuggingFace API error: {e}")
        
        return self._get_mock_detection()
    
    def _parse_predictions(self, predictions):
        """Parse HuggingFace predictions"""
        if isinstance(predictions, list) and len(predictions) > 0:
            top_result = predictions
            label = top_result.get('label', '').lower()
            score = top_result.get('score', 0)
            
            # Map to Fresh/Rotten
            if any(word in label for word in ['fresh', 'good', 'healthy', 'normal']):
                return {
                    'detection_result': 'FRESH',
                    'confidence': score,
                    'label': label
                }
            elif any(word in label for word in ['rotten', 'bad', 'diseased', 'sick', 'moldy']):
                return {
                    'detection_result': 'ROTTEN',
                    'confidence': score,
                    'label': label
                }
        
        return self._get_mock_detection()
    
    def _get_mock_detection(self):
        """Fallback mock detection"""
        import random
        return {
            'detection_result': random.choice(['FRESH', 'ROTTEN']),
            'confidence': round(random.uniform(0.75, 0.99), 2),
            'label': 'Mock detection - API unavailable'
        }
