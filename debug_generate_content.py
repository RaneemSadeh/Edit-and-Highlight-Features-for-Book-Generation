"""
Debug script to test the Generate Base Context feature
This will help identify why the consolidation is taking too long
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configuration
OUTPUT_DIR = Path("extracted_docs")
CONSOLIDATED_DIR = Path("consolidated_docs")

def test_api_connection():
    """Test if the Gemini API is working"""
    print("=" * 60)
    print("1. Testing API Connection...")
    print("=" * 60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"[OK] API Key found: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        print("[OK] API configured successfully")
        return True
    except Exception as e:
        print(f"❌ ERROR configuring API: {e}")
        return False

def list_available_models():
    """List all available Gemini models"""
    print("\n" + "=" * 60)
    print("2. Listing Available Models...")
    print("=" * 60)
    
    try:
        models = genai.list_models()
        print("\nAvailable models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        return True
    except Exception as e:
        print(f"❌ ERROR listing models: {e}")
        return False

def test_simple_generation():
    """Test a simple generation to verify the model works"""
    print("\n" + "=" * 60)
    print("3. Testing Simple Generation...")
    print("=" * 60)
    
    # Try different model names
    model_names = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-pro"
    ]
    
    for model_name in model_names:
        try:
            print(f"\nTrying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            start_time = time.time()
            response = model.generate_content("Say 'Hello, I am working!'")
            elapsed = time.time() - start_time
            
            print(f"✓ Model {model_name} works!")
            print(f"  Response: {response.text[:100]}")
            print(f"  Time taken: {elapsed:.2f} seconds")
            return model_name
        except Exception as e:
            print(f"✗ Model {model_name} failed: {str(e)[:100]}")
    
    return None

def check_extracted_files():
    """Check if there are files to consolidate"""
    print("\n" + "=" * 60)
    print("4. Checking Extracted Files...")
    print("=" * 60)
    
    if not OUTPUT_DIR.exists():
        print(f"❌ Directory {OUTPUT_DIR} does not exist")
        return False
    
    md_files = list(OUTPUT_DIR.glob("*.md"))
    
    if not md_files:
        print(f"⚠️  No .md files found in {OUTPUT_DIR}")
        print("   You need to upload and process files first!")
        return False
    
    print(f"✓ Found {len(md_files)} markdown files:")
    total_size = 0
    for md_file in md_files:
        size = md_file.stat().st_size
        total_size += size
        print(f"  - {md_file.name} ({size:,} bytes)")
    
    print(f"\nTotal content size: {total_size:,} bytes ({total_size/1024:.2f} KB)")
    
    if total_size > 1_000_000:  # 1MB
        print("⚠️  WARNING: Large content size may take longer to process")
    
    return True

def test_consolidation_with_timeout(working_model):
    """Test the actual consolidation with a timeout"""
    print("\n" + "=" * 60)
    print("5. Testing Consolidation (with 60s timeout)...")
    print("=" * 60)
    
    if not working_model:
        print("❌ No working model found, skipping consolidation test")
        return
    
    # Read files
    md_files = list(OUTPUT_DIR.glob("*.md"))
    if not md_files:
        print("❌ No files to consolidate")
        return
    
    combined_text = ""
    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            combined_text += f"\n\n--- START OF FILE: {md_file.name} ---\n\n"
            combined_text += content
            combined_text += f"\n\n--- END OF FILE: {md_file.name} ---\n\n"
    
    print(f"Combined text length: {len(combined_text):,} characters")
    
    # Test with simple prompt first
    try:
        print(f"\nUsing model: {working_model}")
        model = genai.GenerativeModel(
            model_name=working_model,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 8192,  # Reduced for testing
            }
        )
        
        # Simple test prompt
        test_prompt = f"Please summarize the following content in 3-5 sentences:\n\n{combined_text[:2000]}"
        
        print("Sending test request to Gemini...")
        start_time = time.time()
        
        response = model.generate_content(test_prompt)
        
        elapsed = time.time() - start_time
        print(f"\n✓ SUCCESS! Consolidation completed in {elapsed:.2f} seconds")
        print(f"\nResponse preview:\n{response.text[:500]}...")
        
    except Exception as e:
        print(f"\n❌ ERROR during consolidation: {e}")

def main():
    print("\n" + "=" * 60)
    print("DEBUGGING: Generate Base Context Feature")
    print("=" * 60)
    
    # Step 1: Test API
    if not test_api_connection():
        return
    
    # Step 2: List models
    list_available_models()
    
    # Step 3: Find working model
    working_model = test_simple_generation()
    
    # Step 4: Check files
    has_files = check_extracted_files()
    
    # Step 5: Test consolidation if we have files
    if has_files and working_model:
        test_consolidation_with_timeout(working_model)
    
    print("\n" + "=" * 60)
    print("DEBUGGING COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. If a model works, update MODEL_NAME in app/consolidator.py")
    print("2. If consolidation times out, consider reducing max_output_tokens")
    print("3. If files are too large, consider processing them in batches")

if __name__ == "__main__":
    main()
