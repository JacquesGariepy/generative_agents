# LiteLLM Integration - Unified LLM Access for SOTA Agents

> **Version**: 1.0.0
> **Status**: Production Ready
> **Purpose**: Enable SOTA agents to use ANY LLM (local or cloud) and generate images autonomously

---

## 🎯 Mission

**Allow SOTA agents to use local LLMs (Ollama, LM Studio) OR cloud providers (OpenAI, Anthropic, etc.) with a unified API.**

### ✅ What This Enables

| Capability | Before | After LiteLLM |
|------------|--------|---------------|
| LLM Choice | OpenAI only | **ANY LLM** (100+ providers) |
| Local Models | ❌ Not supported | ✅ **Ollama, LM Studio, vLLM, etc.** |
| Cost | Always paid API | ✅ **Free local models** |
| Privacy | Data sent to cloud | ✅ **On-premise option** |
| Image Generation | Limited providers | ✅ **Multiple providers** |
| Agent Autonomy | Cannot generate images | ✅ **Full creative autonomy** |

---

## 📦 What's Implemented

### 1. **LiteLLM Integration Module** ✅ COMPLETE

**File**: `reverie/backend_server/litellm_integration.py` (530+ lines)

**Features**:
- ✅ Unified API for 100+ LLM providers
- ✅ Local LLM support (Ollama, LM Studio, Text Gen WebUI)
- ✅ Cloud LLM support (OpenAI, Anthropic, Google, Azure, Cohere, etc.)
- ✅ Image generation (DALL-E, Stable Diffusion, Replicate, Ollama)
- ✅ Configuration persistence (JSON file)
- ✅ Automatic fallback mechanisms
- ✅ Cost tracking and usage monitoring
- ✅ Async support for high performance

**Supported Providers**:

**LLM Providers**:
- **Local**: Ollama, LM Studio, vLLM, Text Generation WebUI, llamafile
- **Cloud**: OpenAI, Anthropic (Claude), Google (Gemini), Azure, Cohere, Replicate, HuggingFace
- **Self-hosted**: Any OpenAI-compatible API

**Image Generation Providers**:
- **OpenAI**: DALL-E 3
- **Replicate**: SDXL, FLUX, Stable Diffusion
- **Ollama**: Local Stable Diffusion
- **HuggingFace**: Any diffusion model

**Usage**:
```python
from reverie.backend_server.litellm_integration import get_litellm_manager

# Get manager
manager = get_litellm_manager()

# Use local Ollama
response = manager.complete(
    messages=[{"role": "user", "content": "Hello!"}],
    config_name="ollama_llama3"
)

# Generate image locally
image_result = manager.generate_image(
    prompt="modern tech logo",
    config_name="ollama_sd"
)
```

### 2. **Creative Capabilities for SOTA Agents** ✅ COMPLETE

**File**: `reverie/backend_server/persona/sota_modules/creative_capabilities.py` (460+ lines)

**Features**:
- ✅ Agents can generate images using any provider
- ✅ Autonomous creative decision-making
- ✅ Quality evaluation and iteration
- ✅ Self-evaluation using LLM
- ✅ Integration with Creative Studio
- ✅ Task planning and reasoning
- ✅ Creative history tracking

**Agent Capabilities**:

```python
from reverie.backend_server.persona.sota_modules.creative_capabilities import CreativeCapabilities, CreativeTask

# Create creative agent
agent = CreativeCapabilities("DesignerAgent")

# Define task
task = CreativeTask(
    task_type="logo_design",
    description="modern tech startup logo, minimalist",
    requirements={'width': 512, 'height': 512, 'style': 'minimalist'},
    target_audience="tech professionals"
)

# Agent autonomously:
# 1. Reasons about design approach (using LLM)
# 2. Generates image (using image model)
# 3. Evaluates quality (using Creative Studio)
# 4. Iterates if needed
# 5. Self-evaluates result (using LLM)
result = agent.design_autonomously(task)

print(f"Quality: {result.quality_score:.2f}")
print(f"Success: {result.success}")
result.image.save("output.png")
```

### 3. **LiteLLM GPT Wrapper** ✅ COMPLETE

**File**: `reverie/backend_server/persona/prompt_template/litellm_gpt_wrapper.py` (220+ lines)

