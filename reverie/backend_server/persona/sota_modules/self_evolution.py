"""
Self-Evolution Engine

Enables agents to continuously improve through:
- Performance analysis and pattern recognition
- Strategy adaptation and optimization
- Architecture modification (meta-learning)
- Curriculum learning (progressively harder tasks)
- Co-evolution with other agents

Based on recent research on self-improving AI agents and meta-learning.
"""

import datetime
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import sys
sys.path.append('../../')

from global_methods import *


@dataclass
class PerformanceMetrics:
    """Performance metrics for a task or time period"""
    success_rate: float
    avg_confidence: float
    avg_quality_score: float
    efficiency: float  # Time taken relative to baseline
    error_rate: float
    learning_rate: float  # Rate of improvement
    timestamp: str


@dataclass
class EvolutionEvent:
    """Record of an evolutionary change"""
    event_id: str
    timestamp: str
    change_type: str  # "strategy_addition", "parameter_tuning", "architecture_modification"
    description: str
    rationale: str
    before_metrics: PerformanceMetrics
    after_metrics: Optional[PerformanceMetrics] = None
    success: Optional[bool] = None  # Was this change beneficial?


@dataclass
class AdaptiveStrategy:
    """A strategy that can be adapted based on performance"""
    strategy_id: str
    name: str
    description: str
    parameters: Dict[str, float]
    performance_history: List[PerformanceMetrics] = field(default_factory=list)
    contexts_effective: List[str] = field(default_factory=list)
    contexts_ineffective: List[str] = field(default_factory=list)
    times_used: int = 0
    times_succeeded: int = 0

    def effectiveness(self) -> float:
        """Calculate overall effectiveness"""
        if self.times_used == 0:
            return 0.5
        return self.times_succeeded / self.times_used

    def is_improving(self) -> bool:
        """Check if strategy is improving over time"""
        if len(self.performance_history) < 5:
            return False

        recent = self.performance_history[-5:]
        older = self.performance_history[-10:-5] if len(self.performance_history) >= 10 else self.performance_history[:-5]

        if not older:
            return True

        recent_avg = np.mean([p.success_rate for p in recent])
        older_avg = np.mean([p.success_rate for p in older])

        return recent_avg > older_avg


