import os
import litellm
import structlog
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Configure structlog logger
logger = structlog.get_logger()

class LLMService:
    def __init__(self):
        # Allow configuring model via env var, default to something cheap/standard
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
        # Configure LiteLLM callbacks
        # simple_proxy just logs to console by default, but we can add 'lunary', 'langfuse' etc to this list
        litellm.success_callback = ["simple_proxy"]
        litellm.failure_callback = ["simple_proxy"]
        
        # If a specific observability tool is set in env, add it
        observability_tool = os.getenv("LITELLM_CALLBACK")
        if observability_tool:
            litellm.success_callback.append(observability_tool)
            litellm.failure_callback.append(observability_tool)

    async def generate_response(self, system_prompt: str, user_prompt: str, json_mode: bool = False, user_id: Optional[str] = None) -> Optional[str]:
        """
        Generate a response using LiteLLM.
        """
        try:
            # Check for API Key presence before call to avoid hard crash if not set
            # (LiteLLM usually handles this but good for our safety check)
            if not os.getenv("OPENAI_API_KEY") and "gpt" in self.model:
                 logger.warning("OPENAI_API_KEY not set. Skipping LLM call.")
                 return None

            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "metadata": {"user_id": user_id} if user_id else {}
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = await litellm.acompletion(**kwargs)
            
            content = response.choices[0].message.content
            
            # Log usage for cost tracking (LiteLLM does this internally but nice to have in app logs too)
            usage = response.usage
            logger.info("LLM Call Success", model=self.model, usage=dict(usage))
            
            return content

        except Exception as e:
            logger.error("LLM Generation Failed", error=str(e))
            return None

llm_service = LLMService()
