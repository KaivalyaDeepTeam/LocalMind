#!/usr/bin/env python3
"""
Test script to demonstrate JSON Schema-based constrained generation.

This shows how the schema guarantees valid JSON output from local LLMs.
"""

import json

from localmind.workers.audit_worker import (
    DEFAULT_PARAMETERS,
    create_audit_json_schema,
)


def main():
    """Demonstrate JSON schema generation."""
    print("=" * 70)
    print("JSON Schema-Based Constrained Generation for LocalMind")
    print("=" * 70)
    print()

    # Generate schema from default parameters
    schema = create_audit_json_schema(DEFAULT_PARAMETERS)

    print("Generated JSON Schema for Audit Results:")
    print("-" * 70)
    print(json.dumps(schema, indent=2))
    print()

    print("Benefits of Schema-Based Constrained Generation:")
    print("-" * 70)
    print("✅ Guarantees valid JSON structure")
    print("✅ Enforces required fields (all parameters, strengths, improvements)")
    print("✅ Validates data types (numbers for scores, arrays for lists)")
    print("✅ Enforces score ranges (0 to max_score for each parameter)")
    print("✅ Prevents hallucinated fields (additionalProperties: false)")
    print("✅ Enforces array lengths (2-4 items for strengths/improvements)")
    print()

    print("How it works:")
    print("-" * 70)
    print("1. Schema defines exact structure expected from LLM")
    print("2. llama-cpp-python uses grammar-based sampling")
    print("3. LLM can ONLY generate tokens that match the schema")
    print("4. Result: 100% valid JSON, no parsing errors")
    print()

    print("Schema Features:")
    print("-" * 70)
    print(f"• Required parameters: {len(DEFAULT_PARAMETERS)}")
    print(f"• Parameter names: {', '.join(p['name'] for p in DEFAULT_PARAMETERS)}")
    print("• Score validation: 0 to max_score for each parameter")
    print("• Strengths/improvements: 2-4 items required")
    print("• No extra fields allowed (strict validation)")
    print()


if __name__ == "__main__":
    main()
