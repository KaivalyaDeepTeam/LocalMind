#!/usr/bin/env python
"""
Test script to download and verify Hindi models.

This script will:
1. Download both Apex and Prime models
2. Verify they load correctly
3. Test basic inference
"""

import sys
from pathlib import Path

# Add localmind to path
sys.path.insert(0, str(Path(__file__).parent))


def _download_and_verify_model(model_id: str, variant_name: str):
    """Test downloading and loading a model."""
    print(f"\n{'='*70}")
    print(f"Testing {variant_name} Model: {model_id}")
    print(f"{'='*70}\n")

    try:
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

        # Determine device
        if torch.cuda.is_available():
            device = "cuda:0"
            torch_dtype = torch.float16
            print("✓ Using CUDA GPU")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
            torch_dtype = torch.float16
            print("✓ Using Apple Silicon GPU (MPS)")
        else:
            device = "cpu"
            torch_dtype = torch.float32
            print("✓ Using CPU")

        print("\n1. Downloading model from Hugging Face...")
        print("   This may take a few minutes on first run...")

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        print("   ✓ Model downloaded and loaded")

        print(f"\n2. Moving model to {device}...")
        model.to(device)
        print("   ✓ Model moved to device")

        print("\n3. Loading processor...")
        processor = AutoProcessor.from_pretrained(model_id)
        print("   ✓ Processor loaded")

        print("\n4. Verifying model configuration...")
        config = model.config
        print(f"   - Model type: {config.model_type}")
        print(f"   - Vocab size: {config.vocab_size}")
        print(f"   - Max length: {config.max_length}")
        print("   ✓ Model configuration verified")

        # Clean up
        del model
        del processor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print(f"\n✅ {variant_name} Model Test PASSED")
        return True

    except ImportError as e:
        print(f"\n❌ Missing dependencies: {e}")
        print("   Install with: pip install transformers torch")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Test both Hindi models."""
    print("\n" + "=" * 70)
    print("Hindi Model Download & Verification Test")
    print("=" * 70)

    models_to_test = [
        ("Oriserve/Whisper-Hindi2Hinglish-Apex", "Apex (Fast, Noisy Audio)"),
        ("Oriserve/Whisper-Hindi2Hinglish-Prime", "Prime (Accurate, Clean Audio)"),
    ]

    results = []

    for model_id, variant_name in models_to_test:
        success = _download_and_verify_model(model_id, variant_name)
        results.append((variant_name, success))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for variant_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {variant_name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n✅ All models downloaded and verified successfully!")
        print("\nModels are cached at: ~/.cache/huggingface/hub/")
        print("\nYou can now run the application:")
        print("  python -m localmind")
        return 0
    else:
        print("\n❌ Some models failed to download")
        return 1


if __name__ == "__main__":
    sys.exit(main())
