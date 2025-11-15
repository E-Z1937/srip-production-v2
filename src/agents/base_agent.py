"""Base agent with retry logic and caching"""
import time
import hashlib
import logging
from typing import Dict, Optional, List
from abc import ABC, abstractmethod
import groq
from groq import Groq
from src.config import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.cache: Dict[str, str] = {}
        self.metrics = {"total_calls": 0, "successful_calls": 0, "failed_calls": 0, "cache_hits": 0, "total_duration": 0.0}
        logger.info(f"Initialized {agent_name}")
    
    def _cache_key(self, content: str) -> str:
        return hashlib.sha256(f"{self.agent_name}:{content}".encode()).hexdigest()[:20]
    
    def _get_cached(self, key: str) -> Optional[str]:
        if settings.ENABLE_CACHE and key in self.cache:
            self.metrics["cache_hits"] += 1
            return self.cache[key]
        return None
    
    def _set_cache(self, key: str, value: str):
        if settings.ENABLE_CACHE:
            if len(self.cache) >= settings.CACHE_MAX_SIZE:
                oldest = list(self.cache.keys())[0]
                del self.cache[oldest]
            self.cache[key] = value
    
    def _execute_with_retry(self, messages: List[Dict], max_tokens: int, temperature: float = 0.1) -> str:
        models = [settings.GROQ_DEFAULT_MODEL] + settings.GROQ_FALLBACK_MODELS
        self.metrics["total_calls"] += 1
        start_time = time.time()
        
        for model in models:
            for attempt in range(settings.GROQ_MAX_RETRIES):
                try:
                    response = self.client.chat.completions.create(
                        model=model, messages=messages, max_tokens=max_tokens,
                        temperature=temperature, timeout=settings.GROQ_TIMEOUT
                    )
                    content = response.choices[0].message.content
                    duration = time.time() - start_time
                    self.metrics["successful_calls"] += 1
                    self.metrics["total_duration"] += duration
                    logger.info(f"{self.agent_name}: Success with {model} in {duration:.2f}s")
                    return content
                except groq.RateLimitError:
                    wait_time = (attempt + 1) * 15
                    logger.warning(f"{self.agent_name}: Rate limit, waiting {wait_time}s")
                    time.sleep(wait_time)
                except Exception as e:
                    logger.error(f"{self.agent_name}: Error with {model}: {e}")
                    break
        
        self.metrics["failed_calls"] += 1
        raise RuntimeError(f"{self.agent_name}: All models failed")
    
    def execute(self, query: str, context: Optional[str] = None, **kwargs) -> str:
        cache_key = self._cache_key(f"{query}:{context}")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        result = self._analyze(query, context, **kwargs)
        self._set_cache(cache_key, result)
        return result
    
    @abstractmethod
    def _analyze(self, query: str, context: Optional[str] = None, **kwargs) -> str:
        pass
    
    def get_metrics(self) -> dict:
        avg_duration = self.metrics["total_duration"] / self.metrics["successful_calls"] if self.metrics["successful_calls"] > 0 else 0.0
        return {"agent_name": self.agent_name, **self.metrics, "average_duration": avg_duration}
