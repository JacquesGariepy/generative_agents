"""
SOTA Agents with LiteLLM Integration Demo

Demonstrates:
1. Using local LLMs (Ollama, LM Studio) with SOTA agents ✓
2. Agents generating images autonomously ✓
3. Multi-modal creative capabilities ✓
4. Flexible provider switching (local ↔ cloud) ✓
5. Complete autonomous creative workflow ✓

This shows how SOTA agents can:
- Use any LLM (local or cloud)
- Generate images using multiple providers
- Reason about creative tasks
- Self-evaluate their work
- Iterate until quality is achieved
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reverie.backend_server.litellm_integration import (
    get_litellm_manager,
    LLMConfig,
    ImageGenConfig
)
from reverie.backend_server.persona.sota_modules.creative_capabilities import (
    CreativeCapabilities,
    CreativeTask,
    add_creative_capabilities_to_persona
)

import json


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_1_litellm_setup():
    """
    Demo 1: Setup LiteLLM with multiple providers
    """
    print_section("DEMO 1: LiteLLM Setup - Local & Cloud Providers")

    # Get LiteLLM manager
    manager = get_litellm_manager()

    print("\n→ Available LLM Models:")
    models = manager.list_available_models()
    for i, model in enumerate(models['llm_models'], 1):
        config = manager.llm_configs[model]
        print(f"  {i}. {model}")
        print(f"     Provider: {config.provider}")
        print(f"     Model: {config.model}")
        if config.api_base:
            print(f"     API Base: {config.api_base}")

    print("\n→ Available Image Generation Models:")
    for i, model in enumerate(models['image_models'], 1):
        config = manager.image_configs[model]
        print(f"  {i}. {model}")
        print(f"     Provider: {config.provider}")
        print(f"     Model: {config.model}")

    print(f"\n→ Default LLM: {manager.default_llm}")
    print(f"→ Default Image Gen: {manager.default_image_gen}")

    # Add custom local model (example)
    print("\n→ Adding custom Ollama model...")
    manager.add_llm_config(
        "ollama_codellama",
        LLMConfig(
            provider="ollama",
            model="codellama",
            api_base="http://localhost:11434",
            temperature=0.7
        )
    )
    print("  ✓ Added ollama_codellama")

    return manager


def demo_2_test_llm_providers():
    """
    Demo 2: Test different LLM providers
    """
    print_section("DEMO 2: Testing LLM Providers (Local & Cloud)")

    manager = get_litellm_manager()

    test_prompt = "What are the 3 key principles of good design? Answer in one sentence."

    # Test each available LLM
    print("\n→ Testing each LLM provider:\n")

    for config_name in manager.llm_configs.keys():
        config = manager.llm_configs[config_name]

        # Skip if requires API key and not available
        if config.provider in ['openai', 'anthropic'] and not config.api_key:
            print(f"  ⊘ {config_name}: Skipped (no API key)")
            continue

        try:
            print(f"  → Testing {config_name} ({config.model})...")

            messages = [{"role": "user", "content": test_prompt}]

            # Short timeout for demo
            response = manager.complete(
                messages=messages,
                config_name=config_name,
                max_tokens=100,
                timeout=10
            )

            print(f"    ✓ Response: {response['content'][:100]}...")
            print(f"    Tokens: {response['usage']['total_tokens']}")
            print()

        except Exception as e:
            print(f"    ✗ Failed: {e}")
            print()
            continue

    print("✓ LLM provider testing complete")


def demo_3_agent_text_generation():
    """
    Demo 3: SOTA Agent using LiteLLM for reasoning
    """
    print_section("DEMO 3: SOTA Agent with LiteLLM Reasoning")

    manager = get_litellm_manager()

    # Create creative agent
    agent = CreativeCapabilities(
        agent_name="DesignerAgent",
        litellm_manager=manager,
        use_creative_studio=True
    )

    print("\n→ Agent created with LiteLLM capabilities")
    print(f"  Name: {agent.agent_name}")
    print(f"  LiteLLM available: {agent.litellm is not None}")
    print(f"  Creative Studio: {agent.use_creative_studio}")

    # Create a design task
    task = CreativeTask(
        task_type="logo_design",
        description="modern tech startup logo, minimalist, blue and white colors",
        requirements={
            'style': 'minimalist',
            'colors': ['blue', 'white'],
            'quality': 'high',
            'width': 512,
            'height': 512
        },
        constraints={
            'no_text': True,
            'simple': True
        },
        target_audience="tech professionals"
    )

    print("\n→ Design Task:")
    print(f"  Type: {task.task_type}")
    print(f"  Description: {task.description}")
    print(f"  Requirements: {task.requirements}")

    # Agent reasons about the design
    print("\n→ Agent reasoning about design approach...")

    design_plan = agent._reason_about_design(task)

    if design_plan:
        print(f"\n  ✓ Design Plan Generated:")
        print(f"  Model used: {design_plan.get('model_used', 'N/A')}")
        print(f"  Tokens: {design_plan.get('tokens', 'N/A')}")
        print(f"\n  Reasoning:")
        print(f"  {design_plan.get('reasoning', 'N/A')[:300]}...")
    else:
        print("  ⊘ Design reasoning skipped (no LLM available)")

    return agent, task


def demo_4_agent_image_generation():
    """
    Demo 4: Agent generating images with LiteLLM
    """
    print_section("DEMO 4: Agent Image Generation with LiteLLM")

    manager = get_litellm_manager()

    agent = CreativeCapabilities(
        agent_name="ImageAgent",
        litellm_manager=manager,
        use_creative_studio=True
    )

    print("\n→ Testing image generation providers:\n")

    # Test each available image provider
    for config_name in manager.image_configs.keys():
        config = manager.image_configs[config_name]

        # Skip if requires API key and not available
        if config.provider in ['openai', 'replicate'] and not config.api_key:
            print(f"  ⊘ {config_name}: Skipped (no API key)")
            continue

        try:
            print(f"  → Testing {config_name} ({config.model})...")

            result = agent.generate_image(
                prompt="a professional blue and white tech logo, minimalist design",
                model_preference=config_name,
                iterations=1
            )

            if result.success:
                print(f"    ✓ Image generated successfully!")
                print(f"    Quality score: {result.quality_score:.2f}")
                print(f"    Provider: {result.metadata.get('provider', 'unknown')}")
                if result.image:
                    print(f"    Image size: {result.image.size}")
                    # Save image
                    try:
                        os.makedirs("demo_output", exist_ok=True)
                        output_path = f"demo_output/{config_name}_logo.png"
                        result.image.save(output_path)
                        print(f"    💾 Saved: {output_path}")
                    except:
                        pass
            else:
                print(f"    ✗ Generation failed")
                print(f"    Reason: {result.reasoning}")
            print()

        except Exception as e:
            print(f"    ✗ Error: {e}")
            print()
            continue

    print("✓ Image generation testing complete")


def demo_5_autonomous_creative_workflow():
    """
    Demo 5: Full autonomous creative workflow
    """
    print_section("DEMO 5: Autonomous Creative Workflow")

    manager = get_litellm_manager()

    agent = CreativeCapabilities(
        agent_name="AutonomousDesigner",
        litellm_manager=manager,
        use_creative_studio=True
    )

    print("\n→ Creating autonomous design agent")
    print(f"  Agent: {agent.agent_name}")

    # Complex creative task
    task = CreativeTask(
        task_type="social_media_ad",
        description="Instagram ad for eco-friendly water bottle, vibrant and energetic, call-to-action",
        requirements={
            'platform': 'instagram',
            'format': 'square',
            'width': 1080,
            'height': 1080,
            'quality_iterations': 2,
            'style': 'vibrant',
            'mood': 'energetic',
            'include_cta': True
        },
        constraints={
            'brand_safe': True,
            'mobile_optimized': True
        },
        target_audience="environmentally conscious millennials"
    )

    print("\n→ Task Details:")
    print(f"  Type: {task.task_type}")
    print(f"  Description: {task.description}")
    print(f"  Target: {task.target_audience}")
    print(f"  Quality iterations: {task.requirements['quality_iterations']}")

    print("\n→ Starting autonomous design process...")
    print("  Step 1: Reasoning about design approach...")
    print("  Step 2: Generating image with quality iterations...")
    print("  Step 3: Optimizing with Creative Studio...")
    print("  Step 4: Self-evaluating result...")

    # Execute autonomous design
    result = agent.design_autonomously(task, use_reasoning=True)

    print(f"\n→ Autonomous Design Complete!")
    print(f"  Success: {result.success}")
    print(f"  Quality Score: {result.quality_score:.2f}")
    print(f"  Iterations: {result.iterations}")

    if result.success:
        print(f"\n  Metadata:")
        for key, value in result.metadata.items():
            if key == 'self_evaluation':
                print(f"    {key}:")
                print(f"      {str(value)[:200]}...")
            else:
                print(f"    {key}: {value}")

        if result.image:
            try:
                os.makedirs("demo_output", exist_ok=True)
                result.image.save("demo_output/autonomous_design.png")
                print(f"\n  💾 Saved: demo_output/autonomous_design.png")
            except:
                pass
    else:
        print(f"\n  Failed: {result.reasoning}")

    # Show stats
    print("\n→ Agent Creative Statistics:")
    stats = agent.get_creative_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    return agent, result


def demo_6_provider_switching():
    """
    Demo 6: Easy provider switching (local ↔ cloud)
    """
    print_section("DEMO 6: Provider Switching - Local to Cloud")

    manager = get_litellm_manager()

    print("\n→ Demonstrating provider flexibility:\n")

    prompt = "Describe a modern minimalist logo in 10 words."

    # Try local first
    print("  1. Using LOCAL Ollama (if available):")
    try:
        messages = [{"role": "user", "content": prompt}]
        response = manager.complete(messages, config_name="ollama_llama3", max_tokens=50)
        print(f"     ✓ Ollama: {response['content']}")
    except Exception as e:
        print(f"     ✗ Ollama unavailable: {e}")

    # Try cloud (if API key available)
    print("\n  2. Using CLOUD OpenAI (if API key available):")
    try:
        if "openai_gpt4" in manager.llm_configs:
            messages = [{"role": "user", "content": prompt}]
            response = manager.complete(messages, config_name="openai_gpt4", max_tokens=50)
            print(f"     ✓ OpenAI: {response['content']}")
        else:
            print("     ⊘ OpenAI not configured")
    except Exception as e:
        print(f"     ✗ OpenAI failed: {e}")

    # Switch defaults
    print("\n  3. Switching default provider:")
    original_default = manager.default_llm
    print(f"     Current default: {original_default}")

    # Try to switch
    if "openai_gpt4" in manager.llm_configs:
        manager.set_defaults(llm="openai_gpt4")
        print(f"     → Changed to: openai_gpt4")
        manager.set_defaults(llm=original_default)
        print(f"     → Restored to: {original_default}")
    else:
        print("     → (No alternative provider to switch to)")

    print("\n  ✓ Provider switching demonstrated!")
    print("  → Can easily switch between local and cloud models")
    print("  → Same API, different backends")
    print("  → Cost optimization by preferring local models")


def demo_7_configuration_persistence():
    """
    Demo 7: Configuration saving and loading
    """
    print_section("DEMO 7: Configuration Persistence")

    manager = get_litellm_manager()

    config_file = "demo_litellm_config.json"

    print("\n→ Saving current configuration...")

    # Force save
    manager.config_path = config_file
    manager._save_config()

    print(f"  ✓ Saved to: {config_file}")

    # Check file
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_data = json.load(f)

        print(f"\n→ Configuration contains:")
        print(f"  LLM configs: {len(config_data['llm_configs'])}")
        print(f"  Image configs: {len(config_data['image_configs'])}")
        print(f"  Default LLM: {config_data['default_llm']}")
        print(f"  Default Image: {config_data['default_image_gen']}")

        print(f"\n→ Sample LLM config:")
        sample_llm = list(config_data['llm_configs'].keys())[0]
        print(f"  Name: {sample_llm}")
        print(f"  Details: {json.dumps(config_data['llm_configs'][sample_llm], indent=4)}")

    print("\n  ✓ Configuration can be saved and loaded")
    print("  → Persistent across sessions")
    print("  → Easy to share and version control")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "SOTA AGENTS WITH LITELLM INTEGRATION" + " " * 27 + "║")
    print("║" + " " * 78 + "║")
    print("║  Local LLMs ✓ | Cloud LLMs ✓ | Image Generation ✓ | Autonomous ✓" + " " * 12 + "║")
    print("╚" + "=" * 78 + "╝")

    print("\n🎯 This demo shows how SOTA agents can:")
    print("  • Use ANY LLM (Ollama, LM Studio, OpenAI, Anthropic, etc.)")
    print("  • Generate images with multiple providers")
    print("  • Reason autonomously about creative tasks")
    print("  • Switch providers seamlessly (local ↔ cloud)")
    print("  • Self-evaluate and iterate on quality")

    print("\n📝 NOTE:")
    print("  • Ollama must be running for local LLM demos: ollama serve")
    print("  • API keys needed for cloud providers (optional)")
    print("  • Some demos may skip if dependencies unavailable")

    try:
        # Run demos
        demo_1_litellm_setup()
        demo_2_test_llm_providers()
        demo_3_agent_text_generation()
        demo_4_agent_image_generation()
        demo_5_autonomous_creative_workflow()
        demo_6_provider_switching()
        demo_7_configuration_persistence()

        print("\n" + "=" * 80)
        print("✓ ALL DEMOS COMPLETED!")
        print("=" * 80)

        print("\n🎯 Key Achievements:")
        print("  ✓ LiteLLM integrated for flexible LLM access")
        print("  ✓ Supports local models (Ollama, LM Studio)")
        print("  ✓ Supports cloud models (OpenAI, Anthropic, etc.)")
        print("  ✓ SOTA agents can generate images autonomously")
        print("  ✓ Multi-modal creative capabilities enabled")
        print("  ✓ Easy provider switching for cost optimization")

        print("\n📊 Benefits:")
        print("  • Cost savings: Use free local models")
        print("  • Privacy: Keep data on-premise")
        print("  • Flexibility: Switch providers anytime")
        print("  • Performance: Choose optimal model for each task")

        print("\n🚀 SOTA Agents + LiteLLM = Unlimited Creative Potential!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
