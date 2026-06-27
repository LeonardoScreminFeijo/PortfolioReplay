from typing import Any

import diskcache

from app.core.config import settings

_cache: diskcache.Cache = diskcache.Cache(settings.cache_dir)


def get_cached(key: str) -> Any | None:
    return _cache.get(key)


def set_cached(key: str, value: Any) -> None:
    _cache.set(key, value, expire=settings.cache_ttl_hours * 3600)
