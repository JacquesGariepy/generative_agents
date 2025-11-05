"""
Multi-Level Reasoning System

Implements a hierarchical reasoning architecture with multiple cognitive levels:

Level 0 (Reactive): Immediate stimulus-response, no deliberation
Level 1 (Deliberative): Planning and goal-oriented behavior with memory
Level 2 (Reflective): Learning from experience, pattern recognition
Level 3 (Meta-Cognitive): Reasoning about reasoning, self-improvement

Each level can invoke lower levels and be monitored by higher levels.
Higher levels are more computationally expensive but more sophisticated.
"""

import datetime
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import sys
sys.path.append('../../')

from global_methods import *
from persona.sota_modules.metacognition import MetaCognitiveSystem, ReasoningQuality


class ReasoningLevel(Enum):
    """Levels of cognitive processing"""
    REACTIVE = 0  # Fast, automatic responses
    DELIBERATIVE = 1  # Planned, goal-oriented
    REFLECTIVE = 2  # Learning-based, experience-driven
    METACOGNITIVE = 3  # Self-aware, self-improving


@dataclass
class ReasoningContext:
    """Context for reasoning process"""
    problem: str
    urgency: float  # 0-1, how urgent is this
    complexity: float  # 0-1, estimated complexity
    available_time: float  # How much time available
    past_experiences: List[Any]  # Related past experiences
    current_goal: str
    constraints: List[str]


@dataclass
class ReasoningResult:
    """Result from a reasoning process"""
    level_used: ReasoningLevel
    solution: str
    confidence: float
    reasoning_trace: List[str]
    time_taken: float
    quality_estimate: ReasoningQuality
    should_escalate: bool  # Should we use higher level?
    metadata: Dict[str, Any]


class ReactiveReasoning:
    """
    Level 0: Reactive Reasoning

    Fast, pattern-matched responses. No deliberation.
    Uses cached solutions and simple heuristics.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.response_cache: Dict[str, str] = {}
        self.pattern_responses: Dict[str, str] = self._init_patterns()

    def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Reactive reasoning: immediate response based on patterns.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult with quick response
        """
        start_time = datetime.datetime.now()

        # Check cache first
        cache_key = self._create_cache_key(context.problem)
        if cache_key in self.response_cache:
            solution = self.response_cache[cache_key]
            reasoning_trace = ["Retrieved cached response"]
            confidence = 0.9  # High confidence in cached responses

            return ReasoningResult(
                level_used=ReasoningLevel.REACTIVE,
                solution=solution,
                confidence=confidence,
                reasoning_trace=reasoning_trace,
                time_taken=(datetime.datetime.now() - start_time).total_seconds(),
                quality_estimate=ReasoningQuality.GOOD,
                should_escalate=False,
                metadata={'source': 'cache'}
            )

        # Pattern matching
        for pattern, response_template in self.pattern_responses.items():
            if pattern in context.problem.lower():
                solution = response_template.format(agent=self.agent_name)
                reasoning_trace = [f"Matched pattern: {pattern}"]
                confidence = 0.7

                # Cache this response
                self.response_cache[cache_key] = solution

                return ReasoningResult(
                    level_used=ReasoningLevel.REACTIVE,
                    solution=solution,
                    confidence=confidence,
                    reasoning_trace=reasoning_trace,
                    time_taken=(datetime.datetime.now() - start_time).total_seconds(),
                    quality_estimate=ReasoningQuality.ADEQUATE,
                    should_escalate=False,
                    metadata={'source': 'pattern_match', 'pattern': pattern}
                )

        # No pattern match - should escalate to deliberative
        return ReasoningResult(
            level_used=ReasoningLevel.REACTIVE,
            solution="",
            confidence=0.0,
            reasoning_trace=["No reactive response available"],
            time_taken=(datetime.datetime.now() - start_time).total_seconds(),
            quality_estimate=ReasoningQuality.FAILED,
            should_escalate=True,
            metadata={'reason': 'no_pattern_match'}
        )

    @staticmethod
    def _init_patterns() -> Dict[str, str]:
        """Initialize common patterns and responses"""
        return {
            'hello': "Hello! How can I help you?",
            'how are you': "I'm doing well, thank you for asking!",
            'good morning': "Good morning! I hope you're having a great day.",
            'goodbye': "Goodbye! Take care.",
            'thank you': "You're welcome!",
            # Action patterns
            'wake up': "waking up and starting morning routine",
            'go to sleep': "going to bed to sleep",
            'eat breakfast': "eating breakfast",
            'eat lunch': "eating lunch",
            'eat dinner': "eating dinner",
        }

    @staticmethod
    def _create_cache_key(problem: str) -> str:
        """Create a cache key from problem"""
        return problem.lower().strip()[:100]  # Truncate for consistency


