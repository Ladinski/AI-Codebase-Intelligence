import hashlib
import json

from redis import Redis

from app.core.config import settings


class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    def build_rag_key(
        self,
        repository_id: int,
        query: str,
        top_k: int,
    ) -> str:
        normalized_query = query.strip().lower()

        raw_key = (
            f"{repository_id}:"
            f"{normalized_query}:"
            f"{top_k}"
        )

        digest = hashlib.sha256(
            raw_key.encode("utf-8")
        ).hexdigest()

        return f"rag:{digest}"

    def get_json(
        self,
        key: str,
    ) -> dict | None:
        value = self.redis.get(key)

        if value is None:
            return None

        return json.loads(value)

    def set_json(
        self,
        key: str,
        value: dict,
        ttl_seconds: int,
    ) -> None:
        self.redis.setex(
            key,
            ttl_seconds,
            json.dumps(value),
        )