import time
import asyncio
from typing import Optional
from opentelemetry import trace

from .config import CacheConfig
from .models import CacheRecord, RequestRecord, ResponseSource
from .fingerprint import normalize, fingerprint
from .cache import CacheDB
from .vector_store import VectorStore
from .logging import RequestLogger
from .metrics import record_latency, request_counter, hit_counter, miss_counter, tokens_saved_counter, cost_saved_counter
from .providers.base import BaseProvider
from .embeddings import BaseEmbeddingModel

tracer = trace.get_tracer("semantic-cache")

class SemanticCache:
    def __init__(
        self,
        provider: Optional[BaseProvider] = None,
        embedding_model: Optional[BaseEmbeddingModel] = None,
        **kwargs
    ):
        self.config = CacheConfig(**kwargs)
        
        self.db = CacheDB(db_path=self.config.db_path)
        self.logger = RequestLogger(db_path=self.config.db_path)
        self.vector_store = VectorStore(dimension=self.config.vector_dim, index_path=self.config.index_path)
        
        if provider is None:
            if self.config.provider == "gemini":
                from .providers.gemini import GeminiProvider
                self.provider = GeminiProvider(model=self.config.model)
            else:
                raise ValueError("Provider not injected and default is unsupported.")
        else:
            self.provider = provider
            
        if embedding_model is None:
            if self.config.embedding_model == "text-embedding-004":
                from .embeddings import GeminiEmbedding
                self.embedding_model = GeminiEmbedding(model_name=self.config.embedding_model)
            else:
                raise ValueError("Embedding model not injected.")
        else:
            self.embedding_model = embedding_model

    def _evict_if_needed(self):
        if self.config.max_entries > 0:
            evicted_faiss_ids = self.db.evict_oldest(self.config.max_entries)
            if evicted_faiss_ids:
                self.vector_store.remove(evicted_faiss_ids)
                self.vector_store.save()

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        request_counter.add(1)
        total_start = time.time()
        
        exact_hit = False
        semantic_hit = False
        similarity_score = None
        source = ResponseSource.LLM
        response_text = ""
        
        latencies = {'exact': 0.0, 'embed': 0.0, 'search': 0.0, 'provider': 0.0, 'write': 0.0}
        tokens_in = 0
        tokens_out = 0
        tokens_saved = 0
        cost_saved = 0.0

        with tracer.start_as_current_span("generate"):
            # 1. Normalize & Fingerprint
            norm_prompt = normalize(prompt)
            prompt_fp = fingerprint(norm_prompt)
            
            # 2. Exact Cache Lookup
            t0 = time.time()
            record = self.db.lookup_by_fingerprint(prompt_fp, ttl_days=self.config.ttl_days)
            latencies['exact'] = (time.time() - t0) * 1000
            
            if record:
                exact_hit = True
                source = ResponseSource.EXACT_CACHE
                response_text = record.response
                self.db.update_hit(record.id)
                hit_counter.add(1, {"layer": "exact"})
            else:
                # 3. Embedding Generation
                t0 = time.time()
                query_embedding = self.embedding_model.embed(prompt)
                latencies['embed'] = (time.time() - t0) * 1000
                
                # 4. Vector Search
                t0 = time.time()
                results = self.vector_store.search(query_embedding, top_k=1)
                latencies['search'] = (time.time() - t0) * 1000
                
                # 5. Threshold Check
                if results and results[0][1] >= self.config.similarity_threshold:
                    semantic_hit = True
                    source = ResponseSource.SEMANTIC_CACHE
                    faiss_id, similarity_score = results[0]
                    record = self.db.lookup_by_faiss_id(faiss_id, ttl_days=self.config.ttl_days)
                    if record:
                        response_text = record.response
                        self.db.update_hit(record.id)
                        hit_counter.add(1, {"layer": "semantic"})
                    else:
                        # Record missing in DB but exists in FAISS (inconsistent state)
                        self.vector_store.remove([faiss_id])
                        semantic_hit = False
                        source = ResponseSource.LLM
                
                if not exact_hit and not semantic_hit:
                    miss_counter.add(1)
                    
                    # 6. Provider Call
                    t0 = time.time()
                    response_text = self.provider.generate(prompt, temperature=temperature)
                    latencies['provider'] = (time.time() - t0) * 1000
                    
                    tokens_in = self.provider.count_tokens(prompt)
                    tokens_out = self.provider.count_tokens(response_text)
                    
                    # 7. Store Cache & Vector
                    t0 = time.time()
                    new_faiss_id = self.vector_store.next_id()
                    new_record = CacheRecord(
                        faiss_id=new_faiss_id,
                        prompt=prompt,
                        fingerprint=prompt_fp,
                        response=response_text,
                        provider=self.provider.model_name(),
                        model=self.provider.model_name(),
                        temperature=temperature,
                        ttl=self.config.ttl_days
                    )
                    record_id = self.db.store(new_record)
                    self.vector_store.add(query_embedding, new_faiss_id)
                    self.vector_store.save()
                    latencies['write'] = (time.time() - t0) * 1000
                    
                    self._evict_if_needed()

            total_latency = (time.time() - total_start) * 1000
            
            # Reconstruct tokens for hits to calculate savings
            if exact_hit or semantic_hit:
                # Approximate tokens saved based on current prompt and cached response
                tokens_in = self.provider.count_tokens(prompt)
                tokens_out = self.provider.count_tokens(response_text)
                tokens_saved = tokens_in + tokens_out
                cost_saved = tokens_saved * 0.000001
                tokens_saved_counter.add(tokens_saved)
                cost_saved_counter.add(cost_saved)

            if self.config.log_requests:
                self.logger.log(RequestRecord(
                    prompt=prompt,
                    fingerprint=prompt_fp,
                    exact_hit=exact_hit,
                    semantic_hit=semantic_hit,
                    similarity=similarity_score,
                    latency_ms=total_latency,
                    provider_latency_ms=latencies['provider'],
                    embedding_latency_ms=latencies['embed'],
                    tokens_input=tokens_in,
                    tokens_output=tokens_out,
                    tokens_saved=tokens_saved,
                    estimated_cost_saved=cost_saved,
                    response_source=source
                ))

            return response_text

    async def agenerate(self, prompt: str, temperature: float = 0.7) -> str:
        request_counter.add(1)
        total_start = time.time()
        
        exact_hit = False
        semantic_hit = False
        similarity_score = None
        source = ResponseSource.LLM
        response_text = ""
        
        latencies = {'exact': 0.0, 'embed': 0.0, 'search': 0.0, 'provider': 0.0, 'write': 0.0}
        tokens_in = 0
        tokens_out = 0
        tokens_saved = 0
        cost_saved = 0.0

        # Note: OpenTelemetry async support varies, keeping basic telemetry for now
        with tracer.start_as_current_span("agenerate"):
            norm_prompt = normalize(prompt)
            prompt_fp = fingerprint(norm_prompt)
            
            t0 = time.time()
            record = await asyncio.to_thread(self.db.lookup_by_fingerprint, prompt_fp, self.config.ttl_days)
            latencies['exact'] = (time.time() - t0) * 1000
            
            if record:
                exact_hit = True
                source = ResponseSource.EXACT_CACHE
                response_text = record.response
                await asyncio.to_thread(self.db.update_hit, record.id)
                hit_counter.add(1, {"layer": "exact"})
            else:
                t0 = time.time()
                query_embedding = await self.embedding_model.aembed(prompt)
                latencies['embed'] = (time.time() - t0) * 1000
                
                t0 = time.time()
                results = await asyncio.to_thread(self.vector_store.search, query_embedding, 1)
                latencies['search'] = (time.time() - t0) * 1000
                
                if results and results[0][1] >= self.config.similarity_threshold:
                    semantic_hit = True
                    source = ResponseSource.SEMANTIC_CACHE
                    faiss_id, similarity_score = results[0]
                    record = await asyncio.to_thread(self.db.lookup_by_faiss_id, faiss_id, self.config.ttl_days)
                    if record:
                        response_text = record.response
                        await asyncio.to_thread(self.db.update_hit, record.id)
                        hit_counter.add(1, {"layer": "semantic"})
                    else:
                        await asyncio.to_thread(self.vector_store.remove, [faiss_id])
                        semantic_hit = False
                        source = ResponseSource.LLM
                
                if not exact_hit and not semantic_hit:
                    miss_counter.add(1)
                    
                    t0 = time.time()
                    response_text = await self.provider.agenerate(prompt, temperature=temperature)
                    latencies['provider'] = (time.time() - t0) * 1000
                    
                    # Fetch token counts asynchronously or concurrently
                    t_in = asyncio.create_task(self.provider.acount_tokens(prompt))
                    t_out = asyncio.create_task(self.provider.acount_tokens(response_text))
                    tokens_in, tokens_out = await asyncio.gather(t_in, t_out)
                    
                    t0 = time.time()
                    new_faiss_id = self.vector_store.next_id()
                    new_record = CacheRecord(
                        faiss_id=new_faiss_id,
                        prompt=prompt,
                        fingerprint=prompt_fp,
                        response=response_text,
                        provider=self.provider.model_name(),
                        model=self.provider.model_name(),
                        temperature=temperature,
                        ttl=self.config.ttl_days
                    )
                    record_id = await asyncio.to_thread(self.db.store, new_record)
                    await asyncio.to_thread(self.vector_store.add, query_embedding, new_faiss_id)
                    await asyncio.to_thread(self.vector_store.save)
                    latencies['write'] = (time.time() - t0) * 1000
                    
                    await asyncio.to_thread(self._evict_if_needed)

            total_latency = (time.time() - total_start) * 1000
            
            if exact_hit or semantic_hit:
                t_in = asyncio.create_task(self.provider.acount_tokens(prompt))
                t_out = asyncio.create_task(self.provider.acount_tokens(response_text))
                tokens_in, tokens_out = await asyncio.gather(t_in, t_out)
                tokens_saved = tokens_in + tokens_out
                cost_saved = tokens_saved * 0.000001
                tokens_saved_counter.add(tokens_saved)
                cost_saved_counter.add(cost_saved)

            if self.config.log_requests:
                await asyncio.to_thread(
                    self.logger.log,
                    RequestRecord(
                        prompt=prompt,
                        fingerprint=prompt_fp,
                        exact_hit=exact_hit,
                        semantic_hit=semantic_hit,
                        similarity=similarity_score,
                        latency_ms=total_latency,
                        provider_latency_ms=latencies['provider'],
                        embedding_latency_ms=latencies['embed'],
                        tokens_input=tokens_in,
                        tokens_output=tokens_out,
                        tokens_saved=tokens_saved,
                        estimated_cost_saved=cost_saved,
                        response_source=source
                    )
                )

            return response_text
