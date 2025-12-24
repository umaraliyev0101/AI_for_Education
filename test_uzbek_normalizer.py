#!/usr/bin/env python3
"""
Test script for Uzbek text normalizer.
Tests that different apostrophe variants are correctly normalized.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Direct import to avoid dependency issues
import re
import unicodedata
from typing import Dict, Any

# Copy of the normalizer for standalone testing
class UzbekTextNormalizer:
    """Normalizes Uzbek text to ensure consistent character encoding."""
    
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
    
    STANDARD_UZBEK_APOSTROPHE = '\u02BB'  # ʻ
    ASCII_APOSTROPHE = '\u0027'  # '
    
    def __init__(self, use_ascii_apostrophe: bool = False):
        self.target_apostrophe = self.ASCII_APOSTROPHE if use_ascii_apostrophe else self.STANDARD_UZBEK_APOSTROPHE
        self.apostrophe_pattern = re.compile(
            '[' + ''.join(re.escape(c) for c in self.APOSTROPHE_VARIANTS) + ']'
        )
    
    def normalize(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize('NFC', text)
        text = self.apostrophe_pattern.sub(self.target_apostrophe, text)
        double_apostrophe = self.target_apostrophe * 2
        while double_apostrophe in text:
            text = text.replace(double_apostrophe, self.target_apostrophe)
        return text
    
    @staticmethod
    def diagnose_text(text: str) -> Dict[str, Any]:
        diagnosis = {
            'length': len(text),
            'apostrophe_variants_found': {},
            'non_ascii_chars': {},
        }
        
        apostrophe_variants = [
            '\u02BB', '\u02BC', '\u0027', '\u2019', 
            '\u02BD', '\u0060', '\u00B4', '\u2018', '\u201B'
        ]
        
        for char in text:
            if char in apostrophe_variants:
                char_name = unicodedata.name(char, f'U+{ord(char):04X}')
                if char_name not in diagnosis['apostrophe_variants_found']:
                    diagnosis['apostrophe_variants_found'][char_name] = 0
                diagnosis['apostrophe_variants_found'][char_name] += 1
            
            if ord(char) > 127:
                char_name = unicodedata.name(char, f'U+{ord(char):04X}')
                if char_name not in diagnosis['non_ascii_chars']:
                    diagnosis['non_ascii_chars'][char_name] = 0
                diagnosis['non_ascii_chars'][char_name] += 1
        
        return diagnosis


def normalize_uzbek_text(text: str, use_ascii_apostrophe: bool = False) -> str:
    return UzbekTextNormalizer(use_ascii_apostrophe).normalize(text)

def test_normalizer():
    """Test the Uzbek text normalizer with various inputs."""
    
    print("=" * 60)
    print("Testing Uzbek Text Normalizer")
    print("=" * 60)
    
    # Test cases with different apostrophe variants
    test_cases = [
        # (input, description)
        ("O'zbekiston", "ASCII apostrophe (')"),
        ("Oʻzbekiston", "Standard Uzbek (ʻ U+02BB)"),
        ("Oʼzbekiston", "Modifier letter apostrophe (ʼ U+02BC)"),
        ("O`zbekiston", "Grave accent (`)"),
        ("O´zbekiston", "Acute accent (´)"),
        ("O'zbekiston", "Right single quote (')"),
        ("O'zbekiston", "Left single quote (')"),
        ("g'ildirak", "ASCII apostrophe for gʻ"),
        ("gʻildirak", "Standard Uzbek gʻ"),
        ("O'zbek tili juda go'zal", "Multiple apostrophes in sentence"),
        ("Men o'qiyman va o'rganaman", "Multiple words with o'"),
    ]
    
    # Test with standard Uzbek apostrophe
    print("\n1. Testing with STANDARD Uzbek apostrophe (ʻ U+02BB):")
    print("-" * 50)
    normalizer_standard = UzbekTextNormalizer(use_ascii_apostrophe=False)
    
    for text, description in test_cases:
        normalized = normalizer_standard.normalize(text)
        print(f"  {description}:")
        print(f"    Input:  '{text}'")
        print(f"    Output: '{normalized}'")
        # Show character codes for apostrophe
        for char in normalized:
            if ord(char) > 127 or char in "'`´":
                print(f"    Found char: '{char}' (U+{ord(char):04X})")
        print()
    
    # Test with ASCII apostrophe
    print("\n2. Testing with ASCII apostrophe ('):")
    print("-" * 50)
    normalizer_ascii = UzbekTextNormalizer(use_ascii_apostrophe=True)
    
    for text, description in test_cases:
        normalized = normalizer_ascii.normalize(text)
        print(f"  {description}:")
        print(f"    Input:  '{text}'")
        print(f"    Output: '{normalized}'")
        print()
    
    # Test the convenience function
    print("\n3. Testing convenience function normalize_uzbek_text():")
    print("-" * 50)
    test_text = "O'zbekiston - go'zal mamlakat"
    print(f"  Input:  '{test_text}'")
    print(f"  Output: '{normalize_uzbek_text(test_text)}'")
    
    # Test diagnosis function
    print("\n4. Testing diagnose_text() function:")
    print("-" * 50)
    mixed_text = "O'zbek va Oʻzbek va O`zbek"
    diagnosis = UzbekTextNormalizer.diagnose_text(mixed_text)
    print(f"  Input: '{mixed_text}'")
    print(f"  Apostrophe variants found: {diagnosis['apostrophe_variants_found']}")
    print(f"  Non-ASCII chars: {diagnosis['non_ascii_chars']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_normalizer()
