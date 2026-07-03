from opentelemetry import trace, metrics
from typing import ContextManager
import time
from contextlib import contextmanager

tracer = trace.get_tracer("semantic-cache")
meter = metrics.get_meter("semantic-cache")

request_counter = meter.create_counter(
    "cache.requests",
    description="Total number of requests",
)

hit_counter = meter.create_counter(
    "cache.hits",
    description="Number of cache hits",
)

miss_counter = meter.create_counter(
    "cache.misses",
    description="Number of cache misses",
)

tokens_saved_counter = meter.create_counter(
    "cache.tokens_saved",
    description="Number of tokens saved via cache hits"
)

cost_saved_counter = meter.create_counter(
    "cache.cost_saved",
    description="Estimated cost saved in dollars"
)

latency_histogram = meter.create_histogram(
    "cache.latency",
    description="Latency of operations",
    unit="ms"
)

@contextmanager
def record_latency(operation: str) -> ContextManager[None]:
    start_time = time.time()
    try:
        yield
    finally:
        latency_ms = (time.time() - start_time) * 1000
        latency_histogram.record(latency_ms, {"operation": operation})

def record_hit(layer: str):
    hit_counter.add(1, {"layer": layer})

def record_miss(layer: str):
    miss_counter.add(1, {"layer": layer})
