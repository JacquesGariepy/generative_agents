"""
Inter-Agent Communication System with Theory of Mind

Implements sophisticated communication protocols between agents including:
- Theory of Mind (ToM): Modeling other agents' beliefs, desires, intentions
- Collaborative problem-solving
- Knowledge sharing and collective learning
- Conflict resolution
- Emergent communication protocols

Based on recent research on multi-agent coordination and social cognition in AI.
"""

import datetime
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import sys
sys.path.append('../../')

from global_methods import *


class MessageType(Enum):
    """Types of inter-agent messages"""
    INFORMATION_SHARING = "information_sharing"
    REQUEST_HELP = "request_help"
    OFFER_HELP = "offer_help"
    COLLABORATIVE_PLANNING = "collaborative_planning"
    KNOWLEDGE_TRANSFER = "knowledge_transfer"
    BELIEF_UPDATE = "belief_update"
    INTENTION_DECLARATION = "intention_declaration"
    QUESTION = "question"
    ANSWER = "answer"
    NEGOTIATION = "negotiation"
    CONFLICT_RESOLUTION = "conflict_resolution"


class CommunicationProtocol(Enum):
    """Communication protocols for different situations"""
    DIRECT = "direct"  # Direct one-to-one communication
    BROADCAST = "broadcast"  # One-to-many
    COLLABORATIVE = "collaborative"  # Many-to-many problem solving
    HIERARCHICAL = "hierarchical"  # Following social hierarchy
    EMERGENT = "emergent"  # Self-organizing communication


@dataclass
class Message:
    """Inter-agent message"""
    msg_id: str
    sender: str
    receiver: str  # or "ALL" for broadcast
    msg_type: MessageType
    content: str
    metadata: Dict[str, Any]
    timestamp: str
    priority: float = 0.5  # 0-1
    requires_response: bool = False
    thread_id: Optional[str] = None  # For conversation threading


@dataclass
class MentalState:
    """Model of another agent's mental state (Theory of Mind)"""
    agent_name: str
    beliefs: Dict[str, Any]  # What they likely believe
    desires: List[str]  # What they likely want
    intentions: List[str]  # What they're likely planning to do
    knowledge: Set[str]  # What knowledge they have
    personality: Dict[str, float]  # Personality traits
    current_goal: Optional[str] = None
    confidence_in_model: float = 0.5  # How confident we are in this model
    last_updated: Optional[str] = None

    def to_dict(self):
        return {
            'agent_name': self.agent_name,
            'beliefs': self.beliefs,
            'desires': self.desires,
            'intentions': self.intentions,
            'knowledge': list(self.knowledge),
            'personality': self.personality,
            'current_goal': self.current_goal,
            'confidence_in_model': self.confidence_in_model,
            'last_updated': self.last_updated
        }


@dataclass
class CollaborativeTask:
    """Task being worked on collaboratively"""
    task_id: str
    task_description: str
    participants: List[str]
    coordinator: Optional[str]
    subtasks: Dict[str, str]  # subtask_id -> assigned_agent
    shared_knowledge: Dict[str, Any]
    status: str  # "planning", "in_progress", "completed"
    created_at: str
    messages: List[Message] = field(default_factory=list)


