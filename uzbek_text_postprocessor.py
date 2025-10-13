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
            # Add more patterns as needed
        }

    def _load_common_typos(self) -> Dict[str, str]:
        """Load common recognition typos and corrections"""

        return {
            # Common Vosk recognition errors for Uzbek
            'rahmat': 'rahmat',
            'voy': 'voy',
            'yoq': "yo'q",
            'yox': "yo'q",
            'yuk': "yo'q",
            'bor': 'bor',
            'yok': "yo'q",
            'salom': 'salom',
            'xayr': 'xayr',
            'qalay': 'qalay',
            'yaxshi': 'yaxshi',
            'yomon': 'yomon',
            'katta': 'katta',
            'kichik': 'kichik',
            'tez': 'tez',
            'sekin': 'sekin',
            'qizil': 'qizil',
            'yashil': 'yashil',
            'qora': 'qora',
            'oq': 'oq',
            # Numbers and common phrases
            'bir': 'bir',
            'ikki': 'ikki',
            'uch': 'uch',
            'tort': 'to\'rt',
            'besh': 'besh',
            'olti': 'olti',
            'yetti': 'yetti',
            'sakkiz': 'sakkiz',
            'toqqiz': 'to\'qqiz',
            'on': 'o\'n',
        }

    def _load_abbreviations(self) -> Dict[str, str]:
        """Load common Uzbek abbreviations"""

        return {
            'dr': 'doctor',
            'prof': 'professor',
            'ing': 'injinir',
            'muh': 'muhandis',
            'o\'zb': "O'zbekiston",
            'uzb': "O'zbekiston",
            'jr': 'junior',
            'sr': 'senior',
        }

    def post_process_text(self, text: str) -> str:
        """
        Apply all post-processing steps to recognized text

        Args:
            text: Raw recognized text from speech recognition

        Returns:
            Processed and cleaned text
        """

        if not text or not text.strip():
            return text

        # Step 1: Normalize Unicode characters
        text = self._normalize_unicode(text)

        # Step 2: Fix common typos and recognition errors
        text = self._fix_common_typos(text)

        # Step 3: Apply vowel harmony corrections
        text = self._apply_vowel_harmony(text)

        # Step 4: Expand abbreviations
        text = self._expand_abbreviations(text)

        # Step 5: Add punctuation
        text = self._add_punctuation(text)

        # Step 6: Capitalize properly
        text = self._capitalize_sentences(text)

        # Step 7: Clean up spacing
        text = self._clean_spacing(text)

        return text.strip()

    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters and fix common issues"""

        # Normalize Unicode
        text = unicodedata.normalize('NFC', text)

        # Fix common apostrophe issues
        text = re.sub(r'[\'`]', "'", text)

        # Fix common quote issues
        text = re.sub(r'[""]', '"', text)

        return text

    def _fix_common_typos(self, text: str) -> str:
        """Fix common recognition typos"""

        words = text.split()
        corrected_words = []

        for word in words:
            # Convert to lowercase for matching
            lower_word = word.lower()

            # Check for exact matches in typo dictionary
            if lower_word in self.common_typos:
                corrected_word = self.common_typos[lower_word]
                # Preserve original capitalization if it was title case
                if word.istitle():
                    corrected_word = corrected_word.capitalize()
                elif word.isupper():
                    corrected_word = corrected_word.upper()
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)

        return ' '.join(corrected_words)

    def _apply_vowel_harmony(self, text: str) -> str:
        """Apply vowel harmony corrections"""

        # This is a simplified implementation
        # In a full implementation, you'd use more sophisticated
        # linguistic rules for Uzbek vowel harmony

        words = text.split()
        corrected_words = []

        for word in words:
            lower_word = word.lower()
            if lower_word in self.vowel_harmony_patterns:
                corrected_word = self.vowel_harmony_patterns[lower_word]
                # Preserve capitalization
                if word.istitle():
                    corrected_word = corrected_word.capitalize()
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)

        return ' '.join(corrected_words)

    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations"""

        words = text.split()
        expanded_words = []

        for word in words:
            lower_word = word.lower().rstrip('.,!?')
            if lower_word in self.abbreviations:
                expanded = self.abbreviations[lower_word]
                # Preserve capitalization
                if word.istitle():
                    expanded = expanded.capitalize()
                expanded_words.append(expanded)
            else:
                expanded_words.append(word)

        return ' '.join(expanded_words)

    def _add_punctuation(self, text: str) -> str:
        """Add basic punctuation based on context"""

        # This is a simplified punctuation addition
        # A more sophisticated version would use NLP models

        sentences = re.split(r'(\s+)', text)
        punctuated_sentences = []

        for i, part in enumerate(sentences):
            if part.strip():
                # Add period at the end if it's the last part and doesn't end with punctuation
                if i == len(sentences) - 1 and not part.rstrip().endswith(('.', '!', '?', '...')):
                    part = part.rstrip() + '.'
                # Add comma before certain words (simplified)
                elif i < len(sentences) - 1 and part.lower().strip() in ['va', 'lekin', 'ammo', 'yoki']:
                    part = ', ' + part
            punctuated_sentences.append(part)

        return ''.join(punctuated_sentences)

    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize the first letter of sentences"""

        # Split into sentences (basic implementation)
        sentences = re.split(r'([.!?]+)', text)

        capitalized_sentences = []
        capitalize_next = True

        for part in sentences:
            if capitalize_next and part.strip():
                # Capitalize first letter
                part = part[0].upper() + part[1:] if part else part
                capitalize_next = False

            # Reset capitalization flag after sentence enders
            if part in self.sentence_enders:
                capitalize_next = True

            capitalized_sentences.append(part)

        return ''.join(capitalized_sentences)

    def _clean_spacing(self, text: str) -> str:
        """Clean up spacing issues"""

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)

        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)
        text = re.sub(r'([.!?,;:])\s*', r'\1 ', text)

        # Remove space before apostrophe in contractions
        text = re.sub(r"\s+'", "'", text)

        return text.strip()

    def get_confidence_score(self, original_text: str, processed_text: str) -> float:
        """
        Calculate a simple confidence score for the post-processing

        Args:
            original_text: Original recognized text
            processed_text: Post-processed text

        Returns:
            Confidence score between 0 and 1
        """

        if not original_text or not processed_text:
            return 0.0

        # Simple confidence based on text length preservation
        # and number of corrections made
        original_words = set(original_text.lower().split())
        processed_words = set(processed_text.lower().split())

        # Words preserved
        preserved_words = original_words.intersection(processed_words)
        preservation_ratio = len(preserved_words) / len(original_words) if original_words else 0

        # Length similarity
        length_ratio = min(len(processed_text), len(original_text)) / max(len(processed_text), len(original_text))

        # Combined confidence
        confidence = (preservation_ratio + length_ratio) / 2

        return min(confidence, 1.0)

def test_post_processor():
    """Test the post-processor with sample Uzbek text"""

    processor = UzbekTextPostProcessor()

    test_cases = [
        "salom qalay siz",  # Should become "Salom, qalay siz?"
        "rahmat yaxshi",    # Should become "Rahmat, yaxshi."
        "voy bu qizil",     # Should become "Voy, bu qizil."
        "yoq men boraman",  # Should become "Yo'q, men boraman."
        "dr ali keladi",    # Should expand abbreviation
    ]

    print("🧹 UZBEK TEXT POST-PROCESSING TEST")
    print("=" * 40)

    for i, test_text in enumerate(test_cases, 1):
        processed = processor.post_process_text(test_text)
        confidence = processor.get_confidence_score(test_text, processed)

        print(f"Test {i}:")
        print(f"  Input:    '{test_text}'")
        print(f"  Output:   '{processed}'")
        print(f"  Confidence: {confidence:.2f}")
        print()

if __name__ == "__main__":
    test_post_processor()
