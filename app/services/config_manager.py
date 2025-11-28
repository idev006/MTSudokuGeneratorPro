import json
import os
from typing import Dict, Any
from app.models.settings import GenerationConfig, Difficulty

class ConfigManager:
    """
    Singleton class to manage application settings.
    Acts as the Single Source of Truth (SSOT).
    """
    _instance = None
    _settings: Dict[str, Any] = {}
    
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Loads settings from JSON file."""
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, 'r') as f:
                    self._settings = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                # Fallback to empty or defaults if needed
        else:
            print(f"Config file not found at {self.CONFIG_PATH}")

    def get_difficulty_config(self, difficulty: Difficulty) -> Dict[str, int]:
        """Returns the min/max empty cells for a given difficulty."""
        key = difficulty.value # 'easy', 'medium', etc.
        presets = self._settings.get("difficulty_presets", {})
        defaults = self._settings.get("defaults", {"empty_ratio_min": 0.45, "empty_ratio_max": 0.55})
        return presets.get(key, defaults)

    def get_app_setting(self, key: str, default=None):
        return self._settings.get("app_settings", {}).get(key, default)

    def set_app_setting(self, key: str, value: Any):
        """Sets an app setting and saves to file."""
        if "app_settings" not in self._settings:
            self._settings["app_settings"] = {}
        self._settings["app_settings"][key] = value
        self._save_config()

    def _save_config(self):
        try:
            with open(self.CONFIG_PATH, 'w') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_visual_setting(self, key: str, default=None):
        """Returns a visual setting value (e.g. gray_color, gray_margin)."""
        return self._settings.get("visual_settings", {}).get(key, default)

    def get_font_path(self, font_key: str = "thai_font") -> str:
        """
        Gets the full path to the configured font.
        font_key: 'thai_font' or 'english_font'
        """
        font_filename = self._settings.get("font_settings", {}).get(font_key)
        if not font_filename:
            return None
            
        # Construct full path: app/services/config_manager.py -> app/assets/fonts
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(current_dir)
        font_path = os.path.join(app_dir, 'assets', 'fonts', font_filename)
        
        if os.path.exists(font_path):
            return font_path
        
        print(f"Warning: Font file not found at {font_path}")
        return None

    def reload(self):
        self._load_config()
