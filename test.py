#!/usr/bin/env python3
"""
Tokenizer apostrophe comparison test

Usage:
  python test.py --model <hf-id-or-local-path>

This script loads a tokenizer and prints tokenization for several
variants of Uzbek words using different apostrophe characters. It also
shows the effect of normalizing ASCII and other quotes to the Uzbek
modifier letter turned comma (U+02BB, 'ʻ').
"""

import argparse
from transformers import AutoTokenizer

APOSTROPHES = {
    "ASCII_apostrophe": "'",        # U+0027
    "MODIFIER_LETTER_TURNED_COMMA": "ʻ",  # U+02BB recommended for Uzbek
    "RIGHT_SINGLE_QUOTE": "’",      # U+2019
    "MODIFIER_LETTER_APOSTROPHE": "ʼ",   # U+02BC
}

SAMPLES = [
    "o{a}g{a}il",   # o'g'il variants
    "g{a}ar",       # gʻar variant
    "sh{a}ar",      # shʻar variant
]

def normalize_to_uzbek_apostrophe(s: str) -> str:
    """Replace common apostrophes with U+02BB (ʻ)."""
    return s.replace("'", "ʻ").replace("’", "ʻ").replace("ʼ", "ʻ")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="HuggingFace model id or local path to tokenizer")
    args = p.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model, use_fast=True)

    print(f"Loaded tokenizer: {args.model}\n")

    for sample_pattern in SAMPLES:
        for name, ch in APOSTROPHES.items():
            text = sample_pattern.format(a=ch)
            toks = tok.tokenize(text, add_special_tokens=False)
            print(f"Sample: {text} ({name}) -> tokens: {toks}")

        # show normalized variant
        ascii_text = sample_pattern.format(a=APOSTROPHES['ASCII_apostrophe'])
        norm = normalize_to_uzbek_apostrophe(ascii_text)
        print(f"Normalized: {ascii_text} -> {norm} -> tokens: {tok.tokenize(norm, add_special_tokens=False)}")
        print("-" * 60)

if __name__ == '__main__':
    main()