class DeliberativeReasoning:
    """
    Level 1: Deliberative Reasoning

    Goal-oriented planning with memory retrieval and evaluation of options.
    Uses existing cognitive modules (plan, retrieve, execute).
    """

    def __init__(self, persona):
        self.persona = persona

    def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Deliberative reasoning: plan and evaluate options.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult with planned solution
        """
        start_time = datetime.datetime.now()
        reasoning_trace = []

        # Step 1: Retrieve relevant memories
        reasoning_trace.append("Retrieving relevant memories...")
        # Use persona's existing retrieve mechanism
        # This is a simplified version - in real implementation, integrate with persona.retrieve()

        # Step 2: Generate multiple options
        reasoning_trace.append("Generating options...")
        options = self._generate_options(context)

        # Step 3: Evaluate each option
        reasoning_trace.append(f"Evaluating {len(options)} options...")
        evaluated_options = []
        for option in options:
            score = self._evaluate_option(option, context)
            evaluated_options.append((score, option))

        evaluated_options.sort(reverse=True, key=lambda x: x[0])

        # Step 4: Select best option
        if evaluated_options:
            best_score, best_option = evaluated_options[0]
            solution = best_option
            confidence = best_score
            quality = ReasoningQuality.GOOD if best_score > 0.7 else ReasoningQuality.ADEQUATE
            reasoning_trace.append(f"Selected best option with score {best_score:.2f}")
        else:
            solution = "continue current activity"
            confidence = 0.3
            quality = ReasoningQuality.POOR
            reasoning_trace.append("No good options found, using default")

        # Determine if should escalate to reflective level
        should_escalate = (
            confidence < 0.5 or
            context.complexity > 0.7 or
            len(context.past_experiences) > 0  # Has relevant experiences to learn from
        )

        return ReasoningResult(
            level_used=ReasoningLevel.DELIBERATIVE,
            solution=solution,
            confidence=confidence,
            reasoning_trace=reasoning_trace,
            time_taken=(datetime.datetime.now() - start_time).total_seconds(),
            quality_estimate=quality,
            should_escalate=should_escalate,
            metadata={
                'options_considered': len(options),
                'best_score': best_score if evaluated_options else 0.0
            }
        )

    def _generate_options(self, context: ReasoningContext) -> List[str]:
        """Generate possible action options"""
        options = []

        # Option 1: Continue current goal
        if context.current_goal:
            options.append(f"continue working on: {context.current_goal}")

        # Option 2-4: Based on problem type
        problem_lower = context.problem.lower()

        if 'plan' in problem_lower or 'schedule' in problem_lower:
            options.extend([
                "create detailed plan for the day",
                "review and adjust existing plan",
                "break down goal into smaller tasks"
            ])
        elif 'social' in problem_lower or 'talk' in problem_lower or 'conversation' in problem_lower:
            options.extend([
                "initiate conversation",
                "respond thoughtfully to others",
                "observe social dynamics"
            ])
        elif 'work' in problem_lower or 'task' in problem_lower:
            options.extend([
                "focus on current task",
                "take a break and refocus",
                "seek help or resources"
            ])
        else:
            # General options
            options.extend([
                "gather more information",
                "try a new approach",
                "reflect on past experiences"
            ])

        return options

    def _evaluate_option(self, option: str, context: ReasoningContext) -> float:
        """Evaluate how good an option is"""
        score = 0.5  # Base score

        # Higher score if aligns with current goal
        if context.current_goal and context.current_goal.lower() in option.lower():
            score += 0.3

        # Consider constraints
        constraint_penalty = 0.0
        for constraint in context.constraints:
            if constraint.lower() in option.lower():
                constraint_penalty += 0.1
        score -= constraint_penalty

        # Consider urgency
        if context.urgency > 0.7:
            # Prefer quick, direct options
            if any(word in option.lower() for word in ['quick', 'immediate', 'now']):
                score += 0.2

        # Normalize to [0, 1]
        return min(max(score, 0.0), 1.0)


class ReflectiveReasoning:
    """
    Level 2: Reflective Reasoning

    Learning from experience, analogical reasoning, pattern discovery.
    Uses experience pool to find similar situations and learn from them.
    """

    def __init__(self, persona, experience_pool):
        self.persona = persona
        self.experience_pool = experience_pool

    def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Reflective reasoning: learn from past experiences.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult incorporating learned patterns
        """
        start_time = datetime.datetime.now()
        reasoning_trace = []

        # Step 1: Retrieve relevant experiences
        reasoning_trace.append("Searching experience pool for similar situations...")
        similar_experiences = self.experience_pool.orchestrate_experiences(
            current_problem=context.problem,
            context={'urgency': context.urgency, 'complexity': context.complexity},
            agent_id=self.persona.name,
            k=5
        )

        if not similar_experiences:
            reasoning_trace.append("No similar experiences found")
            return ReasoningResult(
                level_used=ReasoningLevel.REFLECTIVE,
                solution="",
                confidence=0.0,
                reasoning_trace=reasoning_trace,
                time_taken=(datetime.datetime.now() - start_time).total_seconds(),
                quality_estimate=ReasoningQuality.FAILED,
                should_escalate=True,
                metadata={'reason': 'no_experiences'}
            )

        reasoning_trace.append(f"Found {len(similar_experiences)} similar experiences")

        # Step 2: Analyze patterns in successful experiences
        successful_exps = [exp for exp in similar_experiences if exp.success]

        if successful_exps:
            reasoning_trace.append(f"Analyzing {len(successful_exps)} successful experiences")

            # Extract common strategies from successful experiences
            strategy_counts = {}
            for exp in successful_exps:
                strategy = exp.strategy_type
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

            best_strategy = max(strategy_counts.items(), key=lambda x: x[1])[0]
            reasoning_trace.append(f"Identified best strategy: {best_strategy}")

            # Synthesize solution based on successful patterns
            # For simplicity, adapt the best experience's solution
            best_exp = max(successful_exps, key=lambda x: x.success_metrics.get('accuracy', 0.5))
            solution = self._adapt_solution(best_exp.solution, context)
            reasoning_trace.append(f"Adapted solution from experience {best_exp.exp_id}")

            confidence = 0.7 + (0.2 * (len(successful_exps) / len(similar_experiences)))
            quality = ReasoningQuality.GOOD

        else:
            reasoning_trace.append("No successful experiences - learning from failures")

            # Learn what NOT to do from failures
            failed_exps = [exp for exp in similar_experiences if not exp.success]
            avoided_strategies = set(exp.strategy_type for exp in failed_exps)

            reasoning_trace.append(f"Avoiding strategies: {avoided_strategies}")

            # Generate novel solution
            solution = f"try novel approach (avoiding {avoided_strategies})"
            confidence = 0.4
            quality = ReasoningQuality.ADEQUATE

        # Step 3: Cross-validate with multiple experiences
        if len(similar_experiences) >= 3:
            reasoning_trace.append("Cross-validating solution...")
            validation_score = self._cross_validate(solution, similar_experiences)
            confidence = confidence * (0.5 + 0.5 * validation_score)
            reasoning_trace.append(f"Validation score: {validation_score:.2f}")

        # Decide if should escalate to meta-cognitive level
        should_escalate = (
            confidence < 0.6 or
            context.complexity > 0.8 or
            len(similar_experiences) < 2  # Not enough experience data
        )

        return ReasoningResult(
            level_used=ReasoningLevel.REFLECTIVE,
            solution=solution,
            confidence=confidence,
            reasoning_trace=reasoning_trace,
            time_taken=(datetime.datetime.now() - start_time).total_seconds(),
            quality_estimate=quality,
            should_escalate=should_escalate,
            metadata={
                'experiences_used': len(similar_experiences),
                'successful_experiences': len(successful_exps) if successful_exps else 0
            }
        )

    @staticmethod
    def _adapt_solution(original_solution: str, context: ReasoningContext) -> str:
        """Adapt a solution from past experience to current context"""
        # In a real implementation, this would use LLM to adapt the solution
        # For now, simple template
        adapted = original_solution

        # Add context-specific adaptations
        if context.urgency > 0.7:
            adapted = f"quickly {adapted}"

        if context.constraints:
            adapted = f"{adapted} (while respecting constraints)"

        return adapted

    @staticmethod
    def _cross_validate(solution: str, experiences: List[Any]) -> float:
        """Cross-validate solution against experiences"""
        # Check if solution is consistent with successful experiences
        # Simplified: just check if solution uses similar strategies

        if not experiences:
            return 0.5

        # Count how many experiences support this solution approach
        support_count = 0
        for exp in experiences:
            if exp.success:
                # Simple check: does solution relate to this experience?
                # In real implementation, use semantic similarity
                if any(word in solution.lower() for word in exp.solution.lower().split()[:5]):
                    support_count += 1

        return support_count / len(experiences)


