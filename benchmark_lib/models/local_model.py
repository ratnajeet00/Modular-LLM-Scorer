from __future__ import annotations

import requests

from .base_model import BaseModel


class LocalModel(BaseModel):
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "",
    ) -> None:
        if not model:
            raise ValueError("A local model name is required")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = f"local:{model}"
        self._last_cost = 0.0

    @staticmethod
    def _strip_v1_suffix(base_url: str) -> str:
        normalized = base_url.rstrip("/")
        if normalized.endswith("/v1"):
            return normalized[:-3]
        return normalized

    @staticmethod
    def _parse_openai_chat_response(payload: dict) -> str:
        return payload["choices"][0]["message"]["content"].strip()

    @staticmethod
    def _parse_ollama_chat_response(payload: dict) -> str:
        message = payload.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        # Fallback for generate-like payloads.
        response = payload.get("response")
        if isinstance(response, str):
            return response.strip()
        raise KeyError("No assistant content found in local provider response")

    def _post(self, url: str, headers: dict[str, str], body: dict) -> requests.Response:
        return requests.post(url, headers=headers, json=body, timeout=60)

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        errors: list[str] = []
        
        # Retry logic: start with max_tokens, retry with half on 402 or token errors
        current_max_tokens = max_tokens
        retry_count = 0
        max_retries = 2

        while retry_count <= max_retries:
            # Try OpenAI-compatible local endpoints first.
            try:
                body_dict: dict = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                }
                if current_max_tokens:
                    body_dict["max_tokens"] = current_max_tokens
                
                response = self._post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    body=body_dict,
                )
                
                # Handle 402 (payment required) or token errors
                if response.status_code == 402:
                    if current_max_tokens and current_max_tokens > 64 and retry_count < max_retries:
                        current_max_tokens = max(64, current_max_tokens // 2)
                        retry_count += 1
                        continue
                    response.raise_for_status()
                
                response.raise_for_status()
                payload = response.json()
                usage = payload.get("usage", {})
                self._last_cost = float(usage.get("cost", 0.0) or 0.0)
                return self._parse_openai_chat_response(payload)
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                body = ""
                if exc.response is not None:
                    try:
                        body = exc.response.text[:300]
                    except Exception:
                        body = ""
                errors.append(f"openai-chat {status}: {body}".strip())
                body_lc = body.lower()
                # If endpoint exists but model is missing/invalid, return immediately.
                if "model" in body_lc and ("not found" in body_lc or "does not exist" in body_lc):
                    raise RuntimeError(errors[-1]) from exc
                # Fall back to Ollama-native endpoint for missing route errors.
                if status not in {404, 405}:
                    raise RuntimeError(errors[-1]) from exc
                break  # Exit retry loop and try Ollama fallback
            except Exception as exc:
                errors.append(f"openai-chat error: {exc}")
                break  # Exit retry loop and try Ollama fallback

        # Ollama native endpoint fallback: /api/chat
        native_base = self._strip_v1_suffix(self.base_url)
        try:
            body_dict: dict = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0},
            }
            if current_max_tokens:
                body_dict["options"]["num_predict"] = current_max_tokens
            
            response = self._post(
                f"{native_base}/api/chat",
                headers=headers,
                body=body_dict,
            )
            response.raise_for_status()
            payload = response.json()
            self._last_cost = 0.0
            return self._parse_ollama_chat_response(payload)
        except Exception as exc:
            errors.append(f"ollama-chat error: {exc}")
            raise RuntimeError(" | ".join(errors)) from exc

    def get_last_cost(self) -> float:
        return self._last_cost
