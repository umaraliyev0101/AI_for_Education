#!/usr/bin/env python3
"""Test XLS-R pipeline initialization"""

from stt_pipelines.uzbek_xlsr_pipeline import create_uzbek_xlsr_stt

try:
    print("🔄 Initializing XLS-R pipeline...")
    stt = create_uzbek_xlsr_stt()
    print("✅ XLS-R Pipeline initialized successfully")
    info = stt.get_model_info()
    print(f"Device: {info['device']}")
    print(f"Model: {info['model_name']}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
