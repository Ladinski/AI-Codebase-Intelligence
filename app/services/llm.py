import httpx

from app.core.config import settings


class LLMService:
    def generate(
        self,
        prompt: str,
    ) -> dict:
        response = httpx.post(
            f"{settings.ollama_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                },
            },
            timeout=120.0,
        )

        response.raise_for_status()

        data = response.json()

        return {
            "answer": data.get("response", "").strip(),
            "prompt_tokens": data.get(
                "prompt_eval_count",
                0,
            ),
            "completion_tokens": data.get(
                "eval_count",
                0,
            ),
        }