class SelfEvolutionEngine:
    """
    Engine for continuous self-improvement.

    Monitors performance, identifies weaknesses, and autonomously
    adapts strategies and behaviors.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

        # Evolution history
        self.evolution_history: List[EvolutionEvent] = []
        self.event_count = 0

        # Performance tracking
        self.performance_timeline: List[PerformanceMetrics] = []

        # Adaptive strategies
        self.strategies: Dict[str, AdaptiveStrategy] = {}
        self._init_default_strategies()

        # Current configuration
        self.current_config = {
            'learning_rate': 0.1,
            'exploration_rate': 0.2,
            'confidence_threshold': 0.5,
            'reflection_frequency': 0.1,
            'collaboration_propensity': 0.5
        }

        # Performance baselines
        self.baseline_metrics = None

        # Curriculum learning
        self.current_difficulty_level = 0.3  # Start easy
        self.difficulty_progression_rate = 0.05

        # Meta-learning: learning how to learn
        self.meta_learning_history: List[Dict[str, Any]] = []

    def _init_default_strategies(self):
        """Initialize default adaptive strategies"""
        default_strategies = [
            AdaptiveStrategy(
                strategy_id="strat_1",
                name="deliberative_planning",
                description="Careful planning with multiple options",
                parameters={'depth': 3, 'breadth': 5}
            ),
            AdaptiveStrategy(
                strategy_id="strat_2",
                name="experiential_learning",
                description="Learn from past experiences",
                parameters={'similarity_threshold': 0.7, 'max_experiences': 5}
            ),
            AdaptiveStrategy(
                strategy_id="strat_3",
                name="collaborative_problem_solving",
                description="Seek help from others",
                parameters={'help_threshold': 0.4, 'max_collaborators': 3}
            ),
            AdaptiveStrategy(
                strategy_id="strat_4",
                name="rapid_prototyping",
                description="Quick attempts with iteration",
                parameters={'iterations': 3, 'time_per_iteration': 1.0}
            )
        ]

        for strategy in default_strategies:
            self.strategies[strategy.strategy_id] = strategy

    def record_performance(self,
                          success: bool,
                          confidence: float,
                          quality_score: float,
                          time_taken: float,
                          errors: int,
                          strategy_used: Optional[str] = None):
        """
        Record performance on a task.

        Args:
            success: Was task successful
            confidence: Confidence level (0-1)
            quality_score: Quality of result (0-1)
            time_taken: Time taken in seconds
            errors: Number of errors made
            strategy_used: Which strategy was used
        """
        # Calculate metrics
        success_rate = 1.0 if success else 0.0

        # Calculate efficiency (lower is better, normalized to 0-1)
        baseline_time = 10.0  # Baseline time for comparison
        efficiency = min(baseline_time / max(time_taken, 0.1), 1.0)

        error_rate = min(errors / 10.0, 1.0)  # Normalize assuming max 10 errors

        # Calculate learning rate (improvement over recent history)
        if len(self.performance_timeline) > 5:
            recent_success = np.mean([p.success_rate for p in self.performance_timeline[-5:]])
            learning_rate = max(success_rate - recent_success, 0.0)
        else:
            learning_rate = 0.0

        metrics = PerformanceMetrics(
            success_rate=success_rate,
            avg_confidence=confidence,
            avg_quality_score=quality_score,
            efficiency=efficiency,
            error_rate=error_rate,
            learning_rate=learning_rate,
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        self.performance_timeline.append(metrics)

        # Update strategy performance if strategy was used
        if strategy_used and strategy_used in self.strategies:
            strategy = self.strategies[strategy_used]
            strategy.performance_history.append(metrics)
            strategy.times_used += 1
            if success:
                strategy.times_succeeded += 1

        # Set baseline if this is first recording
        if self.baseline_metrics is None:
            self.baseline_metrics = metrics

    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze recent performance to identify improvement opportunities.

        Returns:
            Analysis with identified issues and recommendations
        """
        if len(self.performance_timeline) < 3:
            return {
                'status': 'insufficient_data',
                'issues': [],
                'recommendations': []
            }

        recent = self.performance_timeline[-10:]

        analysis = {
            'status': 'analyzed',
            'current_performance': {
                'avg_success_rate': np.mean([p.success_rate for p in recent]),
                'avg_confidence': np.mean([p.avg_confidence for p in recent]),
                'avg_quality': np.mean([p.avg_quality_score for p in recent]),
                'avg_efficiency': np.mean([p.efficiency for p in recent]),
                'avg_error_rate': np.mean([p.error_rate for p in recent])
            },
            'issues': [],
            'recommendations': []
        }

        # Identify issues
        if analysis['current_performance']['avg_success_rate'] < 0.6:
            analysis['issues'].append({
                'type': 'low_success_rate',
                'severity': 'high',
                'description': f"Success rate {analysis['current_performance']['avg_success_rate']:.2f} is below acceptable threshold"
            })
            analysis['recommendations'].append({
                'action': 'increase_deliberation',
                'reason': 'Low success rate suggests need for more careful reasoning'
            })

        if analysis['current_performance']['avg_confidence'] > analysis['current_performance']['avg_success_rate'] + 0.2:
            analysis['issues'].append({
                'type': 'overconfidence',
                'severity': 'medium',
                'description': 'Confidence exceeds actual performance'
            })
            analysis['recommendations'].append({
                'action': 'calibrate_confidence',
                'reason': 'Need to reduce overconfidence'
            })

        if analysis['current_performance']['avg_error_rate'] > 0.3:
            analysis['issues'].append({
                'type': 'high_error_rate',
                'severity': 'high',
                'description': f"Error rate {analysis['current_performance']['avg_error_rate']:.2f} is too high"
            })
            analysis['recommendations'].append({
                'action': 'enhance_error_checking',
                'reason': 'High error rate suggests need for validation steps'
            })

        if analysis['current_performance']['avg_efficiency'] < 0.5:
            analysis['issues'].append({
                'type': 'low_efficiency',
                'severity': 'medium',
                'description': 'Tasks taking longer than expected'
            })
            analysis['recommendations'].append({
                'action': 'optimize_strategies',
                'reason': 'Low efficiency suggests strategies need optimization'
            })

        # Check for stagnation
        if len(recent) >= 5:
            learning_rates = [p.learning_rate for p in recent]
            if np.mean(learning_rates) < 0.01:
                analysis['issues'].append({
                    'type': 'stagnation',
                    'severity': 'medium',
                    'description': 'No improvement observed recently'
                })
                analysis['recommendations'].append({
                    'action': 'increase_exploration',
                    'reason': 'Stagnation suggests need for trying new approaches'
                })

        return analysis

    def evolve(self, force_evolution: bool = False) -> List[EvolutionEvent]:
        """
        Perform self-evolution based on performance analysis.

        Args:
            force_evolution: Force evolution even if not triggered naturally

        Returns:
            List of evolution events that occurred
        """
        # Check if evolution should trigger
        if not force_evolution and not self._should_evolve():
            return []

        events = []

        # Analyze current performance
        analysis = self.analyze_performance()

        if analysis['status'] == 'insufficient_data':
            return events

        # Take current performance snapshot
        current_metrics = self.performance_timeline[-1]

        # Execute recommendations
        for recommendation in analysis['recommendations']:
            event = self._execute_evolution(
                recommendation['action'],
                recommendation['reason'],
                current_metrics
            )
            if event:
                events.append(event)

        # Adapt strategies
        strategy_events = self._adapt_strategies()
        events.extend(strategy_events)

        # Adjust difficulty for curriculum learning
        difficulty_event = self._adjust_curriculum_difficulty()
        if difficulty_event:
            events.append(difficulty_event)

        return events

    def _should_evolve(self) -> bool:
        """Determine if evolution should trigger"""
        if len(self.performance_timeline) < 5:
            return False

        # Trigger if performance is declining
        recent = self.performance_timeline[-5:]
        older = self.performance_timeline[-10:-5] if len(self.performance_timeline) >= 10 else []

        if older:
            recent_avg = np.mean([p.success_rate for p in recent])
            older_avg = np.mean([p.success_rate for p in older])

            if recent_avg < older_avg - 0.1:  # Decline > 10%
                return True

        # Trigger if stagnating
        learning_rates = [p.learning_rate for p in recent]
        if np.mean(learning_rates) < 0.01:
            return True

        # Periodic evolution
        if len(self.evolution_history) == 0 or len(self.performance_timeline) % 20 == 0:
            return True

        return False

    def _execute_evolution(self,
                          action: str,
                          rationale: str,
                          current_metrics: PerformanceMetrics) -> Optional[EvolutionEvent]:
        """Execute a specific evolutionary action"""
        self.event_count += 1
        event_id = f"evol_{self.agent_name}_{self.event_count}"

        description = ""
        change_type = ""

        if action == 'increase_deliberation':
            # Increase depth of reasoning
            old_value = self.current_config.get('deliberation_depth', 3)
            self.current_config['deliberation_depth'] = old_value + 1
            description = f"Increased deliberation depth from {old_value} to {old_value + 1}"
            change_type = "parameter_tuning"

        elif action == 'calibrate_confidence':
            # Adjust confidence calibration
            old_value = self.current_config.get('confidence_threshold', 0.5)
            self.current_config['confidence_threshold'] = max(old_value + 0.1, 0.3)
            description = f"Adjusted confidence threshold from {old_value:.2f} to {self.current_config['confidence_threshold']:.2f}"
            change_type = "parameter_tuning"

        elif action == 'enhance_error_checking':
            # Enable more validation steps
            self.current_config['enable_validation'] = True
            self.current_config['validation_strictness'] = 0.8
            description = "Enabled enhanced error checking with strict validation"
            change_type = "architecture_modification"

        elif action == 'optimize_strategies':
            # Remove ineffective strategies, boost effective ones
            for strategy in self.strategies.values():
                if strategy.effectiveness() < 0.3 and strategy.times_used > 5:
                    strategy.parameters['weight'] = strategy.parameters.get('weight', 1.0) * 0.5
                elif strategy.effectiveness() > 0.7:
                    strategy.parameters['weight'] = strategy.parameters.get('weight', 1.0) * 1.2
            description = "Optimized strategy weights based on effectiveness"
            change_type = "strategy_adaptation"

        elif action == 'increase_exploration':
            # Increase exploration rate
            old_value = self.current_config.get('exploration_rate', 0.2)
            self.current_config['exploration_rate'] = min(old_value + 0.1, 0.5)
            description = f"Increased exploration rate from {old_value:.2f} to {self.current_config['exploration_rate']:.2f}"
            change_type = "parameter_tuning"

        else:
            return None

        event = EvolutionEvent(
            event_id=event_id,
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            change_type=change_type,
            description=description,
            rationale=rationale,
            before_metrics=current_metrics
        )

        self.evolution_history.append(event)

        return event

    def _adapt_strategies(self) -> List[EvolutionEvent]:
        """Adapt strategies based on their performance"""
        events = []

        for strategy in self.strategies.values():
            if strategy.times_used < 5:
                continue  # Not enough data

            # Check if strategy is underperforming
            if strategy.effectiveness() < 0.3:
                # Modify parameters
                event = self._modify_strategy_parameters(strategy, "underperforming")
                if event:
                    events.append(event)

            # Check if strategy is improving
            elif strategy.is_improving():
                # Boost this strategy
                event = self._modify_strategy_parameters(strategy, "improving")
                if event:
                    events.append(event)

        return events

    def _modify_strategy_parameters(self,
                                   strategy: AdaptiveStrategy,
                                   reason: str) -> Optional[EvolutionEvent]:
        """Modify strategy parameters"""
        self.event_count += 1
        event_id = f"evol_{self.agent_name}_{self.event_count}"

        if reason == "underperforming":
            # Reduce weight or modify parameters
            for param_name in strategy.parameters:
                if param_name == 'weight':
                    strategy.parameters[param_name] *= 0.8
                elif 'threshold' in param_name:
                    strategy.parameters[param_name] *= 0.9
                elif 'max' in param_name:
                    strategy.parameters[param_name] = int(strategy.parameters[param_name] * 0.8)

            description = f"Reduced parameters for underperforming strategy '{strategy.name}'"

        elif reason == "improving":
            # Boost weight
            strategy.parameters['weight'] = strategy.parameters.get('weight', 1.0) * 1.3

            description = f"Boosted weight for improving strategy '{strategy.name}'"

        else:
            return None

        event = EvolutionEvent(
            event_id=event_id,
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            change_type="strategy_adaptation",
            description=description,
            rationale=reason,
            before_metrics=self.performance_timeline[-1] if self.performance_timeline else None
        )

        self.evolution_history.append(event)

        return event

    def _adjust_curriculum_difficulty(self) -> Optional[EvolutionEvent]:
        """Adjust difficulty level for curriculum learning"""
        if len(self.performance_timeline) < 10:
            return None

        # Check recent performance
        recent = self.performance_timeline[-5:]
        avg_success = np.mean([p.success_rate for p in recent])

        old_difficulty = self.current_difficulty_level

        # Increase difficulty if consistently succeeding
        if avg_success > 0.8:
            self.current_difficulty_level = min(
                self.current_difficulty_level + self.difficulty_progression_rate,
                1.0
            )
            description = f"Increased curriculum difficulty from {old_difficulty:.2f} to {self.current_difficulty_level:.2f}"

        # Decrease difficulty if struggling
        elif avg_success < 0.4:
            self.current_difficulty_level = max(
                self.current_difficulty_level - self.difficulty_progression_rate,
                0.1
            )
            description = f"Decreased curriculum difficulty from {old_difficulty:.2f} to {self.current_difficulty_level:.2f}"

        else:
            return None  # No change needed

        self.event_count += 1
        event = EvolutionEvent(
            event_id=f"evol_{self.agent_name}_{self.event_count}",
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            change_type="curriculum_adjustment",
            description=description,
            rationale=f"Average success rate: {avg_success:.2f}",
            before_metrics=self.performance_timeline[-1]
        )

        self.evolution_history.append(event)

        return event

    def evaluate_evolution_effectiveness(self):
        """Evaluate if recent evolutions were effective"""
        if len(self.evolution_history) < 3:
            return

        for event in self.evolution_history[-3:]:
            if event.after_metrics is not None:
                continue  # Already evaluated

            # Find performance after this evolution
            event_time = datetime.datetime.strptime(event.timestamp, '%Y-%m-%d %H:%M:%S')

            # Get metrics from shortly after the event
            after_metrics_list = [
                m for m in self.performance_timeline
                if datetime.datetime.strptime(m.timestamp, '%Y-%m-%d %H:%M:%S') > event_time
            ]

            if len(after_metrics_list) >= 5:
                # Average of next 5 performances
                after_metrics = PerformanceMetrics(
                    success_rate=np.mean([m.success_rate for m in after_metrics_list[:5]]),
                    avg_confidence=np.mean([m.avg_confidence for m in after_metrics_list[:5]]),
                    avg_quality_score=np.mean([m.avg_quality_score for m in after_metrics_list[:5]]),
                    efficiency=np.mean([m.efficiency for m in after_metrics_list[:5]]),
                    error_rate=np.mean([m.error_rate for m in after_metrics_list[:5]]),
                    learning_rate=np.mean([m.learning_rate for m in after_metrics_list[:5]]),
                    timestamp=after_metrics_list[4].timestamp
                )

                event.after_metrics = after_metrics

                # Determine if successful
                improvement = (
                    after_metrics.success_rate > event.before_metrics.success_rate
                    or after_metrics.avg_quality_score > event.before_metrics.avg_quality_score
                )

                event.success = improvement

                # Meta-learning: learn from evolution outcomes
                self.meta_learning_history.append({
                    'event': event,
                    'improved': improvement,
                    'change_type': event.change_type,
                    'improvement_magnitude': after_metrics.success_rate - event.before_metrics.success_rate
                })

    def get_evolution_report(self) -> Dict[str, Any]:
        """Get comprehensive report on evolution"""
        if not self.performance_timeline:
            return {'status': 'no_data'}

        # Calculate overall improvement
        if len(self.performance_timeline) >= 20:
            early = self.performance_timeline[:10]
            recent = self.performance_timeline[-10:]

            early_avg = np.mean([p.success_rate for p in early])
            recent_avg = np.mean([p.success_rate for p in recent])

            overall_improvement = recent_avg - early_avg
        else:
            overall_improvement = 0.0

        # Evolution effectiveness
        successful_evolutions = sum(
            1 for e in self.evolution_history
            if e.success is True
        )
        evaluated_evolutions = sum(
            1 for e in self.evolution_history
            if e.success is not None
        )

        evolution_success_rate = (
            successful_evolutions / evaluated_evolutions
            if evaluated_evolutions > 0 else 0.0
        )

        return {
            'overall_improvement': overall_improvement,
            'total_evolution_events': len(self.evolution_history),
            'evolution_success_rate': evolution_success_rate,
            'current_difficulty_level': self.current_difficulty_level,
            'current_config': self.current_config,
            'strategy_effectiveness': {
                s.name: s.effectiveness()
                for s in self.strategies.values()
            },
            'recent_evolutions': [
                {
                    'description': e.description,
                    'rationale': e.rationale,
                    'success': e.success
                }
                for e in self.evolution_history[-5:]
            ]
        }
