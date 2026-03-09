from __future__ import annotations

import json
import logging
from typing import Any, Callable, TypeVar

import redis as redis_module
from django.conf import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_TTL: int = getattr(settings, "CACHE_SERVICE_DEFAULT_TTL", 60 * 60)


def _build_redis_client() -> redis_module.Redis:
    """
    Returns a Redis client using django-redis's connection pool if available,
    otherwise falls back to a direct redis-py connection.
    """
    try:
        from django_redis import get_redis_connection

        return get_redis_connection("default")
    except ImportError:
        url: str = settings.CACHES.get("default", {}).get(
            "LOCATION", "redis://127.0.0.1:6379/1"
        )
        return redis_module.from_url(url)


_redis: redis_module.Redis = _build_redis_client()


def _encode(value: Any) -> bytes:
    """Serialise a value to bytes for storage."""
    return json.dumps(value).encode()


def _decode(raw: bytes) -> Any:
    """Deserialise bytes back to a Python value."""
    return json.loads(raw)


class CacheService:
    """
    Generic, namespaced cache service backed by Redis.
    """

    def __init__(self, namespace: str, *, default_ttl: int = DEFAULT_TTL) -> None:
        if not namespace:
            raise ValueError("CacheService namespace must be a non-empty string.")
        self._namespace = namespace
        self._default_ttl = default_ttl

    def make_key(self, key: str) -> str:
        """Returns the fully-namespaced Redis key."""
        return f"{self._namespace}:{key}"

    def _scan_keys(self, pattern: str) -> list[bytes]:
        """
        Returns all Redis keys matching *pattern*.
        Uses SCAN to avoid blocking the server on large keyspaces.
        """
        matched: list[bytes] = []
        cursor = 0
        while True:
            cursor, keys = _redis.scan(cursor, match=pattern, count=200)  # type: ignore
            matched.extend(keys)
            if cursor == 0:
                break
        return matched

    def _get_ttl(self, ttl: int | None) -> int:
        return ttl if ttl is not None else self._default_ttl

    def get(self, key: str) -> Any | None:
        """
        Retrieve a value by key.
        Returns None on cache miss or error.
        """
        full_key = self.make_key(key)
        try:
            raw = _redis.get(full_key)
            if raw is None:
                return None
            return _decode(raw)  # type: ignore
        except Exception as exc:
            logger.warning(
                "CacheService[%s] GET failed for %r: %s", self._namespace, key, exc
            )
            return None

    def set(self, key: str, value: Any, *, ttl: int | None = None) -> bool:
        """
        Store a value under key with an optional TTL (seconds).
        Falls back to default_ttl if ttl is not provided.
        Returns True on success, False on failure.
        """
        full_key = self.make_key(key)
        effective_ttl = self._get_ttl(ttl)
        try:
            _redis.set(full_key, _encode(value), ex=effective_ttl)
            return True
        except Exception as exc:
            logger.warning(
                "CacheService[%s] SET failed for %r: %s", self._namespace, key, exc
            )
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a single key.
        Returns True if the key existed and was deleted, False otherwise.
        """
        full_key = self.make_key(key)
        try:
            result = _redis.delete(full_key)
            return bool(result)
        except Exception as exc:
            logger.warning(
                "CacheService[%s] DELETE failed for %r: %s", self._namespace, key, exc
            )
            return False

    def exists(self, key: str) -> bool:
        """Return True if the key exists in the cache."""
        full_key = self.make_key(key)
        try:
            return bool(_redis.exists(full_key))
        except Exception as exc:
            logger.warning(
                "CacheService[%s] EXISTS failed for %r: %s", self._namespace, key, exc
            )
            return False

    def ttl(self, key: str) -> int:
        """
        Return the remaining TTL in seconds for a key.
        Returns -2 if the key does not exist, -1 if it has no expiry.
        """
        full_key = self.make_key(key)
        try:
            result = _redis.ttl(full_key)
            return int(result)  # type: ignore
        except Exception as exc:
            logger.warning(
                "CacheService[%s] TTL failed for %r: %s", self._namespace, key, exc
            )
            return -2

    def invalidate_prefix(self, prefix: str) -> int:
        """
        Delete all keys in this namespace that start with *prefix*.
        Returns the number of keys deleted.
        """
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
        """
        Delete every key in this namespace.
        Use with care — this clears the entire namespace.
        """
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
        self,
        key: str,
        compute: Callable[[], T],
        *,
        ttl: int | None = None,
    ) -> T:
        """
        Return the cached value for *key*, or call *compute()* to generate
        it, store it, and return it.
        """
        cached = self.get(key)
        if cached is not None:
            return cached

        value = compute()
        self.set(key, value, ttl=ttl)
        return value
