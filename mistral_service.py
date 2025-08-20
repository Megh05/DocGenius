"""
Mistral AI integration for OCR enhancement and field validation
"""
import os
import logging
import requests
import base64
import json
from typing import Dict, Any, Optional, List
from PIL import Image
import io

class MistralService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.environ.get('MISTRAL_API_KEY')
        self.base_url = "https://api.mistral.ai/v1"
        
    def test_connection(self, api_key: str = None) -> Dict[str, Any]:
        """Test Mistral API connection"""
        test_key = api_key or self.api_key
        
        if not test_key:
            return {"success": False, "error": "No API key provided"}
            
        headers = {
            "Authorization": f"Bearer {test_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            if response.status_code == 200:
                models = response.json()
                return {
                    "success": True, 
                    "message": "Connection successful",
                    "models_available": len(models.get('data', []))
                }
            else:
                return {
                    "success": False, 
                    "error": f"API returned status {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection failed: {str(e)}"}
    
    def enhance_ocr_extraction(self, image_path: str, existing_text: str = "") -> str:
        """Use Mistral vision model to enhance OCR text extraction"""
        if not self.api_key:
            self.logger.warning("Mistral API key not available for OCR enhancement")
            return existing_text
            
        try:
            # Convert image to base64
            with open(image_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            
            prompt = """Please extract ALL text content from this document image with high accuracy. 
            Pay special attention to:
            - Product names, chemical names, and INCI names
            - CAS numbers and molecular formulas
            - Test results, specifications, and numerical values
            - Company names and contact information
            - Dates, batch numbers, and lot numbers
            - Table data with proper formatting
            
            Return the extracted text exactly as it appears, maintaining the original structure and formatting."""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "pixtral-12b-2409",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 4000
            }
            
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                enhanced_text = result['choices'][0]['message']['content']
                self.logger.info(f"Mistral OCR enhanced text: {len(enhanced_text)} characters")
                return enhanced_text
            else:
                self.logger.error(f"Mistral OCR failed: {response.status_code} - {response.text}")
                return existing_text
                
        except Exception as e:
            self.logger.error(f"Mistral OCR enhancement failed: {str(e)}")
            return existing_text
    
    def validate_and_correct_fields(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Mistral LLM to validate and correct extracted field data"""
        if not self.api_key:
            self.logger.warning("Mistral API key not available for field validation")
            return extracted_data
            
        try:
            prompt = f"""
            Please validate and correct the following extracted chemical document data. 
            Look for common OCR errors and inconsistencies:

            Extracted Data:
            {json.dumps(extracted_data, indent=2)}

            Please check and correct:
            1. Product names - ensure proper chemical nomenclature
            2. CAS numbers - validate format (XXXXX-XX-X)
            3. INCI names - verify cosmetic ingredient naming standards
            4. Molecular formulas - check chemical formula syntax
            5. Test values - ensure proper units and ranges
            6. Company names - fix any OCR spelling errors
            7. Dates - standardize format (YYYY-MM-DD)

            Return the corrected data in the same JSON structure. 
            Only modify fields that contain clear errors. 
            Add a "validation_notes" field explaining any corrections made.
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "mistral-large-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                corrected_text = result['choices'][0]['message']['content']
                
                # Try to parse the JSON response
                try:
                    # Extract JSON from response (handling markdown code blocks)
                    if '```json' in corrected_text:
                        json_start = corrected_text.find('```json') + 7
                        json_end = corrected_text.find('```', json_start)
                        json_str = corrected_text[json_start:json_end].strip()
                    else:
                        json_str = corrected_text.strip()
                    
                    corrected_data = json.loads(json_str)
                    self.logger.info("Mistral field validation completed successfully")
                    return corrected_data
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse Mistral validation response: {e}")
                    return extracted_data
            else:
                self.logger.error(f"Mistral validation failed: {response.status_code} - {response.text}")
                return extracted_data
                
        except Exception as e:
            self.logger.error(f"Mistral field validation failed: {str(e)}")
            return extracted_data