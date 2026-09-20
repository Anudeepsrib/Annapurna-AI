import asyncio
import time
from typing import Optional

import litellm
import structlog

from app.core.config import settings

# Configure structlog logger
logger = structlog.get_logger()


class LLMService:
    def __init__(self):
        # Use settings from config (local-first defaults)
        self.provider = settings.LLM_PROVIDER
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.api_key = settings.LLM_API_KEY
        self.timeout_seconds = settings.LLM_TIMEOUT_SECONDS
        self.max_retries = settings.LLM_MAX_RETRIES
        self.failure_threshold = settings.LLM_CIRCUIT_BREAKER_FAILURES
        self.breaker_seconds = settings.LLM_CIRCUIT_BREAKER_SECONDS
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0
        self.last_failure_code: str | None = None

        # Disable LiteLLM callbacks for privacy (local mode)
        litellm.success_callback = []
        litellm.failure_callback = []
        litellm.callbacks = []
        setattr(litellm, "telemetry", False)
        setattr(litellm, "turn_off_message_logging", True)

    def _get_model_string(self) -> str:
        """
        Build the model string for LiteLLM based on provider.
        - Ollama: 'ollama/llama3.2:latest'
        - OpenAI-compatible (LM Studio, llama.cpp): 'openai/custom-model-name'
        """
        if self.provider == "ollama":
            return f"ollama/{self.model}"
        # For LM Studio, llama.cpp, LocalAI, etc.
        # They use OpenAI-compatible API, so prefix with 'openai/'.
        return f"openai/{self.model}"

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a response using LiteLLM.
        Defaults are local-first; a non-local custom endpoint can send prompt data
        outside the machine and is gated by configuration.
        """
        if time.monotonic() < self._circuit_open_until:
            self.last_failure_code = "LLM_UNAVAILABLE"
            logger.warning("LLM circuit open", provider=self.provider, model=self.model)
            return None

        self.last_failure_code = None
        model_string = self._get_model_string()
        kwargs = {
            "model": model_string,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "api_base": self.base_url,
            "api_key": self.api_key,
            "timeout": self.timeout_seconds,
            "metadata": {"user_id": user_id or "local-user"},
        }

        if json_mode:
            kwargs["messages"].append(
                {
                    "role": "system",
                    "content": (
                        "CRITICAL: Output only valid JSON. Do not include markdown fences, "
                        "comments, or text before or after the JSON."
                    ),
                }
            )

            kwargs["response_format"] = {"type": "json_object"}

            if self.provider == "ollama":
                kwargs["format"] = "json"

        for attempt in range(self.max_retries + 1):
            try:
                logger.info("LLM call starting", provider=self.provider, model=self.model, attempt=attempt + 1)
                response = await litellm.acompletion(**kwargs)
                self._consecutive_failures = 0
                self._circuit_open_until = 0.0
                self.last_failure_code = None
                content = response.choices[0].message.content
                logger.info("LLM call succeeded", model=model_string, usage=dict(response.usage or {}))
                return content
            except Exception as exc:
                if attempt < self.max_retries:
                    await asyncio.sleep(0.25 * (2**attempt))
                    continue
                self._consecutive_failures += 1
                self.last_failure_code = "LLM_TIMEOUT" if isinstance(exc, TimeoutError) else "LLM_UNAVAILABLE"
                if self._consecutive_failures >= self.failure_threshold:
                    self._circuit_open_until = time.monotonic() + self.breaker_seconds
                logger.warning(
                    "LLM generation failed",
                    error=exc.__class__.__name__,
                    provider=self.provider,
                    attempts=attempt + 1,
                )
                return None

    async def test_connection(self) -> dict:
        """
        Test the LLM connection and return status info.
        """
        try:
            model_string = self._get_model_string()
            # Simple test prompt
            await litellm.acompletion(
                model=model_string,
                messages=[{"role": "user", "content": "Say 'OK'"}],
                api_base=self.base_url,
                api_key=self.api_key,
                max_tokens=5,
                timeout=10,
            )
            return {
                "status": "connected",
                "provider": self.provider,
                "model": self.model,
                "base_url": self.base_url,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "provider": self.provider,
                "model": self.model,
            }


llm_service = LLMService()
