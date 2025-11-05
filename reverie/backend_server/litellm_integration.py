"""
LiteLLM Integration - Unified LLM Access for All Providers

Supports:
- Local LLMs (Ollama, LM Studio, vLLM, Text Generation WebUI)
- Cloud providers (OpenAI, Anthropic, Google, Azure, Cohere, etc.)
- Image generation (DALL-E, Stable Diffusion, local models)
- Flexible configuration and fallbacks

This module replaces all direct LLM calls with LiteLLM for maximum flexibility.
"""

import os
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
import json
import logging

try:
    import litellm
    from litellm import completion, image_generation, acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logging.warning("LiteLLM not installed. Install with: pip install litellm")


@dataclass
class LLMConfig:
    """Configuration for a specific LLM provider"""
    provider: str  # "openai", "anthropic", "ollama", "azure", etc.
    model: str  # Model name
    api_base: Optional[str] = None  # For local/custom endpoints
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 300
    custom_llm_provider: Optional[str] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageGenConfig:
    """Configuration for image generation"""
    provider: str  # "openai", "replicate", "huggingface", "ollama"
    model: str  # "dall-e-3", "stability-ai/sdxl", etc.
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    size: str = "1024x1024"
    quality: str = "standard"  # "standard" or "hd" for DALL-E
    n: int = 1  # Number of images
    extra_params: Dict[str, Any] = field(default_factory=dict)


