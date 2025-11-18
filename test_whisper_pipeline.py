#!/usr/bin/env python3
"""Test Whisper pipeline initialization"""

from stt_pipelines.uzbek_whisper_pipeline import create_uzbek_whisper_stt

try:
    print("🔄 Initializing Whisper pipeline...")
    stt = create_uzbek_whisper_stt()
    print("✅ Whisper Pipeline initialized successfully")
    info = stt.get_model_info()
    print(f"Device: {info['device']}")
    print(f"Model: {info['model_name']}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
