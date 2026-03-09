from __future__ import annotations

import logging
import pickle
from typing import Any, Callable, TypeVar

import redis as redis_module
from django.conf import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_TTL: int = getattr(settings, "CACHE_SERVICE_DEFAULT_TTL", 60 * 60)


def _build_redis_client() -> redis_module.Redis:
    try:
        from django_redis import get_redis_connection

        return get_redis_connection("default")
    except ImportError:
        url: str = settings.CACHES.get("default", {}).get(
            "LOCATION", "redis://127.0.0.1:6379/1"
        )
        return redis_module.from_url(url)


_redis: redis_module.Redis = _build_redis_client()


class CacheService:
    """
    Generic, namespaced cache service backed by Redis.

    Uses pickle for serialisation so it can store any Python object —
    model instances, querysets, dicts, bytes, etc.
    """

    def __init__(self, namespace: str, *, default_ttl: int = DEFAULT_TTL) -> None:
        if not namespace:
            raise ValueError("CacheService namespace must be a non-empty string.")
        self._namespace = namespace
        self._default_ttl = default_ttl

    def make_key(self, key: str) -> str:
        return f"{self._namespace}:{key}"

    def _get_ttl(self, ttl: int | None) -> int:
        return ttl if ttl is not None else self._default_ttl

    def _scan_keys(self, pattern: str) -> list[bytes]:
        matched: list[bytes] = []
        cursor = 0
        while True:
            cursor, keys = _redis.scan(cursor, match=pattern, count=200)  # type: ignore
            matched.extend(keys)
            if cursor == 0:
                break
        return matched

    def get(self, key: str) -> Any | None:
        full_key = self.make_key(key)
        try:
            raw = _redis.get(full_key)
            if raw is None:
                return None
            return pickle.loads(raw)  # type: ignore
        except Exception as exc:
            logger.warning(
                "CacheService[%s] GET failed for %r: %s", self._namespace, key, exc
            )
            return None

    def set(self, key: str, value: Any, *, ttl: int | None = None) -> bool:
        full_key = self.make_key(key)
        effective_ttl = self._get_ttl(ttl)
        try:
            _redis.set(full_key, pickle.dumps(value), ex=effective_ttl)
            return True
        except Exception as exc:
            logger.warning(
                "CacheService[%s] SET failed for %r: %s", self._namespace, key, exc
            )
            return False

    def delete(self, key: str) -> bool:
        full_key = self.make_key(key)
        try:
            return bool(_redis.delete(full_key))
        except Exception as exc:
            logger.warning(
                "CacheService[%s] DELETE failed for %r: %s", self._namespace, key, exc
            )
            return False

    def exists(self, key: str) -> bool:
        full_key = self.make_key(key)
        try:
            return bool(_redis.exists(full_key))
        except Exception as exc:
            logger.warning(
                "CacheService[%s] EXISTS failed for %r: %s", self._namespace, key, exc
            )
            return False

    def ttl(self, key: str) -> int:
        full_key = self.make_key(key)
        try:
            return int(_redis.ttl(full_key))  # type: ignore
        except Exception as exc:
            logger.warning(
                "CacheService[%s] TTL failed for %r: %s", self._namespace, key, exc
            )
            return -2

    def invalidate_prefix(self, prefix: str) -> int:
        pattern = self.make_key(f"{prefix}:*")
        try:
            keys = self._scan_keys(pattern)
            if not keys:
                return 0
            _redis.delete(*keys)
            return len(keys)
        except Exception as exc:
            logger.warning(
                "CacheService[%s] INVALIDATE_PREFIX failed for %r: %s",
                self._namespace,
                prefix,
                exc,
            )
            return 0

    def invalidate_namespace(self) -> int:
        pattern = self.make_key("*")
        try:
            keys = self._scan_keys(pattern)
            if not keys:
                return 0
            _redis.delete(*keys)
            return len(keys)
        except Exception as exc:
            logger.warning(
                "CacheService[%s] INVALIDATE_NAMESPACE failed: %s",
                self._namespace,
                exc,
            )
            return 0

    def get_or_set(
        self, key: str, compute: Callable[[], T], *, ttl: int | None = None
    ) -> T:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = compute()
        self.set(key, value, ttl=ttl)
        return value
