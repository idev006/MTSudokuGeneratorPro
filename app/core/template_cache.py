"""
Template Cache System
Load and manage pre-generated Jigsaw templates
"""
import json
import os
import random
from typing import List, Dict

class TemplateCache:
    """
    Singleton cache for Jigsaw templates
    Loads templates from disk once and provides fast random access
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TemplateCache, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Cache structure: {size: [ {'regions': [...], 'solution': [...]}, ... ]}
        self._cache_jigsaw = {}
        self._cache_jigsaw_diagonal = {}
        
        self._load_templates()
        self._initialized = True
    
    def _load_templates(self):
        """Load all templates from disk"""
        # Get absolute path to templates directory
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(current_file))
        # project_dir = os.path.dirname(app_dir)
        base_dir = os.path.join(app_dir, 'templates')
        
        # Load Jigsaw 6x6
        self._cache_jigsaw[6] = self._load_from_directory(os.path.join(base_dir, 'jigsaw_6x6'), 6)
        
        # Load Jigsaw 9x9
        self._cache_jigsaw[9] = self._load_from_directory(os.path.join(base_dir, 'jigsaw_9x9'), 9)
        
        # Load Jigsaw Diagonal 9x9
        self._cache_jigsaw_diagonal[9] = self._load_from_directory(os.path.join(base_dir, 'jigsaw_diagonal_9x9'), 9)
        
        print(f"TemplateCache: Loaded {len(self._cache_jigsaw.get(6, []))} Jigsaw 6×6")
        print(f"TemplateCache: Loaded {len(self._cache_jigsaw.get(9, []))} Jigsaw 9×9")
        print(f"TemplateCache: Loaded {len(self._cache_jigsaw_diagonal.get(9, []))} Jigsaw Diagonal 9×9")
    
    def _load_from_directory(self, directory: str, size: int) -> List[Dict]:
        """Load templates (regions + solution) from directory"""
        templates = []
        
        if not os.path.exists(directory):
            return templates
        
        files = [f for f in os.listdir(directory) if f.endswith('.json')]
        
        for filename in sorted(files):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if len(data['regions']) == size:
                    # Store both regions and solution (if available)
                    templates.append({
                        'regions': data['regions'],
                        'solution': data.get('solution')
                    })
            except Exception:
                pass
        
        return templates
    
    def get_random_template(self, size: int, is_diagonal: bool = False) -> Dict:
        """Get random template (regions + solution)"""
        cache = self._cache_jigsaw_diagonal if is_diagonal else self._cache_jigsaw
        
        if size not in cache or not cache[size]:
            raise ValueError(f"No templates found for size {size} (diagonal={is_diagonal})")
            
        return random.choice(cache[size])

    def has_templates(self, size: int, is_diagonal: bool = False) -> bool:
        cache = self._cache_jigsaw_diagonal if is_diagonal else self._cache_jigsaw
        return size in cache and len(cache[size]) > 0
    
    @classmethod
    def clear_instance(cls):
        """Clear singleton for testing"""
        cls._instance = None
