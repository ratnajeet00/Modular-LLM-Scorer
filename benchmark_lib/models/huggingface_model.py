from __future__ import annotations

from .base_model import BaseModel


class HuggingFaceModel(BaseModel):
    """Support for Hugging Face models via Transformers or Inference API."""

    def __init__(
        self,
        model: str,
        api_token: str = "",
        use_inference_api: bool = False,
        device: str = "cpu",
    ) -> None:
        """
        Initialize Hugging Face model.

        Args:
            model: Model ID (e.g., "meta-llama/Llama-2-7b" or "mistralai/Mistral-7B")
            api_token: Hugging Face API token (from https://huggingface.co/settings/tokens)
            use_inference_api: If True, use HF Inference API instead of local transformers
            device: Device to use for local inference ("cpu", "cuda", "mps")
        """
        if not model:
            raise ValueError("A Hugging Face model ID is required (e.g., meta-llama/Llama-2-7b)")
        
        self.model_id = model
        self.api_token = api_token
        self.use_inference_api = use_inference_api
        self.device = device
        self.model_name = f"huggingface:{model}"
        self._pipeline = None
        self._last_cost = 0.0
        
        if use_inference_api:
            self._init_inference_api()
        else:
            self._init_local_model()

    def _init_inference_api(self) -> None:
        """Initialize Hugging Face Inference API client."""
        try:
            from huggingface_hub import InferenceClient
        except ImportError as exc:
            raise ImportError("Install huggingface-hub to use HF Inference API") from exc
        
        if not self.api_token:
            raise ValueError(
                "HF_API_TOKEN is required for Inference API. "
                "Get it from https://huggingface.co/settings/tokens"
            )
        
        self._client = InferenceClient(model=self.model_id, token=self.api_token)

    def _init_local_model(self) -> None:
        """Initialize local Transformers pipeline for inference."""
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise ImportError("Install transformers and torch to use local HF models") from exc
        
        # Create text-generation pipeline
        self._pipeline = pipeline(
            "text-generation",
            model=self.model_id,
            device_map="auto" if self.device == "cuda" else self.device,
            model_kwargs={"torch_dtype": "auto"},
            trust_remote_code=True,
        )

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        """Generate response from Hugging Face model."""
        if self.use_inference_api:
            return self._generate_inference_api(prompt, max_tokens)
        else:
            return self._generate_local(prompt, max_tokens)

    def _generate_inference_api(self, prompt: str, max_tokens: int | None = None) -> str:
        """Generate using HF Inference API with fallback for custom providers."""
        kwargs = {
            "max_new_tokens": max_tokens or 256,
            "temperature": 0.2,
        }
        
        try:
            response = self._client.text_generation(prompt, **kwargs)
            return response.strip()
        except Exception as e:
            # Fallback for models on providers that don't support text_generation task
            # (e.g., DeepSeek on nscale provider that only supports chat.completions)
            error_msg = str(e)
            if "not supported" in error_msg.lower() or "available tasks" in error_msg.lower():
                return self._generate_inference_api_chat_fallback(prompt, max_tokens)
            raise  # Re-raise if not a task-support issue

    def _generate_inference_api_chat_fallback(self, prompt: str, max_tokens: int | None = None) -> str:
        """Fallback: Use chat.completions API when text_generation task isn't supported."""
        try:
            # Use chat.completions which supports conversational task
            response = self._client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=max_tokens or 256,
                temperature=0.2,
            )
            
            # Extract text from response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            
            raise RuntimeError("No response from chat.completions API")
        except Exception as e:
            raise RuntimeError(f"HF API chat.completions fallback failed: {str(e)}") from e

    def _generate_local(self, prompt: str, max_tokens: int | None = None) -> str:
        """Generate using local Transformers pipeline."""
        if self._pipeline is None:
            raise RuntimeError("Pipeline not initialized")
        
        # Generate with specified max_tokens
        outputs = self._pipeline(
            prompt,
            max_new_tokens=max_tokens or 256,
            temperature=0.2,
            top_p=1.0,
            do_sample=False,  # Greedy decoding for determinism
            num_return_sequences=1,
        )
        
        # Pipeline returns list of dicts with 'generated_text' key
        generated = outputs[0]["generated_text"]
        
        # Remove the prompt from the output to get just the generated part
        if generated.startswith(prompt):
            return generated[len(prompt) :].strip()
        
        return generated.strip()

    def get_last_cost(self) -> float:
        """Return cost (0 for local models, may vary for API)."""
        return self._last_cost
