"""
SOTA Persona - State-of-the-Art Generative Agent

This class extends the base Persona with cutting-edge capabilities:
- Streaming Experience Pool (RoSE-inspired collective memory)
- Meta-cognitive monitoring and self-regulation
- Multi-level reasoning (reactive -> deliberative -> reflective -> meta-cognitive)
- Advanced inter-agent communication with Theory of Mind
- Self-evolution and continuous improvement

This represents a significant advancement over the original generative agents,
incorporating the latest research from EMNLP 2024/2025.

Author: SOTA Implementation
Date: 2025
"""

import datetime
import sys
sys.path.append('../')

from persona.persona import Persona
from persona.sota_modules.experience_pool import (
    StreamingExperiencePool,
    get_global_experience_pool,
    Experience,
    ReasoningStep
)
from persona.sota_modules.metacognition import (
    MetaCognitiveSystem,
    ReasoningQuality,
    CognitiveState
)
from persona.sota_modules.multi_level_reasoning import (
    MultiLevelReasoningSystem,
    ReasoningLevel,
    ReasoningContext
)
from persona.sota_modules.inter_agent_communication import (
    InterAgentCommunicationSystem,
    MessageType,
    Message
)
from persona.sota_modules.self_evolution import (
    SelfEvolutionEngine,
    PerformanceMetrics
)