class TheoryOfMindModule:
    """
    Theory of Mind: Model other agents' mental states.

    Allows agent to:
    - Predict others' behavior
    - Understand others' perspectives
    - Communicate more effectively
    - Coordinate better
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.mental_models: Dict[str, MentalState] = {}

    def get_or_create_model(self, other_agent: str) -> MentalState:
        """Get existing mental model or create new one"""
        if other_agent not in self.mental_models:
            self.mental_models[other_agent] = MentalState(
                agent_name=other_agent,
                beliefs={},
                desires=[],
                intentions=[],
                knowledge=set(),
                personality={
                    'friendliness': 0.5,
                    'cooperativeness': 0.5,
                    'assertiveness': 0.5,
                    'openness': 0.5
                },
                last_updated=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        return self.mental_models[other_agent]

    def update_model_from_observation(self,
                                     other_agent: str,
                                     observation: Dict[str, Any]):
        """Update mental model based on observation"""
        model = self.get_or_create_model(other_agent)

        # Update beliefs based on what they said or did
        if 'stated_belief' in observation:
            model.beliefs[observation['topic']] = observation['stated_belief']

        # Update inferred intentions
        if 'action' in observation:
            action = observation['action']
            inferred_intention = self._infer_intention_from_action(action)
            if inferred_intention and inferred_intention not in model.intentions:
                model.intentions.append(inferred_intention)

        # Update knowledge
        if 'demonstrated_knowledge' in observation:
            model.knowledge.add(observation['demonstrated_knowledge'])

        # Update personality estimates based on interaction
        if 'interaction_type' in observation:
            self._update_personality_estimate(model, observation)

        model.last_updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        model.confidence_in_model = min(model.confidence_in_model + 0.1, 1.0)

    def update_model_from_communication(self,
                                       other_agent: str,
                                       message: Message):
        """Update mental model based on communication"""
        model = self.get_or_create_model(other_agent)

        # Extract information from message
        if message.msg_type == MessageType.INTENTION_DECLARATION:
            intention = message.content
            if intention not in model.intentions:
                model.intentions.append(intention)

        elif message.msg_type == MessageType.BELIEF_UPDATE:
            # They're telling us what they believe
            topic = message.metadata.get('topic', 'general')
            model.beliefs[topic] = message.content

        elif message.msg_type == MessageType.KNOWLEDGE_TRANSFER:
            # They're sharing knowledge
            model.knowledge.add(message.content)

        elif message.msg_type == MessageType.REQUEST_HELP:
            # Infer: they likely lack knowledge or capability in this area
            topic = message.metadata.get('topic', 'unknown')
            model.beliefs[f'lacks_{topic}'] = True

        model.last_updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def predict_behavior(self, other_agent: str, situation: str) -> Dict[str, Any]:
        """Predict how another agent will behave in a situation"""
        model = self.get_or_create_model(other_agent)

        # Use mental model to predict
        prediction = {
            'most_likely_action': self._predict_action(model, situation),
            'likely_goals': model.desires[:3],
            'expected_cooperation_level': model.personality['cooperativeness'],
            'confidence': model.confidence_in_model
        }

        return prediction

    def should_communicate(self, other_agent: str, topic: str) -> Tuple[bool, str]:
        """Determine if we should communicate with other agent about topic"""
        model = self.get_or_create_model(other_agent)

        # Communicate if they likely don't know but might be interested
        if topic not in model.knowledge:
            if model.personality['openness'] > 0.5:
                return True, "They don't know and are open to learning"

        # Communicate if they're working on related goal
        if model.current_goal and topic.lower() in model.current_goal.lower():
            return True, "Relevant to their current goal"

        # Communicate if highly cooperative
        if model.personality['cooperativeness'] > 0.7:
            return True, "They are highly cooperative"

        return False, "No strong reason to communicate"

    def _infer_intention_from_action(self, action: str) -> Optional[str]:
        """Infer intention from observed action"""
        action_lower = action.lower()

        # Simple inference rules
        if 'going to' in action_lower or 'walking to' in action_lower:
            location = action_lower.split('to')[-1].strip()
            return f"intends to visit {location}"

        if 'working on' in action_lower:
            task = action_lower.split('on')[-1].strip()
            return f"intends to complete {task}"

        if 'talking to' in action_lower or 'meeting' in action_lower:
            return "intends to have social interaction"

        return None

    def _update_personality_estimate(self, model: MentalState, observation: Dict[str, Any]):
        """Update personality estimates based on interaction"""
        interaction_type = observation['interaction_type']
        learning_rate = 0.1

        if interaction_type == 'cooperative':
            model.personality['cooperativeness'] = min(
                model.personality['cooperativeness'] + learning_rate, 1.0
            )
            model.personality['friendliness'] = min(
                model.personality['friendliness'] + learning_rate, 1.0
            )

        elif interaction_type == 'competitive':
            model.personality['cooperativeness'] = max(
                model.personality['cooperativeness'] - learning_rate, 0.0
            )
            model.personality['assertiveness'] = min(
                model.personality['assertiveness'] + learning_rate, 1.0
            )

        elif interaction_type == 'helpful':
            model.personality['cooperativeness'] = min(
                model.personality['cooperativeness'] + learning_rate, 1.0
            )

    def _predict_action(self, model: MentalState, situation: str) -> str:
        """Predict likely action based on mental model"""
        # Use desires and intentions to predict
        if model.intentions:
            return f"likely to: {model.intentions[0]}"

        if model.desires:
            return f"likely to pursue: {model.desires[0]}"

        # Default based on personality
        if model.personality['cooperativeness'] > 0.6:
            return "likely to cooperate or help"

        return "uncertain - need more information"


class InterAgentCommunicationSystem:
    """
    Main communication system for inter-agent interaction.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

        # Theory of Mind module
        self.tom = TheoryOfMindModule(agent_name)

        # Message handling
        self.inbox: List[Message] = []
        self.sent_messages: List[Message] = []
        self.msg_count = 0

        # Collaborative tasks
        self.active_collaborations: Dict[str, CollaborativeTask] = {}

        # Communication history for learning
        self.communication_history: List[Dict[str, Any]] = []

        # Shared knowledge repository (accessible to all agents)
        self.shared_knowledge: Dict[str, Any] = {}

    def send_message(self,
                    receiver: str,
                    msg_type: MessageType,
                    content: str,
                    metadata: Optional[Dict[str, Any]] = None,
                    priority: float = 0.5,
                    requires_response: bool = False,
                    thread_id: Optional[str] = None) -> Message:
        """
        Send a message to another agent.

        Args:
            receiver: Target agent name or "ALL"
            msg_type: Type of message
            content: Message content
            metadata: Additional metadata
            priority: Message priority (0-1)
            requires_response: Whether response is expected
            thread_id: Conversation thread ID

        Returns:
            Created Message object
        """
        self.msg_count += 1
        msg_id = f"msg_{self.agent_name}_{self.msg_count}"

        message = Message(
            msg_id=msg_id,
            sender=self.agent_name,
            receiver=receiver,
            msg_type=msg_type,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            priority=priority,
            requires_response=requires_response,
            thread_id=thread_id
        )

        self.sent_messages.append(message)

        # Log communication
        self.communication_history.append({
            'type': 'sent',
            'message': message,
            'timestamp': message.timestamp
        })

        return message

    def receive_message(self, message: Message):
        """Receive a message from another agent"""
        self.inbox.append(message)

        # Update Theory of Mind based on message
        self.tom.update_model_from_communication(message.sender, message)

        # Log communication
        self.communication_history.append({
            'type': 'received',
            'message': message,
            'timestamp': message.timestamp
        })

    def process_inbox(self) -> List[Dict[str, Any]]:
        """
        Process messages in inbox and generate responses.

        Returns:
            List of actions to take based on messages
        """
        actions = []

        # Sort by priority
        self.inbox.sort(key=lambda m: m.priority, reverse=True)

        for message in self.inbox:
            action = self._process_message(message)
            if action:
                actions.append(action)

        # Clear inbox
        self.inbox = []

        return actions

    def _process_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """Process a single message"""
        action = {
            'message': message,
            'response': None,
            'internal_action': None
        }

        if message.msg_type == MessageType.REQUEST_HELP:
            # Decide if we should help
            should_help, reason = self._should_help(message)
            if should_help:
                action['response'] = self.send_message(
                    receiver=message.sender,
                    msg_type=MessageType.OFFER_HELP,
                    content=f"I can help with: {message.content}",
                    thread_id=message.msg_id,
                    metadata={'reason': reason}
                )
            else:
                action['response'] = self.send_message(
                    receiver=message.sender,
                    msg_type=MessageType.INFORMATION_SHARING,
                    content=f"I'm unable to help right now: {reason}",
                    thread_id=message.msg_id
                )

        elif message.msg_type == MessageType.QUESTION:
            # Answer if we know
            answer = self._answer_question(message.content)
            if answer:
                action['response'] = self.send_message(
                    receiver=message.sender,
                    msg_type=MessageType.ANSWER,
                    content=answer,
                    thread_id=message.msg_id
                )

        elif message.msg_type == MessageType.KNOWLEDGE_TRANSFER:
            # Learn from shared knowledge
            action['internal_action'] = {
                'type': 'learn',
                'knowledge': message.content
            }
            self.shared_knowledge[message.metadata.get('topic', 'general')] = message.content

        elif message.msg_type == MessageType.COLLABORATIVE_PLANNING:
            # Join collaborative task
            task_info = message.metadata.get('task')
            if task_info:
                action['internal_action'] = {
                    'type': 'join_collaboration',
                    'task': task_info
                }

        return action if (action['response'] or action['internal_action']) else None

    def _should_help(self, request_message: Message) -> Tuple[bool, str]:
        """Decide if we should help based on request"""
        requester = request_message.sender

        # Check Theory of Mind
        model = self.tom.get_or_create_model(requester)

        # Help if they're cooperative
        if model.personality['cooperativeness'] > 0.6:
            return True, "They are cooperative"

        # Help if we have relevant knowledge
        topic = request_message.metadata.get('topic', '')
        if topic in self.shared_knowledge:
            return True, "I have relevant knowledge"

        # Help with some probability for unknown agents (exploration)
        if model.confidence_in_model < 0.3:
            if np.random.random() < 0.5:
                return True, "Exploring cooperation with new agent"

        return False, "No strong reason to help"

    def _answer_question(self, question: str) -> Optional[str]:
        """Try to answer a question"""
        # Simple keyword matching with shared knowledge
        question_lower = question.lower()

        for topic, knowledge in self.shared_knowledge.items():
            if topic.lower() in question_lower:
                return str(knowledge)

        return None

    def initiate_collaboration(self,
                              task_description: str,
                              desired_participants: List[str]) -> CollaborativeTask:
        """
        Initiate a collaborative task.

        Args:
            task_description: What to collaborate on
            desired_participants: Other agents to invite

        Returns:
            CollaborativeTask object
        """
        task_id = f"collab_{self.agent_name}_{len(self.active_collaborations) + 1}"

        task = CollaborativeTask(
            task_id=task_id,
            task_description=task_description,
            participants=[self.agent_name] + desired_participants,
            coordinator=self.agent_name,
            subtasks={},
            shared_knowledge={},
            status="planning",
            created_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        self.active_collaborations[task_id] = task

        # Send invitations
        for participant in desired_participants:
            invitation = self.send_message(
                receiver=participant,
                msg_type=MessageType.COLLABORATIVE_PLANNING,
                content=f"Invitation to collaborate on: {task_description}",
                metadata={'task': task},
                requires_response=True
            )
            task.messages.append(invitation)

        return task

    def share_knowledge(self, knowledge: str, topic: str, target_agents: List[str] = None):
        """
        Share knowledge with other agents.

        Args:
            knowledge: Knowledge to share
            topic: Topic of knowledge
            target_agents: Specific agents to share with, or None for intelligent selection
        """
        if target_agents is None:
            # Use Theory of Mind to select who would benefit
            target_agents = []
            for agent_name, model in self.tom.mental_models.items():
                should_share, reason = self.tom.should_communicate(agent_name, topic)
                if should_share:
                    target_agents.append(agent_name)

        # Send knowledge to selected agents
        for agent in target_agents:
            self.send_message(
                receiver=agent,
                msg_type=MessageType.KNOWLEDGE_TRANSFER,
                content=knowledge,
                metadata={'topic': topic},
                priority=0.6
            )

    def request_help_from_experts(self, problem: str, topic: str) -> List[Message]:
        """
        Request help from agents who are likely experts in the topic.

        Args:
            problem: Problem description
            topic: Topic area

        Returns:
            List of request messages sent
        """
        requests = []

        # Identify potential experts based on mental models
        for agent_name, model in self.tom.mental_models.items():
            # Check if they have relevant knowledge
            if topic in model.knowledge or topic in model.beliefs:
                request = self.send_message(
                    receiver=agent_name,
                    msg_type=MessageType.REQUEST_HELP,
                    content=f"Need help with: {problem}",
                    metadata={'topic': topic},
                    requires_response=True,
                    priority=0.8
                )
                requests.append(request)

        return requests

    def broadcast_discovery(self, discovery: str):
        """Broadcast an important discovery to all agents"""
        self.send_message(
            receiver="ALL",
            msg_type=MessageType.INFORMATION_SHARING,
            content=discovery,
            metadata={'type': 'discovery'},
            priority=0.9
        )

    def get_communication_statistics(self) -> Dict[str, Any]:
        """Get statistics about communication patterns"""
        if not self.communication_history:
            return {
                'total_messages': 0,
                'messages_sent': 0,
                'messages_received': 0,
                'active_agents': 0
            }

        sent_count = sum(1 for entry in self.communication_history if entry['type'] == 'sent')
        received_count = sum(1 for entry in self.communication_history if entry['type'] == 'received')

        # Count unique agents communicated with
        agents_communicated = set()
        for entry in self.communication_history:
            msg = entry['message']
            if msg.sender != self.agent_name:
                agents_communicated.add(msg.sender)
            if msg.receiver != self.agent_name and msg.receiver != "ALL":
                agents_communicated.add(msg.receiver)

        # Message type distribution
        msg_type_counts = {}
        for entry in self.communication_history:
            msg_type = entry['message'].msg_type.value
            msg_type_counts[msg_type] = msg_type_counts.get(msg_type, 0) + 1

        return {
            'total_messages': len(self.communication_history),
            'messages_sent': sent_count,
            'messages_received': received_count,
            'active_agents': len(agents_communicated),
            'unique_agents_communicated_with': list(agents_communicated),
            'message_type_distribution': msg_type_counts,
            'active_collaborations': len(self.active_collaborations),
            'mental_models_maintained': len(self.tom.mental_models)
        }
