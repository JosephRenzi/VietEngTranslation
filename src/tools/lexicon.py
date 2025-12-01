import json
import os
from src.core.utils import performance_timer

class LexiconTool:
    def __init__(self):
        # Base path to your data directory
        # Adjusting path to go up from 'tools' -> 'src' -> 'data' -> 'translation_resources'
        self.data_dir = os.path.join(os.path.dirname(__file__), '../data/translation_resources')
        
        # Internal caches
        self._common_phrases = None
        self._full_dict = None

    @performance_timer
    def _load_json(self, filename):
        """Helper to load JSON with explicit path debugging."""
        path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(path):
            # Print a warning but don't crash. Returns empty dict so logic continues.
            print(f"[Tool Warning] Resource file not found: {filename}")
            return {}
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"[Tool Error] Failed to load {filename}: {e}")
            return {}

    @property
    def common_phrases(self):
        """Tier 1: High-priority, common terms."""
        if self._common_phrases is None:
            self._common_phrases = self._load_json('common_translation_phrases_words.json')
        return self._common_phrases

    @property
    def full_dict(self):
        """Tier 2: The massive dictionary file (optional)."""
        if self._full_dict is None:
            # It is safe to load this even if the file is missing (returns {})
            self._full_dict = self._load_json('vi_en_dict.json')
        return self._full_dict

    @performance_timer
    def lookup_vietnamese(self, term: str) -> str:
        """
        Searches for a term using a Priority Tier strategy.
        1. Common Phrases (Fast, Custom)
        2. Full Dictionary (Slow, Broad)
        """
        term_lower = term.lower()
        
        # Tier 1: Check Common Phrases
        if term_lower in self.common_phrases:
            return f"[Common] {term}: {self.common_phrases[term_lower]}"

        # Tier 2: Check Full Dictionary (if available)
        # This will just skip if full_dict is empty, so no need to comment it out
        if self.full_dict and term_lower in self.full_dict:
             return f"[Dict] {term}: {self.full_dict[term_lower]}"

        return "not found"

# Global instance
lexicon = LexiconTool()
