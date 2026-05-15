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
        Generate a response using LiteLLM with local LLM endpoint.
        No data leaves the user's machine.
        """
        try:
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
                "timeout": 30,
                "metadata": {"user_id": user_id or "local-user"},
            }

            if json_mode:
                # Add strict instructions for smaller local-LLMs that struggle with formatting
                kwargs["messages"].append(
                    {
                        "role": "system",
                        "content": (
                            "CRITICAL: Output only valid JSON. Do not include markdown fences, "
                            "comments, or text before or after the JSON."
                        ),
                    }
                )

                # LitellM supports 'response_format' mapping, but some older/smaller providers reject it.
                # We try applying it but if it fails, the system prompt acts as a fallback.
                kwargs["response_format"] = {"type": "json_object"}

                # For Ollama, native format passing is safer for older versions
                if self.provider == "ollama":
                    kwargs["format"] = "json"

            logger.info("LLM call starting", provider=self.provider, model=self.model)

            response = await litellm.acompletion(**kwargs)

            content = response.choices[0].message.content

            # Log usage locally only
            usage = response.usage
            logger.info("LLM call succeeded", model=model_string, usage=dict(usage or {}))

            return content

        except Exception as e:
            logger.warning("LLM generation failed", error=str(e), provider=self.provider)
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