class MetaCognitiveReasoning:
    """
    Level 3: Meta-Cognitive Reasoning

    Reasoning about reasoning. Self-aware decision making.
    Uses meta-cognitive system to monitor and regulate reasoning process itself.
    """

    def __init__(self, persona, metacognitive_system, experience_pool):
        self.persona = persona
        self.metacognitive_system = metacognitive_system
        self.experience_pool = experience_pool

        # Lower level reasoners
        self.deliberative = DeliberativeReasoning(persona)
        self.reflective = ReflectiveReasoning(persona, experience_pool)

    def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Meta-cognitive reasoning: reason about how to reason.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult from meta-cognitive analysis
        """
        start_time = datetime.datetime.now()
        reasoning_trace = []

        # Step 1: Meta-analyze the reasoning task itself
        reasoning_trace.append("Meta-analyzing reasoning requirements...")
        task_analysis = self._analyze_reasoning_task(context)
        reasoning_trace.append(f"Task analysis: {task_analysis}")

        # Step 2: Select appropriate reasoning strategy
        reasoning_trace.append("Selecting optimal reasoning strategy...")
        strategy = self._select_reasoning_strategy(task_analysis, context)
        reasoning_trace.append(f"Selected strategy: {strategy['name']}")

        # Step 3: Execute strategy with monitoring
        reasoning_trace.append("Executing strategy with self-monitoring...")
        result = self._execute_with_monitoring(strategy, context)
        reasoning_trace.extend(result.reasoning_trace)

        # Step 4: Evaluate our own reasoning process
        reasoning_trace.append("Evaluating reasoning quality...")
        self_evaluation = self._evaluate_reasoning_process(result, context)
        reasoning_trace.append(f"Self-evaluation: {self_evaluation}")

        # Step 5: Decide if reasoning is sufficient or needs improvement
        needs_improvement = self_evaluation['quality'].value < 4

        if needs_improvement:
            reasoning_trace.append("Reasoning quality insufficient - attempting improvement...")
            improved_result = self._improve_reasoning(result, context, self_evaluation)
            reasoning_trace.extend(improved_result.reasoning_trace)
            final_result = improved_result
        else:
            final_result = result

        # Update final result
        final_result.level_used = ReasoningLevel.METACOGNITIVE
        final_result.reasoning_trace = reasoning_trace
        final_result.time_taken = (datetime.datetime.now() - start_time).total_seconds()
        final_result.metadata['self_evaluation'] = self_evaluation
        final_result.metadata['strategy'] = strategy['name']

        return final_result

    def _analyze_reasoning_task(self, context: ReasoningContext) -> Dict[str, Any]:
        """Analyze what kind of reasoning this task requires"""
        analysis = {
            'is_novel': len(context.past_experiences) == 0,
            'is_complex': context.complexity > 0.7,
            'is_urgent': context.urgency > 0.7,
            'requires_learning': len(context.past_experiences) > 2,
            'requires_creativity': 'novel' in context.problem.lower() or 'new' in context.problem.lower(),
            'has_constraints': len(context.constraints) > 0
        }

        return analysis

    def _select_reasoning_strategy(self, task_analysis: Dict[str, Any],
                                  context: ReasoningContext) -> Dict[str, Any]:
        """Select the best reasoning strategy for this task"""

        # Get meta-cognitive system's recommendation
        recommended_strategies = self.metacognitive_system.get_strategy_recommendation(
            context.problem,
            "meta_cognitive_analysis"
        )

        # Analyze task requirements and match to strategies
        if task_analysis['is_urgent'] and not task_analysis['is_complex']:
            strategy = {
                'name': 'fast_deliberative',
                'level': ReasoningLevel.DELIBERATIVE,
                'use_experiences': False
            }
        elif task_analysis['requires_learning'] and task_analysis['has_constraints']:
            strategy = {
                'name': 'constrained_reflective',
                'level': ReasoningLevel.REFLECTIVE,
                'use_experiences': True
            }
        elif task_analysis['is_complex'] or task_analysis['requires_creativity']:
            strategy = {
                'name': 'deep_reflective_with_validation',
                'level': ReasoningLevel.REFLECTIVE,
                'use_experiences': True,
                'validate': True
            }
        else:
            strategy = {
                'name': 'standard_deliberative',
                'level': ReasoningLevel.DELIBERATIVE,
                'use_experiences': True
            }

        # Override with meta-cognitive recommendations if strong preference
        if recommended_strategies and recommended_strategies[0] in ['reflective_reasoning', 'experiential_learning']:
            strategy['use_experiences'] = True

        return strategy

    def _execute_with_monitoring(self, strategy: Dict[str, Any],
                                context: ReasoningContext) -> ReasoningResult:
        """Execute reasoning strategy with self-monitoring"""

        # Create monitoring snapshot
        snapshot = self.metacognitive_system.monitor(
            task_description=context.problem,
            reasoning_depth=strategy['level'].value,
            memory_quality=0.7,  # Would be computed from actual retrieval
            attention_focus=[context.current_goal] if context.current_goal else [],
            active_strategies=[strategy['name']],
            internal_confidence=0.6  # Initial estimate
        )

        # Check if we should proceed
        regulatory_actions = self.metacognitive_system.regulate(snapshot)

        # Execute appropriate level
        if strategy['level'] == ReasoningLevel.DELIBERATIVE:
            result = self.deliberative.reason(context)
        elif strategy['level'] == ReasoningLevel.REFLECTIVE:
            result = self.reflective.reason(context)
        else:
            # Default to deliberative
            result = self.deliberative.reason(context)

        # Apply regulatory actions
        if regulatory_actions['confidence_adjustment'] != 0:
            result.confidence += regulatory_actions['confidence_adjustment']
            result.confidence = min(max(result.confidence, 0.0), 1.0)

        return result

    def _evaluate_reasoning_process(self, result: ReasoningResult,
                                   context: ReasoningContext) -> Dict[str, Any]:
        """Evaluate the quality of our own reasoning"""

        # Predict quality based on multiple factors
        quality_indicators = []

        # 1. Confidence level
        if result.confidence > 0.7:
            quality_indicators.append(('confidence', ReasoningQuality.GOOD))
        elif result.confidence > 0.4:
            quality_indicators.append(('confidence', ReasoningQuality.ADEQUATE))
        else:
            quality_indicators.append(('confidence', ReasoningQuality.POOR))

        # 2. Reasoning depth (more steps usually better)
        reasoning_depth = len(result.reasoning_trace)
        if reasoning_depth >= 5:
            quality_indicators.append(('depth', ReasoningQuality.GOOD))
        elif reasoning_depth >= 3:
            quality_indicators.append(('depth', ReasoningQuality.ADEQUATE))
        else:
            quality_indicators.append(('depth', ReasoningQuality.POOR))

        # 3. Use of experiences (for complex tasks)
        if context.complexity > 0.5:
            experiences_used = result.metadata.get('experiences_used', 0)
            if experiences_used >= 3:
                quality_indicators.append(('experience_use', ReasoningQuality.GOOD))
            elif experiences_used >= 1:
                quality_indicators.append(('experience_use', ReasoningQuality.ADEQUATE))
            else:
                quality_indicators.append(('experience_use', ReasoningQuality.POOR))

        # Aggregate quality estimate
        avg_quality_value = np.mean([q.value for _, q in quality_indicators])
        if avg_quality_value >= 4:
            overall_quality = ReasoningQuality.EXCELLENT
        elif avg_quality_value >= 3.5:
            overall_quality = ReasoningQuality.GOOD
        elif avg_quality_value >= 2.5:
            overall_quality = ReasoningQuality.ADEQUATE
        elif avg_quality_value >= 1.5:
            overall_quality = ReasoningQuality.POOR
        else:
            overall_quality = ReasoningQuality.FAILED

        return {
            'quality': overall_quality,
            'indicators': quality_indicators,
            'confidence_in_evaluation': min(result.confidence + 0.2, 1.0)
        }

    def _improve_reasoning(self, original_result: ReasoningResult,
                          context: ReasoningContext,
                          evaluation: Dict[str, Any]) -> ReasoningResult:
        """Attempt to improve reasoning based on self-evaluation"""

        reasoning_trace = ["Attempting to improve reasoning..."]

        # Identify weakness
        weak_indicators = [
            indicator for indicator, quality in evaluation['indicators']
            if quality.value <= 2
        ]

        # Apply improvements based on weaknesses
        improved_solution = original_result.solution
        improved_confidence = original_result.confidence

        if 'confidence' in weak_indicators:
            # Low confidence - gather more evidence
            reasoning_trace.append("Low confidence - retrieving additional experiences")
            additional_experiences = self.experience_pool.orchestrate_experiences(
                current_problem=context.problem,
                context={},
                agent_id=self.persona.name,
                k=3
            )
            if additional_experiences:
                improved_confidence += 0.2
                reasoning_trace.append(f"Found {len(additional_experiences)} additional supporting experiences")

        if 'depth' in weak_indicators:
            # Shallow reasoning - add more steps
            reasoning_trace.append("Shallow reasoning detected - adding analysis depth")
            reasoning_trace.append(f"  -> Considering implications: {improved_solution}")
            reasoning_trace.append(f"  -> Checking consistency with goals")
            reasoning_trace.append(f"  -> Validating against constraints")

        if 'experience_use' in weak_indicators and context.complexity > 0.5:
            # Not using experiences on complex task
            reasoning_trace.append("Complex task requires experiential learning")
            reflective_result = self.reflective.reason(context)
            if reflective_result.confidence > improved_confidence:
                improved_solution = reflective_result.solution
                improved_confidence = reflective_result.confidence
                reasoning_trace.extend(reflective_result.reasoning_trace)

        # Create improved result
        improved_result = ReasoningResult(
            level_used=original_result.level_used,
            solution=improved_solution,
            confidence=min(improved_confidence, 1.0),
            reasoning_trace=reasoning_trace,
            time_taken=original_result.time_taken,
            quality_estimate=ReasoningQuality.GOOD if improved_confidence > 0.6 else ReasoningQuality.ADEQUATE,
            should_escalate=False,
            metadata={**original_result.metadata, 'improved': True}
        )

        return improved_result


class MultiLevelReasoningSystem:
    """
    Orchestrates multi-level reasoning, automatically selecting appropriate level.
    """

    def __init__(self, persona, metacognitive_system, experience_pool):
        self.persona = persona
        self.metacognitive_system = metacognitive_system
        self.experience_pool = experience_pool

        # Initialize all reasoning levels
        self.reactive = ReactiveReasoning(persona.name)
        self.deliberative = DeliberativeReasoning(persona)
        self.reflective = ReflectiveReasoning(persona, experience_pool)
        self.metacognitive = MetaCognitiveReasoning(
            persona, metacognitive_system, experience_pool
        )

    def reason(self,
              problem: str,
              urgency: float = 0.5,
              complexity: float = 0.5,
              available_time: float = 10.0,
              current_goal: str = "",
              constraints: List[str] = None,
              force_level: Optional[ReasoningLevel] = None) -> ReasoningResult:
        """
        Perform reasoning at appropriate level.

        Args:
            problem: Problem to solve
            urgency: How urgent (0-1)
            complexity: Estimated complexity (0-1)
            available_time: Time available in seconds
            current_goal: Current goal context
            constraints: Any constraints
            force_level: Force specific reasoning level (for testing)

        Returns:
            ReasoningResult
        """
        if constraints is None:
            constraints = []

        # Create context
        context = ReasoningContext(
            problem=problem,
            urgency=urgency,
            complexity=complexity,
            available_time=available_time,
            past_experiences=[],  # Would be populated from experience pool
            current_goal=current_goal,
            constraints=constraints
        )

        # Select appropriate level
        if force_level is not None:
            selected_level = force_level
        else:
            selected_level = self._select_reasoning_level(context)

        # Execute reasoning at selected level
        if selected_level == ReasoningLevel.REACTIVE:
            result = self.reactive.reason(context)

            # Escalate if needed
            if result.should_escalate:
                result = self.deliberative.reason(context)

        elif selected_level == ReasoningLevel.DELIBERATIVE:
            result = self.deliberative.reason(context)

            # Escalate if needed
            if result.should_escalate:
                result = self.reflective.reason(context)

        elif selected_level == ReasoningLevel.REFLECTIVE:
            result = self.reflective.reason(context)

            # Escalate if needed
            if result.should_escalate:
                result = self.metacognitive.reason(context)

        else:  # METACOGNITIVE
            result = self.metacognitive.reason(context)

        return result

    def _select_reasoning_level(self, context: ReasoningContext) -> ReasoningLevel:
        """Select appropriate reasoning level based on context"""

        # Very urgent and low complexity -> Reactive
        if context.urgency > 0.8 and context.complexity < 0.3:
            return ReasoningLevel.REACTIVE

        # High urgency, moderate complexity -> Deliberative
        if context.urgency > 0.6 and context.complexity < 0.6:
            return ReasoningLevel.DELIBERATIVE

        # High complexity or many experiences available -> Reflective
        if context.complexity > 0.6 or len(context.past_experiences) > 3:
            return ReasoningLevel.REFLECTIVE

        # Very high complexity or novel situation -> Meta-cognitive
        if context.complexity > 0.8 or (context.complexity > 0.6 and len(context.past_experiences) == 0):
            return ReasoningLevel.METACOGNITIVE

        # Default: Deliberative
        return ReasoningLevel.DELIBERATIVE
