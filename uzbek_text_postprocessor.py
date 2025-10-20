#!/usr/bin/env python3
"""
Uzbek Text Post-Processing
Clean and normalize recognized Uzbek text
"""

import re
from typing import List, Dict, Set
import unicodedata

class UzbekTextPostProcessor:
    """
    Post-process recognized Uzbek text for better readability and accuracy
    """

    def __init__(self, config_path: str = "uzbek_speech_config.yaml"):
        """Initialize the post-processor"""

        self.config = self._load_config(config_path)

        # Uzbek-specific patterns and rules
        self.vowel_harmony_patterns = self._load_vowel_harmony_patterns()
        self.common_typos = self._load_common_typos()
        self.abbreviations = self._load_abbreviations()

        # Punctuation patterns
        self.sentence_enders = ['.', '!', '?', '...']
        self.pause_markers = [',', ';', ':']
        self.quote_marks = ['"', '"', ''', ''']

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        import yaml
        import os
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {}

    def _load_vowel_harmony_patterns(self) -> Dict[str, str]:
        """Load vowel harmony correction patterns"""
        return {
            # Common vowel harmony corrections
            'qilaman': 'qilaman',
            'qilayotgan': 'qilayotgan',
            'boraman': 'boraman',
            'borayotgan': 'borayotgan',
        }

    def _load_common_typos(self) -> Dict[str, str]:
        """Load common typo corrections"""
        return {
            # Common recognition errors
            'q': 'q',
            'sh': 'sh',
            'ch': 'ch',
            'o\'': 'o\'',
            'u\'': 'u\'',
        }

    def _load_abbreviations(self) -> Dict[str, str]:
        """Load abbreviation expansions"""
        return {
            'dr': 'doctor',
            'prof': 'professor',
            'o\'qit': 'o\'qituvchi',
        }

    def post_process_text(self, text: str) -> str:
        """
        Post-process recognized text

        Args:
            text: Raw recognized text

        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""

        # Convert to lowercase for processing
        processed = text.lower()

        # Apply corrections
        processed = self._apply_vowel_harmony(processed)
        processed = self._correct_typos(processed)
        processed = self._expand_abbreviations(processed)

        # Normalize unicode
        processed = unicodedata.normalize('NFC', processed)

        # Capitalize first letter of sentences
        processed = self._capitalize_sentences(processed)

        # Clean up extra spaces
        processed = re.sub(r'\s+', ' ', processed).strip()

        return processed

    def _apply_vowel_harmony(self, text: str) -> str:
        """Apply vowel harmony corrections"""
        for pattern, correction in self.vowel_harmony_patterns.items():
            text = text.replace(pattern, correction)
        return text

    def _correct_typos(self, text: str) -> str:
        """Correct common typos"""
        for typo, correction in self.common_typos.items():
            text = text.replace(typo, correction)
        return text

    def _expand_abbreviations(self, text: str) -> str:
        """Expand abbreviations"""
        words = text.split()
        expanded_words = []

        for word in words:
            # Check if word is an abbreviation
            expanded = self.abbreviations.get(word.lower(), word)
            expanded_words.append(expanded)

        return ' '.join(expanded_words)

    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of sentences"""
        sentences = re.split(r'([.!?]+)', text)
        result = []

        for i, sentence in enumerate(sentences):
            if i % 2 == 0:  # Text parts
                sentence = sentence.strip()
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:]
            result.append(sentence)

        return ''.join(result)

    def get_confidence_score(self, original_text: str, processed_text: str) -> float:
        """
        Calculate confidence score based on processing changes

        Args:
            original_text: Original recognized text
            processed_text: Processed text

        Returns:
            Confidence score (0-1)
        """
        if not original_text:
            return 0.0

        # Simple confidence based on text length and changes
        changes = sum(1 for a, b in zip(original_text, processed_text) if a != b)
        change_ratio = changes / len(original_text)

        # Higher confidence if fewer changes needed
        confidence = max(0.0, 1.0 - change_ratio)

        return round(confidence, 3)