import time
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_cache import SemanticCache
from semantic_cache.providers.gemini import GeminiProvider
from semantic_cache.embeddings import GeminiEmbedding

def run_benchmark():
    print("Initializing Semantic Cache (Production Configuration)...")
    if os.path.exists("semantic_cache.db"):
        os.remove("semantic_cache.db")
    if os.path.exists("semantic_cache.faiss"):
        os.remove("semantic_cache.faiss")

    cache = SemanticCache(
        provider=GeminiProvider(model="gemini-2.5-flash"),
        embedding_model=GeminiEmbedding(),
        similarity_threshold=0.90,
        db_path="semantic_cache.db",
        index_path="semantic_cache.faiss"
    )

    prompts = [
        "Explain quantum computing in simple terms.",
        "What is the capital of France?",
        "Explain quantum computing simply.", # Semantic hit
        "Capital of France?",                # Semantic hit
        "How do neural networks work?",
        "Explain quantum computing in simple terms.", # Exact hit
    ]

    print("Running Benchmark...")
    results = []
    latencies = []
    
    for i, prompt in enumerate(prompts):
        print(f"Request {i+1}: {prompt}")
        start_time = time.time()
        response = cache.generate(prompt)
        latency = (time.time() - start_time) * 1000
        latencies.append(latency)
        
        import sqlite3
        with sqlite3.connect("semantic_cache.db") as conn:
            conn.row_factory = sqlite3.Row
            log = conn.execute("SELECT * FROM request_logs ORDER BY id DESC LIMIT 1").fetchone()
            
        results.append({
            'prompt': prompt,
            'source': log['response_source'],
            'latency': latency,
            'similarity': log['similarity'] or 0.0,
            'tokens_saved': log['tokens_saved'] or 0,
            'cost_saved': log['estimated_cost_saved'] or 0.0
        })
        print(f"  Result: Source={log['response_source']}, Latency={latency:.1f}ms")

    # Metrics
    total_req = len(prompts)
    exact_hits = sum(1 for r in results if r['source'] == 'EXACT_CACHE')
    semantic_hits = sum(1 for r in results if r['source'] == 'SEMANTIC_CACHE')
    total_hits = exact_hits + semantic_hits
    provider_calls = total_req - total_hits
    
    avg_latency = np.mean(latencies)
    p50_latency = np.percentile(latencies, 50)
    p95_latency = np.percentile(latencies, 95)
    
    tokens_saved = sum(r['tokens_saved'] for r in results)
    cost_saved = sum(r['cost_saved'] for r in results)
    
    sim_scores = [r['similarity'] for r in results if r['similarity'] > 0]
    avg_similarity = np.mean(sim_scores) if sim_scores else 0.0

    report = f\"\"\"# Benchmark Report

## Summary
- **Total Requests**: {total_req}
- **Provider Calls**: {provider_calls}
- **Cache Hits**: {total_hits} (Exact: {exact_hits}, Semantic: {semantic_hits})
- **Hit Rate**: {(total_hits/total_req)*100:.1f}%

## Latency
- **Average**: {avg_latency:.1f} ms
- **P50**: {p50_latency:.1f} ms
- **P95**: {p95_latency:.1f} ms

## Savings & Accuracy
- **Tokens Saved**: {tokens_saved:,}
- **Estimated $ Saved**: ${cost_saved:.4f}
- **Average Similarity Score (for hits)**: {avg_similarity:.4f}

## Details
| Request | Prompt | Source | Latency (ms) | Similarity |
|---|---|---|---|---|
\"\"\"
    for i, r in enumerate(results):
        report += f"| {i+1} | {r['prompt']} | {r['source']} | {r['latency']:.1f} | {r['similarity']:.4f} |\n"

    with open("benchmark_report.md", "w") as f:
        f.write(report)
        
    print("\\nBenchmark complete. Report saved to benchmark_report.md")

if __name__ == "__main__":
    run_benchmark()
