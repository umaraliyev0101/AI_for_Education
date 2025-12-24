#!/usr/bin/env python3
"""
Tokenizer apostrophe comparison test

Usage:
  python test.py --model <hf-id-or-local-path>
  python test.py  # Uses model from backend.llm_config

This script loads a tokenizer and prints tokenization for several
variants of Uzbek words using different apostrophe characters. It also
shows the effect of normalizing to ASCII apostrophe (') which works
best with the Llama Uzbek tokenizer.
"""

import argparse
from transformers import AutoTokenizer

# Try to import default model from backend.llm_config
try:
    from backend.llm_config import CURRENT_LLM_MODEL as DEFAULT_MODEL
except Exception:
    DEFAULT_MODEL = None

APOSTROPHES = {
    "ASCII_apostrophe": "'",        # U+0027
    "MODIFIER_LETTER_TURNED_COMMA": "ʻ",  # U+02BB recommended for Uzbek
    "RIGHT_SINGLE_QUOTE": "'",      # U+2019
    "MODIFIER_LETTER_APOSTROPHE": "ʼ",   # U+02BC
}

SAMPLES = [
    "o{a}g{a}il",   # o'g'il variants
    "g{a}ar",       # gʻar variant
    "sh{a}ar",      # shʻar variant
]

def normalize_to_uzbek_apostrophe(s: str) -> str:
    """Replace common apostrophes with U+02BB (ʻ)."""
    return s.replace("'", "ʻ").replace("'", "ʻ").replace("ʼ", "ʻ")

def normalize_to_ascii_apostrophe(s: str) -> str:
    """Replace common apostrophes with ASCII apostrophe (U+0027)."""
    return s.replace("ʻ", "'").replace("'", "'").replace("ʼ", "'")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=(DEFAULT_MODEL is None),
                   default=DEFAULT_MODEL,
                   help=f"HuggingFace model id or local path to tokenizer (default from backend.llm_config: {DEFAULT_MODEL})")
    args = p.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model, use_fast=True)

    print(f"Loaded tokenizer: {args.model}\n")

    for sample_pattern in SAMPLES:
        for name, ch in APOSTROPHES.items():
            text = sample_pattern.format(a=ch)
            toks = tok.tokenize(text, add_special_tokens=False)
            print(f"Sample: {text} ({name}) -> tokens: {toks}")

        # show normalized variants
        base_text = sample_pattern.format(a=APOSTROPHES['MODIFIER_LETTER_TURNED_COMMA'])
        
        # ASCII normalization (recommended for this model)
        ascii_norm = normalize_to_ascii_apostrophe(base_text)
        print(f"-> ASCII norm: {base_text} -> {ascii_norm} -> tokens: {tok.tokenize(ascii_norm, add_special_tokens=False)}")
        
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION:")
    print("Based on the tokenization above, choose the apostrophe form that")
    print("produces fewer, cleaner tokens (not split into bytes like 'Ê', '»').")
    print("For behbudiy/Llama-3.1-8B-Instruct-Uz: ASCII apostrophe (') is better.")
    print("=" * 60)

if __name__ == '__main__':
    main()
