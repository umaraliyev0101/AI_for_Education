#!/usr/bin/env python3
"""
Test script to check slide generation
"""
import os
import sys

# Check if comtypes is available
try:
    import comtypes.client
    print("✅ comtypes is installed")
    COMTYPES_AVAILABLE = True
except ImportError as e:
    print(f"❌ comtypes NOT available: {e}")
    COMTYPES_AVAILABLE = False

# Check if PowerPoint is available
if COMTYPES_AVAILABLE:
    try:
        print("\n🔌 Testing PowerPoint COM...")
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        print("✅ PowerPoint COM object created successfully")
        
        # Try to set DisplayAlerts
        try:
            powerpoint.DisplayAlerts = 0
            print("✅ DisplayAlerts set successfully")
        except Exception as e:
            print(f"⚠️  Could not set DisplayAlerts: {e}")
        
        # Check version
        try:
            version = powerpoint.Version
            print(f"✅ PowerPoint version: {version}")
        except:
            print("⚠️  Could not get PowerPoint version")
        
        powerpoint.Quit()
        print("✅ PowerPoint quit successfully")
        
    except Exception as e:
        print(f"❌ PowerPoint COM failed: {e}")
        print(f"   Error type: {type(e).__name__}")

# Check presentations directory
print("\n📁 Checking directories...")
uploads_dir = "D:\\Projects\\AI_in_Education\\uploads"
presentations_dir = os.path.join(uploads_dir, "presentations")
slides_dir = os.path.join(uploads_dir, "slides")

if os.path.exists(presentations_dir):
    presentations = [f for f in os.listdir(presentations_dir) if f.endswith(('.pptx', '.pdf'))]
    print(f"✅ Presentations directory exists")
    print(f"   Files found: {len(presentations)}")
    for f in presentations:
        print(f"   - {f}")
else:
    print(f"❌ Presentations directory not found: {presentations_dir}")

if os.path.exists(slides_dir):
    slide_dirs = [d for d in os.listdir(slides_dir) if os.path.isdir(os.path.join(slides_dir, d))]
    print(f"✅ Slides directory exists")
    print(f"   Lesson folders: {len(slide_dirs)}")
    for d in slide_dirs:
        lesson_dir = os.path.join(slides_dir, d)
        slide_files = [f for f in os.listdir(lesson_dir) if f.endswith('.png')]
        print(f"   - {d}: {len(slide_files)} slides")
else:
    print(f"❌ Slides directory not found: {slides_dir}")

# Check database
print("\n💾 Checking database...")
try:
    import sqlite3
    conn = sqlite3.connect('ai_education.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, title, presentation_path FROM lessons WHERE presentation_path IS NOT NULL')
    lessons = cursor.fetchall()
    
    print(f"✅ Lessons with presentations: {len(lessons)}")
    for lesson_id, title, path in lessons:
        exists = "✅" if (path and os.path.exists(path)) else "❌"
        print(f"   {exists} ID {lesson_id}: {title}")
        print(f"      Path: {path}")
    
    conn.close()
except Exception as e:
    print(f"❌ Database check failed: {e}")

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print(f"comtypes available: {'✅ YES' if COMTYPES_AVAILABLE else '❌ NO'}")
print(f"Presentations uploaded: {len(presentations) if os.path.exists(presentations_dir) else 0}")
print(f"Lessons in DB: {len(lessons) if 'lessons' in locals() else 0}")
print("="*60)