class LiteLLMManager:
    """
    Centralized manager for all LLM and image generation calls.

    Features:
    - Automatic provider detection
    - Fallback mechanisms
    - Cost tracking
    - Local LLM support (Ollama, LM Studio)
    - Unified API for all providers
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize LiteLLM manager.

        Args:
            config_path: Path to configuration JSON file
        """
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM not installed. Install with: pip install litellm")

        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "litellm_config.json"

        # Load configurations
        self.llm_configs: Dict[str, LLMConfig] = {}
        self.image_configs: Dict[str, ImageGenConfig] = {}
        self.default_llm: Optional[str] = None
        self.default_image_gen: Optional[str] = None

        # Load from file if exists
        self._load_config()

        # Set LiteLLM settings
        litellm.drop_params = True  # Drop unsupported params
        litellm.set_verbose = False  # Set to True for debugging

        # Initialize default configs if none loaded
        if not self.llm_configs:
            self._init_default_configs()

    def _load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)

                # Load LLM configs
                for name, cfg in config.get('llm_configs', {}).items():
                    self.llm_configs[name] = LLMConfig(**cfg)

                # Load image configs
                for name, cfg in config.get('image_configs', {}).items():
                    self.image_configs[name] = ImageGenConfig(**cfg)

                self.default_llm = config.get('default_llm')
                self.default_image_gen = config.get('default_image_gen')

                self.logger.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

    def _init_default_configs(self):
        """Initialize default configurations"""
        # Ollama local LLM (default for local usage)
        self.llm_configs['ollama_llama3'] = LLMConfig(
            provider="ollama",
            model="llama3",
            api_base="http://localhost:11434",
            temperature=0.7
        )

        self.llm_configs['ollama_mistral'] = LLMConfig(
            provider="ollama",
            model="mistral",
            api_base="http://localhost:11434",
            temperature=0.7
        )

        # OpenAI (if API key available)
        if os.getenv('OPENAI_API_KEY'):
            self.llm_configs['openai_gpt4'] = LLMConfig(
                provider="openai",
                model="gpt-4-turbo-preview",
                api_key=os.getenv('OPENAI_API_KEY'),
                temperature=0.7
            )

            self.llm_configs['openai_gpt35'] = LLMConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                api_key=os.getenv('OPENAI_API_KEY'),
                temperature=0.7
            )

        # Anthropic (if API key available)
        if os.getenv('ANTHROPIC_API_KEY'):
            self.llm_configs['anthropic_claude'] = LLMConfig(
                provider="anthropic",
                model="claude-3-opus-20240229",
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                temperature=0.7
            )

        # LM Studio local server
        self.llm_configs['lmstudio_local'] = LLMConfig(
            provider="openai",  # LM Studio uses OpenAI-compatible API
            model="local-model",
            api_base="http://localhost:1234/v1",
            api_key="not-needed",
            temperature=0.7
        )

        # Text Generation WebUI (oobabooga)
        self.llm_configs['textgen_local'] = LLMConfig(
            provider="text-generation-webui",
            model="local-model",
            api_base="http://localhost:5000",
            temperature=0.7
        )

        # Image generation configs
        # DALL-E 3
        if os.getenv('OPENAI_API_KEY'):
            self.image_configs['dalle3'] = ImageGenConfig(
                provider="openai",
                model="dall-e-3",
                api_key=os.getenv('OPENAI_API_KEY'),
                size="1024x1024",
                quality="hd"
            )

        # Local Stable Diffusion via Ollama
        self.image_configs['ollama_sd'] = ImageGenConfig(
            provider="ollama",
            model="stable-diffusion",
            api_base="http://localhost:11434",
            size="1024x1024"
        )

        # Replicate (if API key available)
        if os.getenv('REPLICATE_API_KEY'):
            self.image_configs['replicate_sdxl'] = ImageGenConfig(
                provider="replicate",
                model="stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                api_key=os.getenv('REPLICATE_API_KEY'),
                size="1024x1024"
            )

        # Set defaults
        self.default_llm = 'ollama_llama3'  # Use local Ollama by default
        self.default_image_gen = 'ollama_sd'  # Use local SD by default

    def complete(
        self,
        messages: List[Dict[str, str]],
        config_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text completion.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            config_name: Name of LLM config to use (or use default)
            **kwargs: Override config parameters

        Returns:
            Response dict with 'content', 'model', 'usage', etc.
        """
        # Select config
        config_name = config_name or self.default_llm
        if config_name not in self.llm_configs:
            raise ValueError(f"LLM config '{config_name}' not found")

        config = self.llm_configs[config_name]

        # Prepare kwargs
        call_kwargs = {
            'model': config.model,
            'messages': messages,
            'temperature': kwargs.get('temperature', config.temperature),
            'max_tokens': kwargs.get('max_tokens', config.max_tokens),
            'timeout': kwargs.get('timeout', config.timeout),
        }

        # Add provider-specific params
        if config.api_base:
            call_kwargs['api_base'] = config.api_base
        if config.api_key:
            call_kwargs['api_key'] = config.api_key
        if config.custom_llm_provider:
            call_kwargs['custom_llm_provider'] = config.custom_llm_provider

        # Add extra params from config
        call_kwargs.update(config.extra_params)

        # Add any additional kwargs
        call_kwargs.update(kwargs)

        try:
            self.logger.info(f"Calling LLM: {config_name} ({config.model})")
            response = litellm.completion(**call_kwargs)

            # Extract response
            result = {
                'content': response.choices[0].message.content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'finish_reason': response.choices[0].finish_reason,
                'raw_response': response
            }

            self.logger.info(f"Completion success. Tokens: {result['usage']['total_tokens']}")
            return result

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    async def acomplete(
        self,
        messages: List[Dict[str, str]],
        config_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Async version of complete()"""
        config_name = config_name or self.default_llm
        if config_name not in self.llm_configs:
            raise ValueError(f"LLM config '{config_name}' not found")

        config = self.llm_configs[config_name]

        call_kwargs = {
            'model': config.model,
            'messages': messages,
            'temperature': kwargs.get('temperature', config.temperature),
            'max_tokens': kwargs.get('max_tokens', config.max_tokens),
        }

        if config.api_base:
            call_kwargs['api_base'] = config.api_base
        if config.api_key:
            call_kwargs['api_key'] = config.api_key

        call_kwargs.update(config.extra_params)
        call_kwargs.update(kwargs)

        response = await litellm.acompletion(**call_kwargs)

        return {
            'content': response.choices[0].message.content,
            'model': response.model,
            'usage': response.usage.__dict__,
            'finish_reason': response.choices[0].finish_reason,
            'raw_response': response
        }

    def generate_image(
        self,
        prompt: str,
        config_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image from text prompt.

        Args:
            prompt: Text description of image
            config_name: Name of image gen config (or use default)
            **kwargs: Override config parameters

        Returns:
            Response dict with 'url', 'b64_json', etc.
        """
        # Select config
        config_name = config_name or self.default_image_gen
        if config_name not in self.image_configs:
            raise ValueError(f"Image config '{config_name}' not found")

        config = self.image_configs[config_name]

        # Prepare kwargs
        call_kwargs = {
            'prompt': prompt,
            'model': config.model,
            'n': kwargs.get('n', config.n),
        }

        # Size handling
        if 'size' in kwargs:
            call_kwargs['size'] = kwargs['size']
        elif config.size:
            call_kwargs['size'] = config.size

        # Quality (for DALL-E)
        if config.provider == 'openai':
            call_kwargs['quality'] = kwargs.get('quality', config.quality)

        # API credentials
        if config.api_base:
            call_kwargs['api_base'] = config.api_base
        if config.api_key:
            call_kwargs['api_key'] = config.api_key

        # Extra params
        call_kwargs.update(config.extra_params)
        call_kwargs.update(kwargs)

        try:
            self.logger.info(f"Generating image: {config_name} ({config.model})")
            response = litellm.image_generation(**call_kwargs)

            result = {
                'images': [],
                'model': config.model,
                'provider': config.provider,
                'raw_response': response
            }

            # Extract image data
            if hasattr(response, 'data'):
                for img_data in response.data:
                    img_info = {}
                    if hasattr(img_data, 'url'):
                        img_info['url'] = img_data.url
                    if hasattr(img_data, 'b64_json'):
                        img_info['b64_json'] = img_data.b64_json
                    result['images'].append(img_info)

            self.logger.info(f"Image generation success. Images: {len(result['images'])}")
            return result

        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise

    def add_llm_config(self, name: str, config: LLMConfig):
        """Add or update LLM configuration"""
        self.llm_configs[name] = config
        self._save_config()

    def add_image_config(self, name: str, config: ImageGenConfig):
        """Add or update image generation configuration"""
        self.image_configs[name] = config
        self._save_config()

    def _save_config(self):
        """Save current configuration to file"""
        config = {
            'llm_configs': {
                name: {
                    'provider': cfg.provider,
                    'model': cfg.model,
                    'api_base': cfg.api_base,
                    'api_key': cfg.api_key,
                    'temperature': cfg.temperature,
                    'max_tokens': cfg.max_tokens,
                    'timeout': cfg.timeout,
                    'custom_llm_provider': cfg.custom_llm_provider,
                    'extra_params': cfg.extra_params
                }
                for name, cfg in self.llm_configs.items()
            },
            'image_configs': {
                name: {
                    'provider': cfg.provider,
                    'model': cfg.model,
                    'api_base': cfg.api_base,
                    'api_key': cfg.api_key,
                    'size': cfg.size,
                    'quality': cfg.quality,
                    'n': cfg.n,
                    'extra_params': cfg.extra_params
                }
                for name, cfg in self.image_configs.items()
            },
            'default_llm': self.default_llm,
            'default_image_gen': self.default_image_gen
        }

        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Saved config to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def list_available_models(self) -> Dict[str, List[str]]:
        """List all available models"""
        return {
            'llm_models': list(self.llm_configs.keys()),
            'image_models': list(self.image_configs.keys())
        }

    def set_defaults(self, llm: Optional[str] = None, image_gen: Optional[str] = None):
        """Set default models"""
        if llm and llm in self.llm_configs:
            self.default_llm = llm
        if image_gen and image_gen in self.image_configs:
            self.default_image_gen = image_gen
        self._save_config()


# Global instance
_litellm_manager: Optional[LiteLLMManager] = None


def get_litellm_manager(config_path: Optional[str] = None) -> LiteLLMManager:
    """Get or create global LiteLLM manager instance"""
    global _litellm_manager
    if _litellm_manager is None:
        _litellm_manager = LiteLLMManager(config_path)
    return _litellm_manager


# Convenience functions
def complete(messages: List[Dict[str, str]], config_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Quick access to completion"""
    manager = get_litellm_manager()
    return manager.complete(messages, config_name, **kwargs)


def generate_image(prompt: str, config_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Quick access to image generation"""
    manager = get_litellm_manager()
    return manager.generate_image(prompt, config_name, **kwargs)