**Features**:
- ✅ Drop-in replacement for OpenAI calls
- ✅ Backward compatible with existing code
- ✅ Monkey-patching capability
- ✅ Automatic retry with exponential backoff

**Usage**:
```python
from reverie.backend_server.persona.prompt_template.litellm_gpt_wrapper import (
    safe_generate_response_litellm,
    ChatGPT_single_request_litellm,
    patch_gpt_functions_to_litellm
)

# Direct usage
response = ChatGPT_single_request_litellm(
    prompt="What is good design?",
    config_name="ollama_llama3"
)

# Or patch existing modules
import persona.prompt_template.run_gpt_prompt as gpt_module
patch_gpt_functions_to_litellm(gpt_module, config_name='ollama_llama3')
# Now all calls in gpt_module use LiteLLM!
```

### 4. **Comprehensive Demo** ✅ COMPLETE

**File**: `examples/sota_agents_with_litellm_demo.py` (600+ lines)

**7 Complete Demonstrations**:
1. LiteLLM setup with multiple providers
2. Testing different LLM providers (local & cloud)
3. SOTA agent using LiteLLM for reasoning
4. Agent image generation with multiple providers
5. Full autonomous creative workflow
6. Provider switching (local ↔ cloud)
7. Configuration persistence

**Run Demo**:
```bash
# Install dependencies
pip install litellm pillow numpy opencv-python scipy

# Optional: Start Ollama for local LLMs
ollama serve
ollama pull llama3

# Run demo
python examples/sota_agents_with_litellm_demo.py
```

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install LiteLLM (required)
pip install litellm

# 2. Install image processing (for Creative Studio)
pip install pillow numpy opencv-python scipy

# 3. Optional: Local LLM setup
# Option A: Ollama (recommended)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3
ollama pull mistral

# Option B: LM Studio
# Download from https://lmstudio.ai/

# Option C: Text Generation WebUI
# Follow: https://github.com/oobabooga/text-generation-webui
```

### Basic Usage

#### 1. Text Completion with Local LLM

```python
from reverie.backend_server.litellm_integration import get_litellm_manager

manager = get_litellm_manager()

# Use Ollama (local)
response = manager.complete(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain design principles in one sentence."}
    ],
    config_name="ollama_llama3",
    temperature=0.7,
    max_tokens=100
)

print(response['content'])
print(f"Tokens used: {response['usage']['total_tokens']}")
```

#### 2. Image Generation with Local Model

```python
from reverie.backend_server.litellm_integration import generate_image

# Generate with local Ollama Stable Diffusion
result = generate_image(
    prompt="modern minimalist tech logo, blue and white, professional",
    config_name="ollama_sd"
)

# Download and save image
if result['images']:
    url = result['images'][0]['url']
    # ... download and save
```

#### 3. SOTA Agent with Creative Capabilities

```python
from reverie.backend_server.persona.sota_persona import SOTAPersona
from reverie.backend_server.persona.sota_modules.creative_capabilities import (
    add_creative_capabilities_to_persona,
    CreativeTask
)

# Create SOTA agent
agent = SOTAPersona("DesignerAgent")

# Add creative capabilities
add_creative_capabilities_to_persona(agent)

# Now agent can generate images!
task = CreativeTask(
    task_type="social_media_post",
    description="Instagram post for eco product, vibrant, modern",
    requirements={'width': 1080, 'height': 1080}
)

result = agent.creative.design_autonomously(task)

if result.success:
    result.image.save("instagram_post.png")
    print(f"Quality: {result.quality_score:.2f}")
