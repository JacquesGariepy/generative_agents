"""
Creative Capabilities for SOTA Agents

Allows SOTA agents to:
- Generate images using LiteLLM (local or cloud models)
- Use the Creative Studio for design tasks
- Perform autonomous creative work
- Collaborate on creative projects

Integrates:
- LiteLLM for flexible LLM/image generation
- Creative Studio for canvas awareness and optimization
- SOTA modules for intelligent decision-making
"""

from typing import Optional, Dict, Any, List
from PIL import Image
import io
import base64
import requests
from dataclasses import dataclass
import logging

# Import LiteLLM integration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from litellm_integration import get_litellm_manager, LiteLLMManager
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

# Import Creative Studio
try:
    from ..creative_studio.canvas_awareness import CanvasAwarenessSystem
    from ..creative_studio.generation_engine import GenerationEngine, GenerationConfig
    CREATIVE_STUDIO_AVAILABLE = True
except ImportError:
    CREATIVE_STUDIO_AVAILABLE = False


@dataclass
class CreativeTask:
    """A creative task for an agent"""
    task_type: str  # "generate_image", "design_ad", "create_logo", etc.
    description: str
    requirements: Dict[str, Any]
    constraints: Dict[str, Any]
    target_audience: Optional[str] = None
    style_preferences: Optional[List[str]] = None


@dataclass
class CreativeResult:
    """Result of a creative task"""
    task_type: str
    image: Optional[Image.Image]
    image_url: Optional[str]
    metadata: Dict[str, Any]
    quality_score: float
    reasoning: str
    iterations: int
    success: bool


