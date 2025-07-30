#!/usr/bin/env python3
"""
Script to download Gemma model locally for Audio Chat Studio
סקריפט להורדת מודל Gemma מקומית עבור Audio Chat Studio
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download, login
import argparse

def download_gemma_model(model_id="google/gemma-2-2b-it", cache_dir=None):
    """
    Download Gemma model locally
    
    Args:
        model_id (str): Hugging Face model ID
        cache_dir (str): Local cache directory
    """
    print(f"🤖 Downloading Gemma model: {model_id}")
    print("📝 Note: This may require Hugging Face authentication")
    
    if cache_dir is None:
        # Use project's models directory
        project_root = Path(__file__).parent.parent
        cache_dir = project_root / "models" / "gemma"
        cache_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"📁 Download location: {cache_dir}")
        print("⏳ Starting download... (this may take several minutes)")
        
        # Download the model
        local_path = snapshot_download(
            repo_id=model_id,
            cache_dir=str(cache_dir),
            local_files_only=False,
            resume_download=True
        )
        
        print(f"✅ Successfully downloaded {model_id}")
        print(f"📂 Model location: {local_path}")
        
        # Create a simple config file to remember the model location
        config_file = Path(cache_dir) / "model_config.txt"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(f"model_id={model_id}\n")
            f.write(f"local_path={local_path}\n")
            f.write(f"status=downloaded\n")
        
        print(f"💾 Configuration saved to: {config_file}")
        return local_path
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        
        if "authentication" in str(e).lower() or "token" in str(e).lower():
            print("\n🔐 Authentication required!")
            print("Please run the following commands:")
            print("1. huggingface-cli login")
            print("2. Accept Gemma license at: https://huggingface.co/google/gemma-2-2b-it")
            print("3. Run this script again")
        
        return None

def check_model_exists(cache_dir=None):
    """Check if Gemma model is already downloaded"""
    if cache_dir is None:
        project_root = Path(__file__).parent.parent
        cache_dir = project_root / "models" / "gemma"
    
    config_file = Path(cache_dir) / "model_config.txt"
    if config_file.exists():
        print(f"✅ Model configuration found: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = f.read()
            print(config)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description='Download local chat model for Audio Chat Studio')
    parser.add_argument('--model', default='microsoft/DialoGPT-small', 
                       help='Hugging Face model ID (default: microsoft/DialoGPT-small)')
    parser.add_argument('--cache-dir', help='Custom cache directory')
    parser.add_argument('--check', action='store_true', help='Check if model exists')
    
    args = parser.parse_args()
    
    print("🎵 Audio Chat Studio - Local Chat Model Downloader")
    print("=" * 50)
    
    if args.check:
        if check_model_exists(args.cache_dir):
            print("✅ Local chat model is available")
            sys.exit(0)
        else:
            print("❌ Local chat model not found")
            sys.exit(1)
    
    # Try to download the model
    result = download_gemma_model(args.model, args.cache_dir)
    
    if result:
        print("\n🎉 Success! Local chat model is ready to use.")
        print("🚀 You can now start Audio Chat Studio and use the local model for conversations.")
        print("💡 The model will appear as 'Local Gemma' in the interface.")
    else:
        print("\n❌ Download failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()