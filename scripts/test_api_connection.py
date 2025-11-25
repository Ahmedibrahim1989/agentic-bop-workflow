#!/usr/bin/env python
"""Test API connectivity and configuration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


def main() -> None:
    """Test API configuration."""
    print("\n" + "="*80)
    print("API CONFIGURATION TEST")
    print("="*80 + "\n")
    
    # Check API keys
    print("API Keys:")
    print(f"  OPENAI_API_KEY:    {'\u2713 Set' if settings.openai_api_key else '✗ Not set'}")
    print(f"  ANTHROPIC_API_KEY: {'\u2713 Set' if settings.anthropic_api_key else '✗ Not set'}")
    
    # Check model configuration
    print("\nModel Configuration:")
    print(f"  OpenAI model:    {settings.model_name_openai}")
    print(f"  Anthropic model: {settings.model_name_anthropic}")
    print(f"  Temperature:     {settings.temperature}")
    print(f"  Max tokens:      {settings.max_tokens}")
    
    # Validation
    print("\nValidation:")
    try:
        settings.validate()
        print("  ✓ Configuration is valid")
    except ValueError as e:
        print(f"  ✗ Configuration error: {e}")
        print("\nPlease set at least one API key in your .env file.")
        sys.exit(1)
    
    # Optional: Test actual API connectivity
    print("\nAPI Connectivity:")
    
    if settings.openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            # Try a minimal API call
            response = client.chat.completions.create(
                model=settings.model_name_openai,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            print(f"  ✓ OpenAI API: Connected ({settings.model_name_openai})")
        except Exception as e:
            print(f"  ✗ OpenAI API: Failed - {e}")
    else:
        print("  - OpenAI API: Skipped (no key)")
    
    if settings.anthropic_api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            # Try a minimal API call
            message = client.messages.create(
                model=settings.model_name_anthropic,
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}],
            )
            print(f"  ✓ Anthropic API: Connected ({settings.model_name_anthropic})")
        except Exception as e:
            print(f"  ✗ Anthropic API: Failed - {e}")
    else:
        print("  - Anthropic API: Skipped (no key)")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
