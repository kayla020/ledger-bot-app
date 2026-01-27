#!/usr/bin/env python3
"""Test LiteLLM connection and find valid model names"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Common model names to try (Bedrock format for Wealthsimple)
MODEL_NAMES = [
    "bedrock-claude-4.5-sonnet",
    "bedrock-claude-4.5-haiku",
    "bedrock-claude-4.5-opus",
    "bedrock-claude-4.0-sonnet",
    "bedrock-claude-3.5-sonnet",
    "bedrock-claude-3-sonnet",
    "gpt-4o",
    "gpt-4",
]

def test_model(client, model_name):
    """Test if a model name works"""
    try:
        response = client.chat.completions.create(
            model=model_name,
            max_tokens=10,
            messages=[{"role": "user", "content": "hi"}]
        )
        return True, response.choices[0].message.content
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 Testing LiteLLM Connection\n")
    print(f"Gateway: {os.environ.get('LITELLM_BASE_URL', 'https://llm.ws2.staging.w10e.com/api/v2')}")
    print(f"API Key: {os.environ.get('LITELLM_DEVELOPER_KEY', 'Not set')[:20]}...\n")

    client = OpenAI(
        api_key=os.environ["LITELLM_DEVELOPER_KEY"],
        base_url="https://llm.ws2.staging.w10e.com/api/v2",
        default_headers={"X-LiteLLM-Dev-Key": os.environ["LITELLM_DEVELOPER_KEY"]}
    )

    print("Testing common model names:\n")

    working_models = []
    for model_name in MODEL_NAMES:
        print(f"Testing: {model_name}...", end=" ")
        success, result = test_model(client, model_name)

        if success:
            print(f"✅ WORKS")
            working_models.append(model_name)
        else:
            # Only show first part of error
            error_msg = result.split('\n')[0][:60]
            print(f"❌ {error_msg}")

    print("\n" + "="*60)
    if working_models:
        print(f"\n✅ Found {len(working_models)} working model(s):")
        for model in working_models:
            print(f"   - {model}")
        print(f"\nAdd this to your .env file:")
        print(f"LITELLM_MODEL={working_models[0]}")
    else:
        print("\n❌ No working models found!")
        print("Contact your LiteLLM admin for the correct model name.")
    print("="*60)

if __name__ == "__main__":
    main()