class CreativeCapabilities:
    """
    Adds creative capabilities to SOTA agents.

    Features:
    - Image generation using multiple providers (local/cloud)
    - Canvas-aware design
    - Autonomous creative decision-making
    - Quality evaluation and iteration
    - Multi-agent creative collaboration
    """

    def __init__(
        self,
        agent_name: str,
        litellm_manager: Optional[LiteLLMManager] = None,
        use_creative_studio: bool = True
    ):
        """
        Initialize creative capabilities.

        Args:
            agent_name: Name of the agent
            litellm_manager: LiteLLM manager instance (or create default)
            use_creative_studio: Whether to use Creative Studio features
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")

        # Initialize LiteLLM
        if LITELLM_AVAILABLE:
            self.litellm = litellm_manager or get_litellm_manager()
        else:
            self.logger.warning("LiteLLM not available")
            self.litellm = None

        # Initialize Creative Studio
        self.use_creative_studio = use_creative_studio and CREATIVE_STUDIO_AVAILABLE
        if self.use_creative_studio:
            self.canvas_system = CanvasAwarenessSystem()
            self.generation_engine = GenerationEngine()
        else:
            self.canvas_system = None
            self.generation_engine = None

        # Track creative history
        self.creative_history: List[CreativeResult] = []
        self.preferences_learned: Dict[str, Any] = {}

    def generate_image(
        self,
        prompt: str,
        task_context: Optional[CreativeTask] = None,
        model_preference: Optional[str] = None,
        iterations: int = 1
    ) -> CreativeResult:
        """
        Generate image using LiteLLM (supports local and cloud models).

        Args:
            prompt: Text description of image
            task_context: Optional task context for better generation
            model_preference: Preferred model config name
            iterations: Number of generation attempts

        Returns:
            CreativeResult with generated image
        """
        if not LITELLM_AVAILABLE or not self.litellm:
            return CreativeResult(
                task_type="generate_image",
                image=None,
                image_url=None,
                metadata={'error': 'LiteLLM not available'},
                quality_score=0.0,
                reasoning="LiteLLM not installed",
                iterations=0,
                success=False
            )

        self.logger.info(f"Generating image: '{prompt[:50]}...'")

        # Enhance prompt based on task context
        if task_context:
            enhanced_prompt = self._enhance_prompt(prompt, task_context)
        else:
            enhanced_prompt = prompt

        best_result = None
        best_quality = 0.0

        for iteration in range(iterations):
            try:
                # Generate image using LiteLLM
                response = self.litellm.generate_image(
                    prompt=enhanced_prompt,
                    config_name=model_preference
                )

                # Download image if URL provided
                image = None
                image_url = None

                if response['images']:
                    img_data = response['images'][0]

                    if 'url' in img_data:
                        image_url = img_data['url']
                        # Download image
                        img_response = requests.get(image_url)
                        image = Image.open(io.BytesIO(img_response.content))

                    elif 'b64_json' in img_data:
                        # Decode base64
                        img_bytes = base64.b64decode(img_data['b64_json'])
                        image = Image.open(io.BytesIO(img_bytes))

                # Evaluate quality
                if image and self.use_creative_studio:
                    quality_score = self._evaluate_image_quality(image, task_context)
                else:
                    quality_score = 0.8  # Default if can't evaluate

                if quality_score > best_quality:
                    best_quality = quality_score
                    best_result = CreativeResult(
                        task_type="generate_image",
                        image=image,
                        image_url=image_url,
                        metadata={
                            'model': response['model'],
                            'provider': response['provider'],
                            'prompt': enhanced_prompt,
                            'iteration': iteration + 1
                        },
                        quality_score=quality_score,
                        reasoning=f"Generated with {response['model']}, iteration {iteration + 1}",
                        iterations=iteration + 1,
                        success=True
                    )

                self.logger.info(f"Iteration {iteration + 1}: quality={quality_score:.2f}")

            except Exception as e:
                self.logger.error(f"Generation iteration {iteration + 1} failed: {e}")
                continue

        if best_result:
            self.creative_history.append(best_result)
            return best_result
        else:
            return CreativeResult(
                task_type="generate_image",
                image=None,
                image_url=None,
                metadata={'error': 'All iterations failed'},
                quality_score=0.0,
                reasoning="Failed to generate image",
                iterations=iterations,
                success=False
            )

    def design_autonomously(
        self,
        task: CreativeTask,
        use_reasoning: bool = True
    ) -> CreativeResult:
        """
        Autonomously design based on task description.

        Uses:
        - LiteLLM for reasoning about design approach
        - Image generation for creating visuals
        - Creative Studio for optimization
        - SOTA metacognition for self-evaluation

        Args:
            task: Creative task to complete
            use_reasoning: Whether to use LLM reasoning

        Returns:
            CreativeResult with designed output
        """
        self.logger.info(f"Autonomous design task: {task.task_type}")

        # Step 1: Reason about approach (if LLM available)
        design_plan = None
        if use_reasoning and self.litellm:
            design_plan = self._reason_about_design(task)

        # Step 2: Generate image based on plan
        prompt = self._create_generation_prompt(task, design_plan)

        # Determine number of iterations based on task importance
        iterations = task.requirements.get('quality_iterations', 3)

        result = self.generate_image(
            prompt=prompt,
            task_context=task,
            iterations=iterations
        )

        # Step 3: Optimize with Creative Studio (if available)
        if result.success and result.image and self.use_creative_studio:
            result = self._optimize_with_creative_studio(result, task)

        # Step 4: Self-evaluate
        if result.success and use_reasoning:
            evaluation = self._self_evaluate_result(result, task)
            result.metadata['self_evaluation'] = evaluation

        return result

    def _enhance_prompt(self, prompt: str, task: CreativeTask) -> str:
        """Enhance prompt based on task context"""
        enhanced = prompt

        # Add style preferences
        if task.style_preferences:
            style_str = ", ".join(task.style_preferences)
            enhanced += f", style: {style_str}"

        # Add quality keywords
        if task.requirements.get('quality', 'standard') == 'high':
            enhanced += ", high quality, professional, detailed"

        # Add target audience context
        if task.target_audience:
            enhanced += f", designed for {task.target_audience}"

        return enhanced

    def _reason_about_design(self, task: CreativeTask) -> Dict[str, Any]:
        """Use LLM to reason about design approach"""
        if not self.litellm:
            return {}

        messages = [
            {
                "role": "system",
                "content": f"You are {self.agent_name}, an expert designer. Analyze the design task and provide a strategic approach."
            },
            {
                "role": "user",
                "content": f"""Design Task: {task.task_type}

Description: {task.description}

Requirements: {task.requirements}

Constraints: {task.constraints}

Please provide:
1. Design strategy
2. Key visual elements to include
3. Composition approach
4. Color scheme suggestions
5. Typography recommendations (if text involved)

