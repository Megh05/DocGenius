import os
import json
import logging
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages application configuration including API keys"""
    
    def __init__(self):
        self.config_file = 'app_config.json'
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return {}
        return {}
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def get_mistral_api_key(self) -> Optional[str]:
        """Get Mistral API key"""
        return self.config.get('mistral_api_key')
    
    def set_mistral_api_key(self, api_key: str) -> bool:
        """Set Mistral API key"""
        self.config['mistral_api_key'] = api_key
        return self.save_config()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value"""
        self.config[key] = value
        return self.save_config()
    
    def get_mistral_settings(self) -> Dict[str, Any]:
        """Get all Mistral-related settings"""
        return {
            'has_api_key': bool(self.get_mistral_api_key()),
            'enable_mistral_ocr': self.get_setting('enable_mistral_ocr', False),
            'enable_field_validation': self.get_setting('enable_field_validation', False)
        }
    
    def update_mistral_settings(self, settings: Dict[str, Any]) -> bool:
        """Update Mistral settings"""
        success = True
        
        if 'mistral_api_key' in settings and settings['mistral_api_key']:
            success &= self.set_mistral_api_key(settings['mistral_api_key'])
        
        if 'enable_mistral_ocr' in settings:
            success &= self.set_setting('enable_mistral_ocr', settings['enable_mistral_ocr'])
        
        if 'enable_field_validation' in settings:
            success &= self.set_setting('enable_field_validation', settings['enable_field_validation'])
        
        return success

# Global config manager instance
config_manager = ConfigManager()