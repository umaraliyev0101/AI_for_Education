"""
Simple upload test to diagnose 'error parsing body' issue
"""
import requests
import os

# Configuration
BASE_URL = "http://localhost:8001"
USERNAME = "admin"
PASSWORD = "admin123"

def test_upload():
    """Test presentation upload with detailed error handling"""
    
    print("=" * 60)
    print("🧪 PRESENTATION UPLOAD DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣  Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": USERNAME,
            "password": PASSWORD
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"   ✅ Login successful")
    print(f"   Token: {token[:20]}...")
    
    # Step 2: Create test file
    print("\n2️⃣  Creating test file...")
    test_file = "test_presentation.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("This is a test presentation file content.\n")
        f.write("It contains some sample text to test upload functionality.\n")
    
    file_size = os.path.getsize(test_file)
    print(f"   ✅ Test file created: {test_file} ({file_size} bytes)")
    
    # Step 3: Test different upload approaches
    lesson_id = 1
    
    # Test 1: Upload with explicit Content-Type (WRONG - this often causes the error)
    print("\n3️⃣  Test 1: Upload WITH explicit Content-Type (typically fails)")
    try:
        with open(test_file, "rb") as f:
            files = {"file": (test_file, f, "text/plain")}
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "multipart/form-data"  # ❌ THIS IS WRONG!
            }
            
            response = requests.post(
                f"{BASE_URL}/api/lessons/{lesson_id}/presentation",
                files=files,
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Body: {response.text[:200]}")
            
            if response.status_code == 200:
                print(f"   ✅ Upload successful")
            else:
                print(f"   ❌ Upload failed")
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Upload WITHOUT explicit Content-Type (CORRECT)
    print("\n4️⃣  Test 2: Upload WITHOUT explicit Content-Type (correct way)")
    try:
        with open(test_file, "rb") as f:
            files = {"file": (test_file, f, "text/plain")}
            headers = {
                "Authorization": f"Bearer {token}"
                # No Content-Type - let requests library add it with boundary
            }
            
            response = requests.post(
                f"{BASE_URL}/api/lessons/{lesson_id}/presentation",
                files=files,
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Body: {response.text[:200]}")
            
            if response.status_code == 200:
                print(f"   ✅ Upload successful")
                result = response.json()
                print(f"   Message: {result.get('message')}")
                print(f"   Filename: {result.get('filename')}")
                print(f"   File Size: {result.get('file_size')} bytes")
            else:
                print(f"   ❌ Upload failed")
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Check what headers requests sends automatically
    print("\n5️⃣  Test 3: Inspect auto-generated headers")
    with open(test_file, "rb") as f:
        files = {"file": (test_file, f, "text/plain")}
        headers = {"Authorization": f"Bearer {token}"}
        
        # Prepare request to see headers
        req = requests.Request(
            "POST",
            f"{BASE_URL}/api/lessons/{lesson_id}/presentation",
            files=files,
            headers=headers
        )
        prepared = req.prepare()
        
        print(f"   Auto-generated Content-Type: {prepared.headers.get('Content-Type')}")
        print(f"   Full headers: {dict(prepared.headers)}")
    
    # Cleanup
    print("\n6️⃣  Cleanup")
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"   ✅ Test file removed")
    
    print("\n" + "=" * 60)
    print("🏁 TEST COMPLETE")
    print("=" * 60)
    
    print("\n📋 SUMMARY:")
    print("   - If Test 1 failed with 'error parsing body', that's expected")
    print("   - If Test 2 succeeded, the issue is with Content-Type header")
    print("   - Check your frontend code - it should NOT set Content-Type")
    print("   - Let the browser/fetch automatically add multipart/form-data")


if __name__ == "__main__":
    test_upload()
