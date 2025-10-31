# ⚠️ IMPORTANT: Install Poppler for PDF Processing

## Why Needed?

The `pdf2image` library requires **Poppler** to convert PDF pages to images. Without it, PDF presentations cannot be processed.

## Installation Steps (Windows)

### Option 1: Using Chocolatey (Recommended)

1. **Open PowerShell as Administrator**

2. **Install Chocolatey** (if not already installed):
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

3. **Install Poppler:**
   ```powershell
   choco install poppler
   ```

4. **Verify:**
   ```powershell
   pdftoppm -v
   ```

### Option 2: Manual Installation

1. **Download Poppler:**
   - Go to: https://github.com/oschwartz10612/poppler-windows/releases/latest
   - Download `Release-XX.XX.X-0.zip` (latest version)

2. **Extract:**
   - Extract to `C:\poppler\` (or any directory)

3. **Add to PATH:**
   - Open System Properties → Environment Variables
   - Edit "Path" under System Variables
   - Add: `C:\poppler\Library\bin`
   - Click OK

4. **Restart Terminal**

5. **Verify:**
   ```powershell
   pdftoppm -v
   ```

## What Happens Without Poppler?

- ✅ PPTX presentations will work (uses PowerPoint COM)
- ❌ PDF presentations will fail with error:
  ```
  ❌ pdf2image not available for PDF conversion
  ```

## Testing

After installation, test with:

```python
from pdf2image import convert_from_path

# This should work without errors
images = convert_from_path('test.pdf', dpi=150)
print(f"Converted {len(images)} pages")
```

## Alternative Workaround (Without Poppler)

If you can't install Poppler, teachers can:
1. Convert PDF to PPTX manually (using online tools or PowerPoint)
2. Upload the PPTX file instead
3. PPTX processing will work with PowerPoint COM

---

**Next Steps:**
1. Install Poppler (choose Option 1 or 2)
2. Verify with `pdftoppm -v`
3. Restart backend server
4. Test PDF upload

**Status:** ⚠️ Required for PDF Processing  
**Date:** October 30, 2025
