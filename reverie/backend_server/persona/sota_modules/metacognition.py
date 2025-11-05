"""
Meta-Cognitive System - Monitoring and Regulating Reasoning

Implements a bi-level cognitive architecture where a meta-cognitive layer
monitors, evaluates, and regulates the underlying cognitive processes.

Key capabilities:
- Self-monitoring: Track own reasoning quality and decision-making
- Self-evaluation: Assess performance and identify weaknesses
- Self-regulation: Adjust strategies and behaviors based on evaluation
- Epistemic awareness: Know what you know and don't know
- Error detection and correction

Based on: "Truly Self-Improving Agents Require Intrinsic Metacognitive Learning"
and related EMNLP 2024/2025 research on meta-cognition.
"""

import datetime
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import sys
sys.path.append('../../')

from global_methods import *


class ReasoningQuality(Enum):
    """Quality levels for reasoning"""
    EXCELLENT = 5
    GOOD = 4
    ADEQUATE = 3
    POOR = 2
    FAILED = 1


class CognitiveState(Enum):
    """Current cognitive state of the agent"""
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    CONFUSED = "confused"
    LEARNING = "learning"
    EXPERT = "expert"


@dataclass
class MonitoringSnapshot:
    """Snapshot of cognitive state at a moment in time"""
    timestamp: str
    task_description: str
    cognitive_state: CognitiveState
    confidence_level: float
    reasoning_depth: int
    memory_retrieval_quality: float
    attention_focus: List[str]
    active_strategies: List[str]
    error_indicators: List[str]

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'task_description': self.task_description,
            'cognitive_state': self.cognitive_state.value,
            'confidence_level': self.confidence_level,
            'reasoning_depth': self.reasoning_depth,
            'memory_retrieval_quality': self.memory_retrieval_quality,
            'attention_focus': self.attention_focus,
            'active_strategies': self.active_strategies,
            'error_indicators': self.error_indicators
        }


@dataclass
class PerformanceEvaluation:
    """Evaluation of performance on a task"""
    task_id: str
    task_type: str
    predicted_quality: ReasoningQuality
    actual_quality: ReasoningQuality
    success: bool
    errors_made: List[str]
    strategies_used: List[str]
    time_taken: float
    confidence_accuracy: float  # How well confidence matched reality
    lessons_learned: List[str]
    timestamp: str

    def calibration_error(self) -> float:
        """How far off was the prediction from reality"""
        return abs(self.predicted_quality.value - self.actual_quality.value)


@dataclass
class StrategyPerformance:
    """Track performance of different cognitive strategies"""
    strategy_name: str
    times_used: int = 0
    successes: int = 0
    failures: int = 0
    avg_confidence: float = 0.5
    avg_quality: float = 0.5
    contexts_effective: List[str] = field(default_factory=list)
    contexts_ineffective: List[str] = field(default_factory=list)

    def success_rate(self) -> float:
        if self.times_used == 0:
            return 0.0
        return self.successes / self.times_used

    def should_use(self, context: str, threshold: float = 0.5) -> bool:
        """Determine if this strategy should be used in this context"""
        if self.times_used < 3:  # Not enough data
            return True

        # Check if context is known to be effective
        if context in self.contexts_effective:
            return True
        if context in self.contexts_ineffective:
            return False

        # Use success rate
        return self.success_rate() >= threshold