```

---

## ⚙️ Configuration

### Configuration File

LiteLLM uses a JSON configuration file (`litellm_config.json`) to store all provider settings.

**Auto-generated default configuration**:

```json
{
  "llm_configs": {
    "ollama_llama3": {
      "provider": "ollama",
      "model": "llama3",
      "api_base": "http://localhost:11434",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "openai_gpt4": {
      "provider": "openai",
      "model": "gpt-4-turbo-preview",
      "api_key": "sk-...",
      "temperature": 0.7
    }
  },
  "image_configs": {
    "ollama_sd": {
      "provider": "ollama",
      "model": "stable-diffusion",
      "api_base": "http://localhost:11434",
      "size": "1024x1024"
    },
    "dalle3": {
      "provider": "openai",
      "model": "dall-e-3",
      "api_key": "sk-...",
      "quality": "hd"
    }
  },
  "default_llm": "ollama_llama3",
  "default_image_gen": "ollama_sd"
}
```

### Adding Custom Providers

#### Add Custom LLM

```python
from reverie.backend_server.litellm_integration import get_litellm_manager, LLMConfig

manager = get_litellm_manager()

# Add LM Studio
manager.add_llm_config(
    "lmstudio_custom",
    LLMConfig(
        provider="openai",  # LM Studio uses OpenAI-compatible API
        model="local-model",
        api_base="http://localhost:1234/v1",
        api_key="not-needed",
        temperature=0.7
    )
)

# Add Azure OpenAI
manager.add_llm_config(
    "azure_gpt4",
    LLMConfig(
        provider="azure",
        model="gpt-4",
        api_base="https://your-resource.openai.azure.com/",
        api_key="your-azure-key",
        extra_params={
            "api_version": "2023-05-15"
        }
    )
)
```

#### Add Custom Image Provider

```python
from reverie.backend_server.litellm_integration import ImageGenConfig

# Add Replicate SDXL
manager.add_image_config(
    "replicate_sdxl",
    ImageGenConfig(
        provider="replicate",
        model="stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        api_key="r8_...",
        size="1024x1024"
    )
)
```

### Environment Variables

Set API keys via environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export REPLICATE_API_KEY="r8_..."
export GOOGLE_API_KEY="..."
export COHERE_API_KEY="..."
```

---

## 🎓 Advanced Usage

### Multi-Agent Creative Team with LiteLLM

```python
from reverie.backend_server.persona.sota_persona import SOTAPersona
from reverie.backend_server.persona.sota_modules.creative_capabilities import (
    add_creative_capabilities_to_persona
)

# Create specialized creative agents
art_director = SOTAPersona("ArtDirector")
copywriter = SOTAPersona("Copywriter")
designer = SOTAPersona("Designer")

# Add creative capabilities to all
for agent in [art_director, copywriter, designer]:
    add_creative_capabilities_to_persona(agent)

# Art director reasons about campaign
campaign_plan = art_director.creative.litellm.complete(
    messages=[{
        "role": "user",
        "content": "Create a social media campaign plan for eco water bottle"
    }],
    config_name="ollama_llama3"
)

# Copywriter writes copy
copy = copywriter.creative.litellm.complete(
    messages=[{
        "role": "user",
        "content": f"Write engaging copy for: {campaign_plan['content']}"
    }],
    config_name="ollama_mistral"
)

# Designer generates image
from reverie.backend_server.persona.sota_modules.creative_capabilities import CreativeTask

task = CreativeTask(
    task_type="social_media_ad",
    description=copy['content'],
    requirements={'width': 1080, 'height': 1080}
)

result = designer.creative.design_autonomously(task)
```

### Cost Optimization: Local → Cloud Fallback

```python
def smart_completion(prompt, prefer_local=True):
    """Try local first, fallback to cloud if needed"""
    manager = get_litellm_manager()

    configs = ["ollama_llama3", "openai_gpt4"] if prefer_local else ["openai_gpt4", "ollama_llama3"]

    for config_name in configs:
        try:
            response = manager.complete(
                messages=[{"role": "user", "content": prompt}],
                config_name=config_name,
                timeout=10
            )
            print(f"Used: {config_name}")
            return response
        except Exception as e:
            print(f"{config_name} failed: {e}")
            continue

    return None
```

### Async Generation for Performance

```python
import asyncio
from reverie.backend_server.litellm_integration import get_litellm_manager

async def generate_multiple():
    """Generate multiple completions in parallel"""
    manager = get_litellm_manager()

    tasks = [
        manager.acomplete(
            messages=[{"role": "user", "content": f"Design idea #{i}"}],
            config_name="ollama_llama3"
        )
        for i in range(5)
    ]

    results = await asyncio.gather(*tasks)
    return results

# Run
results = asyncio.run(generate_multiple())
```

---

## 📊 Performance & Cost Comparison

### Speed Comparison

| Provider | Model | Speed | Cost |
|----------|-------|-------|------|
| Ollama (local) | Llama 3 8B | ~50 tokens/s | **FREE** |
| LM Studio (local) | Mistral 7B | ~60 tokens/s | **FREE** |
| OpenAI | GPT-4 Turbo | ~40 tokens/s | $0.01/1K tokens |
| Anthropic | Claude Opus | ~30 tokens/s | $0.015/1K tokens |

### Cost Savings Example

**Scenario**: 1 million tokens per month

| Approach | Monthly Cost |
|----------|-------------|
| **OpenAI only** | $10,000 |
| **Local only (Ollama)** | **$0** (electricity only) |
| **Hybrid (80% local, 20% cloud)** | **$2,000** (80% savings) |

---

## 🔧 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull required models
ollama pull llama3
ollama pull mistral
```

### LM Studio Setup

1. Download LM Studio from https://lmstudio.ai/
2. Load a model
3. Start local server (Settings → Local Server → Start)
4. Use `http://localhost:1234/v1` as API base

### API Key Issues

```python
# Check if API keys are loaded
import os
print(f"OpenAI: {os.getenv('OPENAI_API_KEY')[:10]}...")

# Set programmatically
manager = get_litellm_manager()
manager.llm_configs['openai_gpt4'].api_key = "sk-..."
```

### Debugging LiteLLM

```python
import litellm
litellm.set_verbose = True  # Enable debug logging

# Now all LiteLLM calls will show detailed logs
```

---

## 🎯 Use Cases

### 1. **Privacy-First Development**
Use local models for sensitive data, cloud for general tasks.

### 2. **Cost Optimization**
Use free local models for development, paid cloud for production.

### 3. **Autonomous Creative Agents**
Agents generate images and reason about designs independently.

### 4. **Multi-Modal Workflows**
Combine text reasoning (LLM) with image generation seamlessly.

### 5. **Experimentation**
Try different models easily without code changes.

---

## 🚀 Integration with Existing Code

### Patch Existing GPT Functions

```python
# In your main application startup
from reverie.backend_server.persona.prompt_template.litellm_gpt_wrapper import (
    patch_gpt_functions_to_litellm
)
import reverie.backend_server.persona.prompt_template.run_gpt_prompt as gpt_module

# Patch all GPT calls to use Ollama
patch_gpt_functions_to_litellm(gpt_module, config_name='ollama_llama3')

# Now all existing code uses local LLM automatically!
```

---

## 📝 API Reference

### LiteLLMManager

```python
class LiteLLMManager:
    def complete(messages, config_name, **kwargs) -> Dict
    def acomplete(messages, config_name, **kwargs) -> Dict  # Async
    def generate_image(prompt, config_name, **kwargs) -> Dict
    def add_llm_config(name, config: LLMConfig)
    def add_image_config(name, config: ImageGenConfig)
    def list_available_models() -> Dict
    def set_defaults(llm, image_gen)
```

### CreativeCapabilities

```python
class CreativeCapabilities:
    def generate_image(prompt, task_context, model_preference, iterations) -> CreativeResult
    def design_autonomously(task: CreativeTask, use_reasoning) -> CreativeResult
    def get_creative_stats() -> Dict
```

---

## 🎉 Benefits Summary

✅ **Flexibility**: Use ANY LLM provider (100+ supported)
✅ **Cost Savings**: Free local models = $0 cost
✅ **Privacy**: Keep data on-premise
✅ **Performance**: Choose optimal model per task
✅ **Agent Autonomy**: Generate images independently
✅ **Easy Integration**: Drop-in replacement
✅ **Future-Proof**: Add new providers easily

---

## 📚 Resources

- **LiteLLM Docs**: https://docs.litellm.ai/
- **Ollama**: https://ollama.com/
- **LM Studio**: https://lmstudio.ai/
- **Supported Providers**: https://docs.litellm.ai/docs/providers

---

## 🎊 Conclusion

**LiteLLM integration transforms SOTA agents into truly autonomous creative systems that can use ANY LLM (local or cloud) and generate images independently.**

**Key Achievement**: SOTA agents are now 100% provider-agnostic and can work completely offline with local models!

---

*Built for the Generative Agents project - Making AI agents truly autonomous and flexible*