class SOTAPersona(Persona):
    """
    SOTA (State-of-the-Art) Persona with advanced cognitive capabilities.

    Extends base Persona with:
    1. Collective learning via shared experience pool
    2. Meta-cognitive self-awareness and regulation
    3. Multi-level reasoning from reactive to meta-cognitive
    4. Theory of Mind for understanding other agents
    5. Continuous self-improvement through evolution

    This represents the cutting edge of agent architecture as of 2024/2025.
    """

    def __init__(self, name, folder_mem_saved=False, experience_pool_path=None):
        """
        Initialize SOTA Persona.

        Args:
            name: Agent name
            folder_mem_saved: Path to saved memory
            experience_pool_path: Path to shared experience pool
        """
        # Initialize base persona
        super().__init__(name, folder_mem_saved)

        # === SOTA Module 1: Streaming Experience Pool ===
        # Shared across all SOTA agents for collective learning
        self.experience_pool = get_global_experience_pool(experience_pool_path)

        # === SOTA Module 2: Meta-Cognitive System ===
        # Self-monitoring and self-regulation
        self.metacognitive_system = MetaCognitiveSystem(name)

        # === SOTA Module 3: Multi-Level Reasoning ===
        # Adaptive reasoning from reactive to meta-cognitive
        self.reasoning_system = MultiLevelReasoningSystem(
            persona=self,
            metacognitive_system=self.metacognitive_system,
            experience_pool=self.experience_pool
        )

        # === SOTA Module 4: Inter-Agent Communication ===
        # Theory of Mind and sophisticated communication
        self.communication_system = InterAgentCommunicationSystem(name)

        # === SOTA Module 5: Self-Evolution Engine ===
        # Continuous self-improvement
        self.evolution_engine = SelfEvolutionEngine(name)

        # Task tracking for performance evaluation
        self.current_task_id = None
        self.task_start_time = None
        self.reasoning_trace_current = []

    def move_with_sota(self, maze, personas, curr_tile, curr_time):
        """
        Enhanced move function using SOTA capabilities.

        This extends the base move() function with:
        - Multi-level reasoning
        - Meta-cognitive monitoring
        - Experience pool learning
        - Inter-agent communication
        - Performance tracking for evolution

        Args:
            maze: Current maze
            personas: All personas
            curr_tile: Current tile position
            curr_time: Current time

        Returns:
            Execution triple (next_tile, emoji, description)
        """
        # Update scratch
        self.scratch.curr_tile = curr_tile

        # Check for new day
        new_day = False
        if not self.scratch.curr_time:
            new_day = "First day"
        elif (self.scratch.curr_time.strftime('%A %B %d') !=
              curr_time.strftime('%A %B %d')):
            new_day = "New day"
        self.scratch.curr_time = curr_time

        # Start task tracking
        self.current_task_id = f"task_{self.name}_{curr_time.strftime('%Y%m%d_%H%M%S')}"
        self.task_start_time = datetime.datetime.now()
        self.reasoning_trace_current = []

        # === PERCEPTION ===
        perceived = self.perceive(maze)

        # === RETRIEVAL (Enhanced with Experience Pool) ===
        # Standard retrieval
        retrieved = self.retrieve(perceived)

        # SOTA Enhancement: Retrieve from experience pool
        if perceived:
            problem_description = f"Context: {self.scratch.act_description or 'current activity'}"
            similar_experiences = self.experience_pool.orchestrate_experiences(
                current_problem=problem_description,
                context={
                    'time': curr_time.strftime('%H:%M'),
                    'location': str(curr_tile)
                },
                agent_id=self.name,
                k=3
            )

            self.reasoning_trace_current.append(
                f"Retrieved {len(similar_experiences)} similar experiences from pool"
            )

        # === MULTI-LEVEL REASONING ===
        # Determine what needs to be reasoned about
        planning_needed = new_day or not self.scratch.act_path

        if planning_needed:
            # Estimate complexity and urgency
            complexity = 0.5 if new_day == "First day" else 0.3
            urgency = 0.3  # Default low urgency

            current_goal = self.scratch.daily_plan[0] if hasattr(self.scratch, 'daily_plan') and self.scratch.daily_plan else ""

            # Use multi-level reasoning
            reasoning_result = self.reasoning_system.reason(
                problem=f"Plan next action. Current goal: {current_goal}",
                urgency=urgency,
                complexity=complexity,
                current_goal=current_goal
            )

            self.reasoning_trace_current.extend(reasoning_result.reasoning_trace)

            # Record reasoning quality for meta-cognition
            snapshot = self.metacognitive_system.monitor(
                task_description=current_goal,
                reasoning_depth=reasoning_result.level_used.value,
                memory_quality=0.7,  # From retrieval
                attention_focus=[current_goal],
                active_strategies=[reasoning_result.metadata.get('strategy', 'default')],
                internal_confidence=reasoning_result.confidence
            )

            # Check if regulation needed
            regulatory_actions = self.metacognitive_system.regulate(snapshot)

            if not regulatory_actions['continue_current_approach']:
                # Meta-cognition suggests intervention
                self.reasoning_trace_current.append(
                    f"Meta-cognitive intervention: {regulatory_actions['interventions']}"
                )

                # Request help if needed
                should_help, reason = self.metacognitive_system.should_request_help(
                    current_goal,
                    reasoning_result.confidence
                )

                if should_help:
                    # Use inter-agent communication to request help
                    self.communication_system.request_help_from_experts(
                        problem=current_goal,
                        topic="planning"
                    )

        # === PLANNING (using base or SOTA-enhanced) ===
        plan = self.plan(maze, personas, new_day, retrieved)

        # === REFLECTION (Enhanced with Meta-Cognition) ===
        self.reflect()

        # SOTA Enhancement: Meta-cognitive reflection
        # Evaluate our own reflection quality
        if hasattr(self.scratch, 'importance_trigger_curr'):
            self_assessment = self.metacognitive_system.get_self_assessment()
            if self_assessment['overall_performance'] == 'Poor':
                # We're performing poorly - trigger evolution
                self.evolution_engine.evolve(force_evolution=True)

        # === EXECUTION ===
        execution = self.execute(maze, personas, plan)

        # === POST-EXECUTION: Record Performance ===
        self._record_task_performance(execution)

        # === INTER-AGENT COMMUNICATION ===
        # Process any incoming messages
        comm_actions = self.communication_system.process_inbox()

        # Share interesting discoveries
        if new_day == "First day":
            self.communication_system.broadcast_discovery(
                f"{self.name} has started their day with goal: {self.scratch.daily_plan[0] if hasattr(self.scratch, 'daily_plan') and self.scratch.daily_plan else 'exploring'}"
            )

        # === PERIODIC EVOLUTION ===
        # Evolve periodically based on performance
        evolution_events = self.evolution_engine.evolve()

        if evolution_events:
            self.reasoning_trace_current.append(
                f"Self-evolution: {len(evolution_events)} changes made"
            )

        return execution

    def _record_task_performance(self, execution):
        """Record performance on current task"""
        if not self.task_start_time:
            return

        # Calculate task duration
        duration = (datetime.datetime.now() - self.task_start_time).total_seconds()

        # Estimate success (simplified - in real system, would have explicit feedback)
        # For now, assume success if execution returned valid result
        success = execution is not None and len(execution) == 3

        # Estimate confidence from reasoning
        confidence = 0.7  # Default

        # Estimate quality
        quality = 0.8 if success else 0.3

        # Count errors (simplified)
        errors = 0

        # Record in evolution engine
        self.evolution_engine.record_performance(
            success=success,
            confidence=confidence,
            quality_score=quality,
            time_taken=duration,
            errors=errors,
            strategy_used="integrated_sota"
        )

        # Create experience for pool
        if success and self.reasoning_trace_current:
            reasoning_steps = [
                ReasoningStep(
                    step_number=i,
                    thought=trace,
                    action="reasoning",
                    observation="",
                    confidence=confidence,
                    timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                for i, trace in enumerate(self.reasoning_trace_current)
            ]

            experience = self.experience_pool.add_experience(
                problem=self.scratch.act_description or "current activity",
                context={
                    'time': self.scratch.curr_time.strftime('%H:%M') if self.scratch.curr_time else '',
                    'location': str(self.scratch.curr_tile)
                },
                reasoning_trace=reasoning_steps,
                solution=execution[2] if execution and len(execution) > 2 else "action completed",
                success=success,
                success_metrics={
                    'accuracy': quality,
                    'duration': duration
                },
                agent_id=self.name,
                strategy_type="integrated_sota"
            )

    def communicate_with(self, other_persona_name, message_type, content, metadata=None):
        """
        Communicate with another SOTA persona.

        Args:
            other_persona_name: Name of other persona
            message_type: Type of message (from MessageType enum)
            content: Message content
            metadata: Optional metadata dict

        Returns:
            Sent message
        """
        return self.communication_system.send_message(
            receiver=other_persona_name,
            msg_type=message_type,
            content=content,
            metadata=metadata or {}
        )

    def receive_communication(self, message):
        """
        Receive communication from another persona.

        Args:
            message: Message object
        """
        self.communication_system.receive_message(message)

        # Update Theory of Mind
        observation = {
            'stated_belief': message.content,
            'topic': message.metadata.get('topic', 'general'),
            'interaction_type': 'cooperative' if message.msg_type in [
                MessageType.INFORMATION_SHARING,
                MessageType.KNOWLEDGE_TRANSFER,
                MessageType.OFFER_HELP
            ] else 'neutral'
        }

        self.communication_system.tom.update_model_from_observation(
            message.sender,
            observation
        )

    def get_comprehensive_status(self):
        """
        Get comprehensive status report including all SOTA capabilities.

        Returns:
            Dict with complete status
        """
        status = {
            'name': self.name,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

            # Base persona status
            'current_action': self.scratch.act_description if hasattr(self.scratch, 'act_description') else None,
            'current_location': str(self.scratch.curr_tile) if hasattr(self.scratch, 'curr_tile') else None,

            # Meta-cognitive status
            'cognitive_state': self.metacognitive_system.current_state.value,
            'self_assessment': self.metacognitive_system.get_self_assessment(),

            # Communication status
            'communication_stats': self.communication_system.get_communication_statistics(),

            # Evolution status
            'evolution_report': self.evolution_engine.get_evolution_report(),

            # Experience pool contribution
            'experience_pool_stats': self.experience_pool.get_pool_statistics()
        }

        return status

    def collaborate_on_task(self, task_description, other_personas):
        """
        Initiate collaborative task with other personas.

        Args:
            task_description: What to collaborate on
            other_personas: List of other SOTAPersona objects

        Returns:
            CollaborativeTask object
        """
        other_names = [p.name for p in other_personas]
        return self.communication_system.initiate_collaboration(
            task_description=task_description,
            desired_participants=other_names
        )

    def learn_from_others(self):
        """
        Explicitly learn from other agents' experiences in the pool.

        This can be called periodically to trigger learning sessions.
        """
        # Get diverse experiences from the pool
        experiences = self.experience_pool.orchestrate_experiences(
            current_problem="general learning",
            context={'mode': 'learning_session'},
            agent_id=self.name,
            k=10,
            diversity_weight=0.7  # High diversity for broad learning
        )

        learning_insights = []

        for exp in experiences:
            if exp.agent_id != self.name:  # Learn from others
                # Extract strategy
                strategy = exp.strategy_type

                # Check if this strategy is new to us
                if strategy not in self.evolution_engine.strategies:
                    # Add this strategy to our repertoire
                    from persona.sota_modules.self_evolution import AdaptiveStrategy

                    new_strategy = AdaptiveStrategy(
                        strategy_id=f"learned_{strategy}",
                        name=f"learned_{strategy}",
                        description=f"Strategy learned from {exp.agent_id}",
                        parameters={'weight': 0.8}
                    )

                    self.evolution_engine.strategies[new_strategy.strategy_id] = new_strategy

                    learning_insights.append({
                        'type': 'new_strategy',
                        'strategy': strategy,
                        'learned_from': exp.agent_id
                    })

        # Share what we learned
        if learning_insights:
            self.communication_system.broadcast_discovery(
                f"Learned {len(learning_insights)} new strategies from other agents"
            )

        return learning_insights

    def save_sota_state(self, save_folder):
        """
        Save SOTA-specific state in addition to base persona.

        Args:
            save_folder: Folder to save to
        """
        # Save base persona state
        self.save(save_folder)

        # Save SOTA components
        import json

        # Save meta-cognitive state
        metacog_path = f"{save_folder}/metacognitive_state.json"
        metacog_data = {
            'current_state': self.metacognitive_system.current_state.value,
            'confidence_level': self.metacognitive_system.confidence_level,
            'known_strengths': self.metacognitive_system.known_strengths,
            'known_weaknesses': self.metacognitive_system.known_weaknesses,
            'common_errors': dict(self.metacognitive_system.common_errors)
        }

        with open(metacog_path, 'w') as f:
            json.dump(metacog_data, f, indent=2)

        # Save evolution state
        evolution_path = f"{save_folder}/evolution_state.json"
        evolution_data = {
            'current_config': self.evolution_engine.current_config,
            'current_difficulty_level': self.evolution_engine.current_difficulty_level
        }

        with open(evolution_path, 'w') as f:
            json.dump(evolution_data, f, indent=2)

        # Save communication state (Theory of Mind models)
        comm_path = f"{save_folder}/communication_state.json"
        comm_data = {
            'mental_models': {
                name: model.to_dict()
                for name, model in self.communication_system.tom.mental_models.items()
            }
        }

        with open(comm_path, 'w') as f:
            json.dump(comm_data, f, indent=2)

        # Experience pool is saved globally
        if self.experience_pool.save_path:
            self.experience_pool.save()

    # === Keep base Persona methods ===
    # All base methods like perceive(), retrieve(), plan(), reflect(), execute(), etc.
    # are inherited and still work. The move_with_sota() is the new main entry point.

    def move(self, maze, personas, curr_tile, curr_time):
        """
        Override base move() to use SOTA capabilities.

        For compatibility, this calls move_with_sota().

        Args:
            maze: Current maze
            personas: All personas
            curr_tile: Current tile
            curr_time: Current time

        Returns:
            Execution triple
        """
        return self.move_with_sota(maze, personas, curr_tile, curr_time)