Be concise and actionable."""
            }
        ]

        try:
            response = self.litellm.complete(messages, max_tokens=500)

            return {
                'reasoning': response['content'],
                'model_used': response['model'],
                'tokens': response['usage']['total_tokens']
            }
        except Exception as e:
            self.logger.error(f"LLM reasoning failed: {e}")
            return {}

    def _create_generation_prompt(
        self,
        task: CreativeTask,
        design_plan: Optional[Dict[str, Any]]
    ) -> str:
        """Create optimized prompt for image generation"""
        prompt_parts = [task.description]

        # Add insights from design plan
        if design_plan and 'reasoning' in design_plan:
            # Extract key visual elements from reasoning
            # (Simple extraction - could be more sophisticated)
            reasoning = design_plan['reasoning']
            if 'color' in reasoning.lower():
                prompt_parts.append("professional color scheme")
            if 'modern' in reasoning.lower():
                prompt_parts.append("modern design")

        # Add requirements
        for key, value in task.requirements.items():
            if key in ['style', 'mood', 'theme']:
                prompt_parts.append(str(value))

        return ", ".join(prompt_parts)

    def _evaluate_image_quality(
        self,
        image: Image.Image,
        task: Optional[CreativeTask]
    ) -> float:
        """Evaluate generated image quality using Creative Studio"""
        if not self.use_creative_studio or not self.canvas_system:
            return 0.7  # Default score

        try:
            # Analyze with canvas system
            state = self.canvas_system.analyze_canvas(image=image)

            quality_score = state.quality_score

            # Adjust based on task requirements
            if task:
                # Check if meets size requirements
                if 'width' in task.requirements and 'height' in task.requirements:
                    target_w = task.requirements['width']
                    target_h = task.requirements['height']

                    if image.size == (target_w, target_h):
                        quality_score += 0.1  # Bonus for exact size

            return min(1.0, quality_score)

        except Exception as e:
            self.logger.error(f"Quality evaluation failed: {e}")
            return 0.5

    def _optimize_with_creative_studio(
        self,
        result: CreativeResult,
        task: CreativeTask
    ) -> CreativeResult:
        """Optimize result using Creative Studio"""
        if not result.image or not self.canvas_system:
            return result

        try:
            # Fix any boundary issues
            target_size = None
            if 'width' in task.requirements and 'height' in task.requirements:
                target_size = (task.requirements['width'], task.requirements['height'])

            fix_result = self.canvas_system.fix_all_issues(
                result.image,
                target_size=target_size
            )

            # Update result
            result.image = fix_result.fixed_image
            result.quality_score = fix_result.quality_score
            result.metadata['optimized'] = True
            result.metadata['optimization_operations'] = fix_result.operations_applied

            self.logger.info(f"Optimized image: quality={fix_result.quality_score:.2f}")

        except Exception as e:
            self.logger.error(f"Optimization failed: {e}")

        return result

    def _self_evaluate_result(
        self,
        result: CreativeResult,
        task: CreativeTask
    ) -> Dict[str, Any]:
        """Self-evaluate the creative result using LLM"""
        if not self.litellm:
            return {}

        messages = [
            {
                "role": "system",
                "content": f"You are {self.agent_name}, evaluating your own creative work."
            },
            {
                "role": "user",
                "content": f"""Task: {task.description}

Result Quality Score: {result.quality_score:.2f}

Metadata: {result.metadata}

Provide a brief self-evaluation:
1. What worked well?
2. What could be improved?
3. Does it meet the task requirements?
4. Confidence level (0-1)?"""
            }
        ]

        try:
            response = self.litellm.complete(messages, max_tokens=300)

            return {
                'evaluation': response['content'],
                'model_used': response['model']
            }
        except Exception as e:
            self.logger.error(f"Self-evaluation failed: {e}")
            return {}

    def get_creative_stats(self) -> Dict[str, Any]:
        """Get statistics about creative work"""
        if not self.creative_history:
            return {
                'total_tasks': 0,
                'success_rate': 0.0,
                'average_quality': 0.0,
                'total_iterations': 0
            }

        successful = [r for r in self.creative_history if r.success]

        return {
            'total_tasks': len(self.creative_history),
            'successful_tasks': len(successful),
            'success_rate': len(successful) / len(self.creative_history),
            'average_quality': sum(r.quality_score for r in successful) / len(successful) if successful else 0.0,
            'total_iterations': sum(r.iterations for r in self.creative_history),
            'average_iterations': sum(r.iterations for r in self.creative_history) / len(self.creative_history)
        }


# Integration with SOTA Persona
def add_creative_capabilities_to_persona(persona, litellm_manager=None):
    """
    Add creative capabilities to an existing SOTA persona.

    Usage:
        persona = SOTAPersona("Designer")
        add_creative_capabilities_to_persona(persona)

        # Now persona can generate images
        result = persona.creative.generate_image("modern logo design")
    """
    persona.creative = CreativeCapabilities(
        agent_name=persona.name,
        litellm_manager=litellm_manager,
        use_creative_studio=True
    )

    return persona
