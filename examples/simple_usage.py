import os
import sys
import asyncio

# Add project root to path for local testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_cache import SemanticCache
from semantic_cache.providers.gemini import GeminiProvider
from semantic_cache.embeddings import GeminiEmbedding

async def main():
    if "GEMINI_API_KEY" not in os.environ:
        print("Please set the GEMINI_API_KEY environment variable.")
        return

    # Initialize cache using Dependency Injection
    cache = SemanticCache(
        provider=GeminiProvider(
            model="gemini-2.5-flash",
            cost_per_input_token=0.30 / 1_000_000,
            cost_per_output_token=2.50 / 1_000_000
        ),
        embedding_model=GeminiEmbedding(),
        similarity_threshold=0.92,
        ttl_days=30,
        max_entries=10000
    )

    prompts = [
        "What are the benefits of using Python?",
        "Why is Python a good programming language?", # Should be a semantic hit
        "Explain machine learning.",
    ]

    print("--- Synchronous Execution ---")
    for prompt in prompts:
        print(f"\\nPrompt: {prompt}")
        response = cache.generate(prompt=prompt, temperature=0.7)
        print(f"Response: {response[:100]}...")

    print("\\n--- Asynchronous Execution ---")
    async def fetch(p):
        res = await cache.agenerate(prompt=p, temperature=0.7)
        print(f"Async Response for '{p[:15]}...': {res[:50]}...")
        
    await asyncio.gather(*(fetch(p) for p in prompts))

if __name__ == "__main__":
    asyncio.run(main())
