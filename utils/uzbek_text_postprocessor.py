#!/usr/bin/env python3
"""
Uzbek Text Post-Processing
Clean and normalize recognized Uzbek text
"""

import re
from typing import List, Dict, Set, Any
import unicodedata


class UzbekTextNormalizer:
    """
    Normalizes Uzbek text to ensure consistent character encoding.
    
    This is crucial for LLM tokenization because Uzbek uses special characters
    like oʻ, gʻ which can be represented in multiple ways:
    - ʻ (U+02BB - MODIFIER LETTER TURNED COMMA) - standard Uzbek
    - ʼ (U+02BC - MODIFIER LETTER APOSTROPHE)
    - ' (U+0027 - APOSTROPHE) - common keyboard input
    - ' (U+2019 - RIGHT SINGLE QUOTATION MARK) - sometimes used
    - ʽ (U+02BD - MODIFIER LETTER REVERSED COMMA)
    - ` (U+0060 - GRAVE ACCENT)
    
    The LLaMA Uzbek tokenizer typically expects one specific form,
    and other forms result in <UNK> tokens.
    """
    
    # All apostrophe-like characters that might be used
    APOSTROPHE_VARIANTS = [
        '\u02BB',  # ʻ MODIFIER LETTER TURNED COMMA (standard Uzbek)
        '\u02BC',  # ʼ MODIFIER LETTER APOSTROPHE
        '\u0027',  # ' APOSTROPHE (ASCII)
        '\u2019',  # ' RIGHT SINGLE QUOTATION MARK
        '\u02BD',  # ʽ MODIFIER LETTER REVERSED COMMA
        '\u0060',  # ` GRAVE ACCENT
        '\u00B4',  # ´ ACUTE ACCENT
        '\u2018',  # ' LEFT SINGLE QUOTATION MARK
        '\u201B',  # ‛ SINGLE HIGH-REVERSED-9 QUOTATION MARK
    ]
    
    # Standard Uzbek apostrophe (most tokenizers expect this)
    STANDARD_UZBEK_APOSTROPHE = '\u02BB'  # ʻ MODIFIER LETTER TURNED COMMA
    
    # Alternative: ASCII apostrophe (might work better with some tokenizers)
    ASCII_APOSTROPHE = '\u0027'  # '
    
    def __init__(self, use_ascii_apostrophe: bool = False):
        """
        Initialize the normalizer.
        
        Args:
            use_ascii_apostrophe: If True, use ASCII apostrophe (') instead of 
                                  the standard Uzbek modifier letter.
                                  Try this if you still get UNK tokens.
        """
        self.target_apostrophe = self.ASCII_APOSTROPHE if use_ascii_apostrophe else self.STANDARD_UZBEK_APOSTROPHE
        
        # Build replacement pattern
        self.apostrophe_pattern = re.compile(
            '[' + ''.join(re.escape(c) for c in self.APOSTROPHE_VARIANTS) + ']'
        )
        
        # Common Uzbek letter combinations with apostrophes
        # These are the letters that use the apostrophe-like modifier
        self.uzbek_modified_letters = {
            'o': f'o{self.target_apostrophe}',  # oʻ
            'g': f'g{self.target_apostrophe}',  # gʻ
        }
    
    def normalize(self, text: str) -> str:
        """
        Normalize Uzbek text for consistent tokenization.
        
        This function:
        1. Normalizes Unicode to NFC form
        2. Replaces all apostrophe variants with the standard one
        3. Handles common encoding issues
        
        Args:
            text: Input text (possibly with mixed apostrophe characters)
            
        Returns:
            Normalized text with consistent apostrophe characters
        """
        if not text:
            return ""
        
        # Step 1: Normalize Unicode (NFC form)
        text = unicodedata.normalize('NFC', text)
        
        # Step 2: Replace all apostrophe variants with the target
        text = self.apostrophe_pattern.sub(self.target_apostrophe, text)
        
        # Step 3: Fix common patterns where apostrophe might be missing or wrong
        # Pattern: o followed by certain consonants should likely be oʻ
        # This is heuristic and might need adjustment
        
        # Step 4: Clean up any double apostrophes that might have been created
        double_apostrophe = self.target_apostrophe * 2
        while double_apostrophe in text:
            text = text.replace(double_apostrophe, self.target_apostrophe)
        
        return text
    
    def normalize_for_tokenizer(self, text: str, tokenizer=None) -> str:
        """
        Normalize text specifically for a given tokenizer.
        
        If a tokenizer is provided, tests which apostrophe form works best.
        
        Args:
            text: Input text
            tokenizer: HuggingFace tokenizer (optional)
            
        Returns:
            Normalized text optimized for the tokenizer
        """
        if tokenizer is None:
            return self.normalize(text)
        
        # Test with standard normalization first
        normalized = self.normalize(text)
        
        # Check if we get UNK tokens
        tokens = tokenizer.tokenize(normalized)
        unk_count = sum(1 for t in tokens if '<unk>' in t.lower() or 'unk' in t.lower())
        
        if unk_count > 0:
            # Try with ASCII apostrophe
            ascii_normalizer = UzbekTextNormalizer(use_ascii_apostrophe=True)
            alt_normalized = ascii_normalizer.normalize(text)
            alt_tokens = tokenizer.tokenize(alt_normalized)
            alt_unk_count = sum(1 for t in alt_tokens if '<unk>' in t.lower() or 'unk' in t.lower())
            
            if alt_unk_count < unk_count:
                return alt_normalized
        
        return normalized
    
    @staticmethod
    def diagnose_text(text: str) -> Dict[str, Any]:
        """
        Diagnose a text for character encoding issues.
        
        Useful for debugging UNK token problems.
        
        Args:
            text: Text to diagnose
            
        Returns:
            Dictionary with diagnostic information
        """
        diagnosis = {
            'length': len(text),
            'apostrophe_variants_found': {},
            'non_ascii_chars': {},
            'unicode_categories': {},
        }
        
        normalizer = UzbekTextNormalizer()
        
        for char in text:
            # Check for apostrophe variants
            if char in normalizer.APOSTROPHE_VARIANTS:
                char_name = unicodedata.name(char, f'U+{ord(char):04X}')
                if char_name not in diagnosis['apostrophe_variants_found']:
                    diagnosis['apostrophe_variants_found'][char_name] = 0
                diagnosis['apostrophe_variants_found'][char_name] += 1
            
            # Check for non-ASCII
            if ord(char) > 127:
                char_name = unicodedata.name(char, f'U+{ord(char):04X}')
                if char_name not in diagnosis['non_ascii_chars']:
                    diagnosis['non_ascii_chars'][char_name] = 0
                diagnosis['non_ascii_chars'][char_name] += 1
        
        return diagnosis


# Global instance for convenience
_default_normalizer = None

def get_uzbek_normalizer(use_ascii_apostrophe: bool = False) -> UzbekTextNormalizer:
    """Get or create a default Uzbek text normalizer."""
    global _default_normalizer
    if _default_normalizer is None or _default_normalizer.target_apostrophe != (
        UzbekTextNormalizer.ASCII_APOSTROPHE if use_ascii_apostrophe 
        else UzbekTextNormalizer.STANDARD_UZBEK_APOSTROPHE
    ):
        _default_normalizer = UzbekTextNormalizer(use_ascii_apostrophe)
    return _default_normalizer


def normalize_uzbek_text(text: str, use_ascii_apostrophe: bool = False) -> str:
    """
    Convenience function to normalize Uzbek text.
    
    Args:
        text: Input text
        use_ascii_apostrophe: Whether to use ASCII apostrophe
        
    Returns:
        Normalized text
    """
    return get_uzbek_normalizer(use_ascii_apostrophe).normalize(text)


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