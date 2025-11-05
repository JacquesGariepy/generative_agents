"""
LiteLLM Wrapper for GPT Functions

This module wraps all GPT calls to use LiteLLM instead of direct OpenAI calls.
This enables:
- Local LLM usage (Ollama, LM Studio, etc.)
- Any cloud provider (OpenAI, Anthropic, Google, Azure, etc.)
- Flexible model switching
- Cost optimization

Usage:
    Instead of calling OpenAI directly, all calls go through LiteLLM.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from litellm_integration import get_litellm_manager

import time
import logging

logger = logging.getLogger(__name__)


def safe_generate_response_litellm(
    prompt: str,
    gpt_param: dict,
    repeat: int = 3,
    fail_safe: str = "",
    func_validate=None,
    func_clean_up=None,
    config_name: str = None
):
    """
    Generate response using LiteLLM (supports any LLM provider).

    This replaces the original safe_generate_response function.

    Args:
        prompt: The prompt text
        gpt_param: Original GPT parameters (will be adapted)
        repeat: Number of retry attempts
        fail_safe: Fallback response if all attempts fail
        func_validate: Function to validate response
        func_clean_up: Function to clean up response
        config_name: LiteLLM config name (e.g., 'ollama_llama3', 'openai_gpt4')

    Returns:
        Cleaned and validated response, or fail_safe if all attempts fail
    """
    # Get LiteLLM manager
    litellm_manager = get_litellm_manager()

    # Convert GPT parameters to LiteLLM format
    messages = [{"role": "user", "content": prompt}]

    # Extract relevant parameters
    temperature = gpt_param.get('temperature', 0.7)
    max_tokens = gpt_param.get('max_tokens', 2000)

    # Try to generate response
    for attempt in range(repeat):
        try:
            logger.info(f"LiteLLM generation attempt {attempt + 1}/{repeat}")

            # Call LiteLLM
            response = litellm_manager.complete(
                messages=messages,
                config_name=config_name,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract content
            content = response['content']

            # Validate if function provided
            if func_validate:
                if not func_validate(content, prompt):
                    logger.warning(f"Validation failed for attempt {attempt + 1}")
                    continue

            # Clean up if function provided
            if func_clean_up:
                content = func_clean_up(content, prompt)

            logger.info(f"Successfully generated response on attempt {attempt + 1}")
            return content

        except Exception as e:
            logger.error(f"LiteLLM generation attempt {attempt + 1} failed: {e}")
            if attempt < repeat - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue

    # All attempts failed, return fail_safe
    logger.warning(f"All {repeat} attempts failed, returning fail_safe")
    return fail_safe


def ChatGPT_single_request_litellm(prompt, config_name=None, temperature=0.7, max_tokens=2000):
    """
    Simple single request to LiteLLM.

    Args:
        prompt: The prompt text
        config_name: LiteLLM config name
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Response text
    """
    litellm_manager = get_litellm_manager()

    messages = [{"role": "user", "content": prompt}]

    try:
        response = litellm_manager.complete(
            messages=messages,
            config_name=config_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response['content']
    except Exception as e:
        logger.error(f"LiteLLM request failed: {e}")
        return ""


def ChatGPT_request_litellm(
    prompt,
    config_name=None,
    temperature=0.7,
    max_tokens=2000,
    system_message=None
):
    """
    Chat-style request to LiteLLM with optional system message.

    Args:
        prompt: User prompt
        config_name: LiteLLM config name
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        system_message: Optional system message

    Returns:
        Response text
    """
    litellm_manager = get_litellm_manager()

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    try:
        response = litellm_manager.complete(
            messages=messages,
            config_name=config_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response['content']
    except Exception as e:
        logger.error(f"LiteLLM chat request failed: {e}")
        return ""


def generate_with_context_litellm(
    system_prompt: str,
    user_prompt: str,
    config_name: str = None,
    conversation_history: list = None,
    **kwargs
):
    """
    Generate with full conversation context.

    Args:
        system_prompt: System instructions
        user_prompt: User message
        config_name: LiteLLM config
        conversation_history: Previous messages
        **kwargs: Additional parameters

    Returns:
        Response text
    """
    litellm_manager = get_litellm_manager()

    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": user_prompt})

    try:
        response = litellm_manager.complete(
            messages=messages,
            config_name=config_name,
            **kwargs
        )
        return response['content']
    except Exception as e:
        logger.error(f"Context generation failed: {e}")
        return ""


# Patch function to replace original safe_generate_response
def patch_gpt_functions_to_litellm(module, config_name=None):
    """
    Monkey-patch a module to use LiteLLM instead of OpenAI.

    Usage:
        import persona.prompt_template.run_gpt_prompt as gpt_module
        patch_gpt_functions_to_litellm(gpt_module, config_name='ollama_llama3')

    Args:
        module: The module to patch
        config_name: Default LiteLLM config to use
    """
    original_safe_generate = getattr(module, 'safe_generate_response', None)

    if original_safe_generate:
        def patched_safe_generate(prompt, gpt_param, repeat=3, fail_safe="",
                                 func_validate=None, func_clean_up=None):
            return safe_generate_response_litellm(
                prompt, gpt_param, repeat, fail_safe,
                func_validate, func_clean_up, config_name
            )

        module.safe_generate_response = patched_safe_generate
        logger.info(f"Patched {module.__name__} to use LiteLLM with config: {config_name}")


def get_available_models():
    """Get list of available models"""
    litellm_manager = get_litellm_manager()
    return litellm_manager.list_available_models()


def set_default_model(llm_config=None, image_config=None):
    """Set default models"""
    litellm_manager = get_litellm_manager()
    litellm_manager.set_defaults(llm=llm_config, image_gen=image_config)


# Example usage and configuration
if __name__ == "__main__":
    # Example: Use local Ollama
    response = ChatGPT_single_request_litellm(
        "What is 2+2?",
        config_name="ollama_llama3"
    )
    print(f"Response: {response}")

    # Example: List available models
    models = get_available_models()
    print(f"Available models: {models}")