class MetaCognitiveSystem:
    """
    Meta-cognitive layer that monitors and regulates cognitive processes.

    This implements a bi-level architecture:
    - Level 1 (Cognitive): The actual reasoning, planning, decision-making
    - Level 2 (Meta-cognitive): Monitoring and regulating Level 1
    """

    def __init__(self, agent_name: str):
        """
        Initialize the meta-cognitive system.

        Args:
            agent_name: Name of the agent this system belongs to
        """
        self.agent_name = agent_name

        # Monitoring history
        self.monitoring_history: List[MonitoringSnapshot] = []

        # Performance tracking
        self.performance_history: List[PerformanceEvaluation] = []

        # Strategy registry and performance
        self.strategies: Dict[str, StrategyPerformance] = {}

        # Current cognitive state
        self.current_state = CognitiveState.LEARNING
        self.confidence_level = 0.5

        # Self-knowledge: what we know we're good/bad at
        self.known_strengths: List[str] = []
        self.known_weaknesses: List[str] = []

        # Error patterns
        self.common_errors: Dict[str, int] = {}

        # Calibration tracking (how well do we estimate our own performance)
        self.calibration_history: List[float] = []

        # Intervention triggers
        self.intervention_threshold = 0.3  # Confidence below this triggers intervention

    def monitor(self,
               task_description: str,
               reasoning_depth: int,
               memory_quality: float,
               attention_focus: List[str],
               active_strategies: List[str],
               internal_confidence: float) -> MonitoringSnapshot:
        """
        Monitor current cognitive processes.

        Args:
            task_description: What task is being performed
            reasoning_depth: How many levels deep is the reasoning
            memory_quality: Quality of memory retrieval (0-1)
            attention_focus: What agent is focusing on
            active_strategies: Which strategies are being used
            internal_confidence: Agent's self-assessed confidence

        Returns:
            MonitoringSnapshot of current state
        """
        # Detect cognitive state
        cognitive_state = self._assess_cognitive_state(
            internal_confidence, memory_quality, reasoning_depth
        )

        # Detect potential errors
        error_indicators = self._detect_error_indicators(
            internal_confidence, memory_quality, active_strategies
        )

        snapshot = MonitoringSnapshot(
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            task_description=task_description,
            cognitive_state=cognitive_state,
            confidence_level=internal_confidence,
            reasoning_depth=reasoning_depth,
            memory_retrieval_quality=memory_quality,
            attention_focus=attention_focus,
            active_strategies=active_strategies,
            error_indicators=error_indicators
        )

        self.monitoring_history.append(snapshot)

        # Update current state
        self.current_state = cognitive_state
        self.confidence_level = internal_confidence

        return snapshot

    def evaluate_performance(self,
                           task_id: str,
                           task_type: str,
                           predicted_quality: ReasoningQuality,
                           actual_outcome: Dict[str, Any],
                           strategies_used: List[str],
                           time_taken: float,
                           predicted_confidence: float) -> PerformanceEvaluation:
        """
        Evaluate performance after task completion.

        Args:
            task_id: Unique task identifier
            task_type: Type of task
            predicted_quality: What quality we expected
            actual_outcome: Actual results
            strategies_used: Which strategies were used
            time_taken: How long it took
            predicted_confidence: What confidence level we had

        Returns:
            PerformanceEvaluation
        """
        # Determine actual quality from outcome
        actual_quality = self._assess_actual_quality(actual_outcome)

        # Check if successful
        success = actual_outcome.get('success', False)

        # Extract errors
        errors_made = actual_outcome.get('errors', [])

        # Calculate confidence accuracy
        # If we were confident and succeeded, or unconfident and failed, that's good calibration
        actual_success_value = 1.0 if success else 0.0
        confidence_accuracy = 1.0 - abs(predicted_confidence - actual_success_value)

        # Generate lessons learned
        lessons = self._generate_lessons(
            predicted_quality, actual_quality, errors_made, strategies_used
        )

        evaluation = PerformanceEvaluation(
            task_id=task_id,
            task_type=task_type,
            predicted_quality=predicted_quality,
            actual_quality=actual_quality,
            success=success,
            errors_made=errors_made,
            strategies_used=strategies_used,
            time_taken=time_taken,
            confidence_accuracy=confidence_accuracy,
            lessons_learned=lessons,
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        self.performance_history.append(evaluation)

        # Update strategy performance
        self._update_strategy_performance(evaluation, task_type)

        # Update calibration history
        self.calibration_history.append(evaluation.calibration_error())

        # Update error patterns
        for error in errors_made:
            self.common_errors[error] = self.common_errors.get(error, 0) + 1

        # Update strengths/weaknesses
        self._update_self_knowledge(task_type, success, actual_quality)

        return evaluation

    def regulate(self, snapshot: MonitoringSnapshot) -> Dict[str, Any]:
        """
        Regulate cognitive processes based on monitoring.

        This is the key meta-cognitive function: based on what we observe,
        adjust behavior, suggest interventions, or change strategies.

        Args:
            snapshot: Current monitoring snapshot

        Returns:
            Regulatory actions to take
        """
        actions = {
            'continue_current_approach': True,
            'interventions': [],
            'strategy_changes': [],
            'attention_shifts': [],
            'confidence_adjustment': 0.0
        }

        # Check if confidence is too low
        if snapshot.confidence_level < self.intervention_threshold:
            actions['continue_current_approach'] = False
            actions['interventions'].append({
                'type': 'low_confidence',
                'action': 'request_help_or_retrieve_more_information',
                'reason': f'Confidence {snapshot.confidence_level} below threshold {self.intervention_threshold}'
            })

        # Check for error indicators
        if snapshot.error_indicators:
            actions['interventions'].append({
                'type': 'error_detection',
                'action': 'verify_reasoning_steps',
                'errors': snapshot.error_indicators
            })

        # Check if current strategies are effective
        ineffective_strategies = []
        for strategy in snapshot.active_strategies:
            if strategy in self.strategies:
                task_context = self._extract_context(snapshot.task_description)
                if not self.strategies[strategy].should_use(task_context):
                    ineffective_strategies.append(strategy)

        if ineffective_strategies:
            actions['strategy_changes'].append({
                'remove': ineffective_strategies,
                'reason': 'strategies_historically_ineffective',
                'suggest_alternatives': self._suggest_alternative_strategies(
                    snapshot.task_description
                )
            })

        # Check if we're confused (stuck in uncertainty)
        if snapshot.cognitive_state == CognitiveState.CONFUSED:
            actions['interventions'].append({
                'type': 'confusion_resolution',
                'action': 'break_down_problem_or_seek_clarification'
            })

        # Adjust confidence based on calibration history
        if len(self.calibration_history) > 5:
            # If we're consistently over-confident, adjust down
            avg_calibration_error = np.mean(self.calibration_history[-10:])
            if avg_calibration_error > 0.3:
                actions['confidence_adjustment'] = -0.1
                actions['interventions'].append({
                    'type': 'calibration_correction',
                    'action': 'reduce_overconfidence'
                })

        # Check memory retrieval quality
        if snapshot.memory_retrieval_quality < 0.3:
            actions['interventions'].append({
                'type': 'poor_memory_retrieval',
                'action': 'broaden_search_or_use_different_keywords'
            })

        # Suggest attention shifts if stuck
        if self._is_stuck(snapshot):
            actions['attention_shifts'] = self._suggest_attention_shifts(snapshot)

        return actions

    def get_strategy_recommendation(self, task_description: str, context: str) -> List[str]:
        """
        Recommend which strategies to use for a given task.

        Args:
            task_description: Description of the task
            context: Context information

        Returns:
            List of recommended strategies
        """
        recommendations = []

        # Check historical performance
        for strategy_name, perf in self.strategies.items():
            if perf.should_use(context, threshold=0.6):
                recommendations.append(strategy_name)

        # If no clear recommendations, use diverse exploration
        if not recommendations:
            recommendations = ['default_planning', 'reflective_reasoning', 'experiential_learning']

        return recommendations

    def should_request_help(self, task_description: str, confidence: float) -> Tuple[bool, str]:
        """
        Determine if agent should request help from other agents or humans.

        Args:
            task_description: Task at hand
            confidence: Current confidence level

        Returns:
            (should_request, reason)
        """
        # Low confidence
        if confidence < 0.2:
            return True, "Very low confidence in ability to complete task"

        # Known weakness
        task_type = self._extract_context(task_description)
        if task_type in self.known_weaknesses:
            return True, f"Known weakness in {task_type}"

        # Repeated failures in this area
        recent_failures = [
            eval for eval in self.performance_history[-10:]
            if not eval.success and task_type in eval.task_type
        ]
        if len(recent_failures) >= 3:
            return True, f"Multiple recent failures in {task_type}"

        return False, ""

    def get_self_assessment(self) -> Dict[str, Any]:
        """
        Generate comprehensive self-assessment.

        Returns:
            Dictionary with self-knowledge about capabilities
        """
        if not self.performance_history:
            return {
                'overall_performance': 'Unknown',
                'strengths': [],
                'weaknesses': [],
                'calibration': 'Unknown',
                'learning_trend': 'Unknown'
            }

        # Calculate overall success rate
        recent_evals = self.performance_history[-20:]
        success_rate = sum(1 for e in recent_evals if e.success) / len(recent_evals)

        # Determine overall performance level
        if success_rate >= 0.8:
            overall = 'Excellent'
        elif success_rate >= 0.6:
            overall = 'Good'
        elif success_rate >= 0.4:
            overall = 'Adequate'
        else:
            overall = 'Poor'

        # Calibration assessment
        if len(self.calibration_history) > 5:
            avg_cal_error = np.mean(self.calibration_history[-20:])
            if avg_cal_error < 0.2:
                calibration = 'Well-calibrated'
            elif avg_cal_error < 0.4:
                calibration = 'Moderately calibrated'
            else:
                calibration = 'Poorly calibrated (overconfident or underconfident)'
        else:
            calibration = 'Insufficient data'

        # Learning trend
        if len(recent_evals) >= 10:
            first_half_success = sum(1 for e in recent_evals[:10] if e.success) / 10
            second_half_success = sum(1 for e in recent_evals[10:] if e.success) / len(recent_evals[10:])
            if second_half_success > first_half_success + 0.1:
                learning_trend = 'Improving'
            elif second_half_success < first_half_success - 0.1:
                learning_trend = 'Declining'
            else:
                learning_trend = 'Stable'
        else:
            learning_trend = 'Insufficient data'

        return {
            'agent_name': self.agent_name,
            'overall_performance': overall,
            'success_rate': success_rate,
            'strengths': self.known_strengths[:5],
            'weaknesses': self.known_weaknesses[:5],
            'calibration': calibration,
            'avg_calibration_error': np.mean(self.calibration_history[-20:]) if self.calibration_history else 0,
            'learning_trend': learning_trend,
            'current_state': self.current_state.value,
            'most_common_errors': sorted(self.common_errors.items(), key=lambda x: x[1], reverse=True)[:5],
            'best_strategies': self._get_best_strategies(),
            'total_tasks_completed': len(self.performance_history)
        }

    def _assess_cognitive_state(self, confidence: float, memory_quality: float, depth: int) -> CognitiveState:
        """Assess current cognitive state"""
        if confidence > 0.8 and memory_quality > 0.7:
            if len(self.performance_history) > 50:
                return CognitiveState.EXPERT
            return CognitiveState.CONFIDENT

        if confidence < 0.3 or memory_quality < 0.3:
            if depth < 2:
                return CognitiveState.CONFUSED
            return CognitiveState.UNCERTAIN

        return CognitiveState.LEARNING

    def _detect_error_indicators(self, confidence: float, memory_quality: float, strategies: List[str]) -> List[str]:
        """Detect potential errors in reasoning"""
        indicators = []

        if confidence < 0.2:
            indicators.append("extremely_low_confidence")

        if memory_quality < 0.2:
            indicators.append("poor_memory_retrieval")

        if not strategies:
            indicators.append("no_clear_strategy")

        # Check for known problematic strategy combinations
        if 'hasty_generalization' in strategies and 'shallow_reasoning' in strategies:
            indicators.append("potentially_flawed_reasoning_pattern")

        return indicators

    def _assess_actual_quality(self, outcome: Dict[str, Any]) -> ReasoningQuality:
        """Assess actual reasoning quality from outcome"""
        if outcome.get('success', False):
            accuracy = outcome.get('accuracy', 0.5)
            if accuracy >= 0.9:
                return ReasoningQuality.EXCELLENT
            elif accuracy >= 0.7:
                return ReasoningQuality.GOOD
            else:
                return ReasoningQuality.ADEQUATE
        else:
            if outcome.get('partial_success', False):
                return ReasoningQuality.POOR
            return ReasoningQuality.FAILED

    def _generate_lessons(self, predicted: ReasoningQuality, actual: ReasoningQuality,
                         errors: List[str], strategies: List[str]) -> List[str]:
        """Generate lessons learned from performance"""
        lessons = []

        # Calibration lesson
        if predicted.value > actual.value + 1:
            lessons.append("Was overconfident - need to be more cautious in predictions")
        elif predicted.value < actual.value - 1:
            lessons.append("Was underconfident - can trust abilities more")

        # Error-specific lessons
        for error in errors:
            if error in self.common_errors and self.common_errors[error] > 3:
                lessons.append(f"Recurring error pattern: {error} - need systematic fix")

        # Strategy lessons
        if not errors and strategies:
            lessons.append(f"Successful strategies: {', '.join(strategies)} - use in similar contexts")

        return lessons

    def _update_strategy_performance(self, evaluation: PerformanceEvaluation, context: str):
        """Update performance tracking for strategies"""
        for strategy in evaluation.strategies_used:
            if strategy not in self.strategies:
                self.strategies[strategy] = StrategyPerformance(strategy_name=strategy)

            perf = self.strategies[strategy]
            perf.times_used += 1

            if evaluation.success:
                perf.successes += 1
                if context not in perf.contexts_effective:
                    perf.contexts_effective.append(context)
            else:
                perf.failures += 1
                if context not in perf.contexts_ineffective:
                    perf.contexts_ineffective.append(context)

            # Update averages
            perf.avg_confidence = (
                (perf.avg_confidence * (perf.times_used - 1) + evaluation.confidence_accuracy) /
                perf.times_used
            )
            perf.avg_quality = (
                (perf.avg_quality * (perf.times_used - 1) + evaluation.actual_quality.value / 5.0) /
                perf.times_used
            )

    def _update_self_knowledge(self, task_type: str, success: bool, quality: ReasoningQuality):
        """Update knowledge about strengths and weaknesses"""
        if success and quality.value >= 4:
            if task_type not in self.known_strengths:
                # Check if consistently good at this
                recent_in_type = [
                    e for e in self.performance_history[-20:]
                    if task_type in e.task_type
                ]
                if len(recent_in_type) >= 3:
                    success_rate = sum(1 for e in recent_in_type if e.success) / len(recent_in_type)
                    if success_rate >= 0.75:
                        self.known_strengths.append(task_type)

        elif not success or quality.value <= 2:
            if task_type not in self.known_weaknesses:
                # Check if consistently poor at this
                recent_in_type = [
                    e for e in self.performance_history[-20:]
                    if task_type in e.task_type
                ]
                if len(recent_in_type) >= 3:
                    success_rate = sum(1 for e in recent_in_type if e.success) / len(recent_in_type)
                    if success_rate <= 0.33:
                        self.known_weaknesses.append(task_type)

    def _suggest_alternative_strategies(self, task_description: str) -> List[str]:
        """Suggest alternative strategies for a task"""
        context = self._extract_context(task_description)

        # Find strategies that work well in this context
        good_strategies = [
            name for name, perf in self.strategies.items()
            if context in perf.contexts_effective and perf.success_rate() > 0.6
        ]

        if good_strategies:
            return good_strategies

        # Default alternatives
        return ['systematic_planning', 'experiential_retrieval', 'collaborative_solving']

    def _is_stuck(self, snapshot: MonitoringSnapshot) -> bool:
        """Determine if agent is stuck"""
        # Check recent history for lack of progress
        if len(self.monitoring_history) < 3:
            return False

        recent = self.monitoring_history[-3:]

        # Same low confidence repeatedly
        if all(s.confidence_level < 0.3 for s in recent):
            return True

        # Same attention focus (not making progress)
        if len(set(tuple(s.attention_focus) for s in recent)) == 1:
            return True

        return False

    def _suggest_attention_shifts(self, snapshot: MonitoringSnapshot) -> List[Dict[str, str]]:
        """Suggest where to shift attention when stuck"""
        shifts = []

        # Suggest looking at different aspects
        current_focus = set(snapshot.attention_focus)

        # Broaden focus
        shifts.append({
            'type': 'broaden',
            'suggestion': 'Consider broader context and related concepts'
        })

        # Try different angle
        shifts.append({
            'type': 'reframe',
            'suggestion': 'Reframe the problem from a different perspective'
        })

        # Seek external input
        shifts.append({
            'type': 'external_input',
            'suggestion': 'Consult experience pool or other agents'
        })

        return shifts

    def _extract_context(self, text: str) -> str:
        """Extract context/type from text (simplified)"""
        # In production, use more sophisticated NLP
        text_lower = text.lower()

        if any(word in text_lower for word in ['plan', 'schedule', 'organize']):
            return 'planning'
        elif any(word in text_lower for word in ['social', 'conversation', 'talk']):
            return 'social_interaction'
        elif any(word in text_lower for word in ['problem', 'solve', 'figure out']):
            return 'problem_solving'
        elif any(word in text_lower for word in ['remember', 'recall', 'memory']):
            return 'memory_retrieval'
        else:
            return 'general'

    def _get_best_strategies(self) -> List[Dict[str, Any]]:
        """Get best performing strategies"""
        sorted_strategies = sorted(
            self.strategies.values(),
            key=lambda s: s.success_rate(),
            reverse=True
        )

        return [
            {
                'name': s.strategy_name,
                'success_rate': s.success_rate(),
                'times_used': s.times_used
            }
            for s in sorted_strategies[:5]
        ]
