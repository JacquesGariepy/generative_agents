"""
Streaming Experience Pool - RoSE-inspired Memory Architecture

This module implements a shared experience repository where agents store and retrieve
reasoning traces. Unlike traditional memory, this pools experiences across agents,
enabling collective learning and knowledge transfer.

Key features:
- Distributed experience storage with semantic indexing
- Experience orchestration for problem-solving
- Self-improving through successful/failed trace analysis
- Cross-agent knowledge transfer

Based on: "Making Large Language Models Better Reasoners with Orchestrated
Streaming Experiences" (RoSE framework)
"""

import json
import datetime
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import sys
sys.path.append('../../')

from global_methods import *


@dataclass
class ReasoningStep:
    """Individual step in a reasoning trace"""
    step_number: int
    thought: str
    action: str
    observation: str
    confidence: float
    timestamp: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Experience:
    """
    Complete experience entry in the streaming pool.

    Attributes:
        exp_id: Unique identifier
        problem: Original problem/query
        context: Environmental and agent context
        reasoning_trace: List of reasoning steps
        solution: Final answer/outcome
        success: Whether the experience led to success
        success_metrics: Quantitative measures (accuracy, efficiency, etc.)
        agent_id: Which agent created this experience
        created_at: Timestamp
        usage_count: How many times this was retrieved
        helpful_count: How many times it actually helped
        embedding: Semantic embedding for retrieval
        keywords: For keyword-based search
        difficulty: Estimated problem difficulty
        strategy_type: Type of reasoning strategy used
    """
    exp_id: str
    problem: str
    context: Dict[str, Any]
    reasoning_trace: List[ReasoningStep]
    solution: str
    success: bool
    success_metrics: Dict[str, float]
    agent_id: str
    created_at: str
    usage_count: int = 0
    helpful_count: int = 0
    embedding: Optional[List[float]] = None
    keywords: List[str] = None
    difficulty: float = 0.5
    strategy_type: str = "default"

    def to_dict(self):
        result = asdict(self)
        result['reasoning_trace'] = [step.to_dict() for step in self.reasoning_trace]
        return result

    def effectiveness_score(self) -> float:
        """Calculate how effective this experience has been"""
        if self.usage_count == 0:
            return 0.0
        base_score = self.helpful_count / self.usage_count
        success_bonus = 0.2 if self.success else 0.0
        recency_factor = 1.0  # Could decay based on age
        return (base_score + success_bonus) * recency_factor


class StreamingExperiencePool:
    """
    Global shared pool of experiences across all agents.

    This implements the core RoSE concept: store all reasoning experiences
    in a streaming pool and orchestrate retrieval to help solve new problems.
    """

    def __init__(self, save_path: Optional[str] = None):
        """
        Initialize the experience pool.

        Args:
            save_path: Path to save/load the pool
        """
        self.experiences: Dict[str, Experience] = {}
        self.exp_count = 0

        # Indexing structures for fast retrieval
        self.keyword_index: Dict[str, List[str]] = defaultdict(list)
        self.agent_index: Dict[str, List[str]] = defaultdict(list)
        self.strategy_index: Dict[str, List[str]] = defaultdict(list)
        self.difficulty_buckets: Dict[str, List[str]] = defaultdict(list)

        # Embedding storage for semantic search
        self.embeddings: Dict[str, List[float]] = {}

        # Statistics tracking
        self.stats = {
            'total_experiences': 0,
            'successful_experiences': 0,
            'total_retrievals': 0,
            'helpful_retrievals': 0,
            'agents_contributed': set()
        }

        self.save_path = save_path
        if save_path:
            self.load(save_path)

    def add_experience(self,
                      problem: str,
                      context: Dict[str, Any],
                      reasoning_trace: List[ReasoningStep],
                      solution: str,
                      success: bool,
                      success_metrics: Dict[str, float],
                      agent_id: str,
                      keywords: Optional[List[str]] = None,
                      strategy_type: str = "default") -> Experience:
        """
        Add a new experience to the pool.

        Args:
            problem: The problem that was solved
            context: Contextual information
            reasoning_trace: Step-by-step reasoning
            solution: Final solution
            success: Whether it was successful
            success_metrics: Performance metrics
            agent_id: ID of the agent
            keywords: Optional keywords for indexing
            strategy_type: Type of strategy used

        Returns:
            The created Experience object
        """
        self.exp_count += 1
        exp_id = f"exp_{self.exp_count}_{agent_id}"

        # Generate embedding for semantic search
        embedding_key = f"{problem} {solution}"
        embedding = get_embedding(embedding_key)

        # Extract keywords if not provided
        if keywords is None:
            keywords = self._extract_keywords(problem, solution)

        # Estimate difficulty based on reasoning trace length and complexity
        difficulty = self._estimate_difficulty(reasoning_trace, success_metrics)

        experience = Experience(
            exp_id=exp_id,
            problem=problem,
            context=context,
            reasoning_trace=reasoning_trace,
            solution=solution,
            success=success,
            success_metrics=success_metrics,
            agent_id=agent_id,
            created_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            embedding=embedding,
            keywords=keywords,
            difficulty=difficulty,
            strategy_type=strategy_type
        )

        # Store experience
        self.experiences[exp_id] = experience
        self.embeddings[exp_id] = embedding

        # Update indices
        for kw in keywords:
            self.keyword_index[kw.lower()].append(exp_id)
        self.agent_index[agent_id].append(exp_id)
        self.strategy_index[strategy_type].append(exp_id)

        # Bucket by difficulty
        difficulty_bucket = self._get_difficulty_bucket(difficulty)
        self.difficulty_buckets[difficulty_bucket].append(exp_id)

        # Update statistics
        self.stats['total_experiences'] += 1
        if success:
            self.stats['successful_experiences'] += 1
        self.stats['agents_contributed'].add(agent_id)

        return experience

    def orchestrate_experiences(self,
                               current_problem: str,
                               context: Dict[str, Any],
                               agent_id: str,
                               k: int = 5,
                               diversity_weight: float = 0.3) -> List[Experience]:
        """
        Orchestrate (retrieve and rank) relevant experiences for a new problem.

        This is the core of RoSE: intelligently select past experiences
        that are most likely to help with the current problem.

        Args:
            current_problem: The problem to solve
            context: Current context
            agent_id: ID of requesting agent
            k: Number of experiences to retrieve
            diversity_weight: Balance between relevance and diversity

        Returns:
            List of orchestrated experiences
        """
        if not self.experiences:
            return []

        # Multi-strategy retrieval
        candidates = self._multi_strategy_retrieval(
            current_problem, context, agent_id
        )

        if not candidates:
            return []

        # Score each candidate
        scored_experiences = []
        current_embedding = get_embedding(current_problem)

        for exp_id in candidates:
            experience = self.experiences[exp_id]

            # Calculate relevance score
            relevance = self._calculate_relevance(
                current_embedding,
                experience.embedding,
                current_problem,
                experience.problem
            )

            # Calculate diversity score (how different from already selected)
            diversity = 1.0  # Will update in final selection

            # Calculate effectiveness score
            effectiveness = experience.effectiveness_score()

            # Combined score
            score = (
                relevance * (1 - diversity_weight) +
                diversity * diversity_weight +
                effectiveness * 0.2
            )

            scored_experiences.append((score, experience))

        # Sort by score and apply diversity
        scored_experiences.sort(reverse=True, key=lambda x: x[0])

        # Select top k with diversity
        selected = self._diversified_selection(scored_experiences, k, diversity_weight)

        # Update usage statistics
        self.stats['total_retrievals'] += len(selected)
        for exp in selected:
            exp.usage_count += 1

        return selected

    def _multi_strategy_retrieval(self,
                                 problem: str,
                                 context: Dict[str, Any],
                                 agent_id: str) -> List[str]:
        """
        Use multiple strategies to retrieve candidate experiences.

        Strategies:
        1. Semantic similarity (embedding-based)
        2. Keyword matching
        3. Same agent's past experiences
        4. Similar difficulty level
        5. Successful experiences with similar strategy
        """
        candidates = set()

        # Strategy 1: Semantic similarity
        problem_embedding = get_embedding(problem)
        semantic_candidates = self._semantic_search(problem_embedding, k=20)
        candidates.update(semantic_candidates)

        # Strategy 2: Keyword matching
        keywords = self._extract_keywords(problem, "")
        for kw in keywords:
            if kw.lower() in self.keyword_index:
                candidates.update(self.keyword_index[kw.lower()][:10])

        # Strategy 3: Same agent's past experiences (limited to recent)
        if agent_id in self.agent_index:
            candidates.update(self.agent_index[agent_id][-10:])

        # Strategy 4: Similar difficulty (estimated from problem)
        estimated_difficulty = context.get('estimated_difficulty', 0.5)
        difficulty_bucket = self._get_difficulty_bucket(estimated_difficulty)
        if difficulty_bucket in self.difficulty_buckets:
            candidates.update(self.difficulty_buckets[difficulty_bucket][:10])

        # Strategy 5: Successful experiences
        successful_exps = [
            exp_id for exp_id, exp in self.experiences.items()
            if exp.success and exp.effectiveness_score() > 0.5
        ]
        candidates.update(successful_exps[:15])

        return list(candidates)

    def _semantic_search(self, query_embedding: List[float], k: int = 10) -> List[str]:
        """Semantic similarity search using embeddings"""
        if not self.embeddings:
            return []

        similarities = []
        for exp_id, exp_embedding in self.embeddings.items():
            sim = self._cosine_similarity(query_embedding, exp_embedding)
            similarities.append((sim, exp_id))

        similarities.sort(reverse=True, key=lambda x: x[0])
        return [exp_id for _, exp_id in similarities[:k]]

    def _calculate_relevance(self,
                            current_emb: List[float],
                            exp_emb: List[float],
                            current_prob: str,
                            exp_prob: str) -> float:
        """Calculate relevance between current problem and experience"""
        # Semantic similarity
        semantic_sim = self._cosine_similarity(current_emb, exp_emb)

        # Keyword overlap
        current_kw = set(self._extract_keywords(current_prob, ""))
        exp_kw = set(self._extract_keywords(exp_prob, ""))
        if current_kw and exp_kw:
            keyword_overlap = len(current_kw & exp_kw) / len(current_kw | exp_kw)
        else:
            keyword_overlap = 0.0

        # Combine
        return 0.7 * semantic_sim + 0.3 * keyword_overlap

    def _diversified_selection(self,
                              scored_experiences: List[Tuple[float, Experience]],
                              k: int,
                              diversity_weight: float) -> List[Experience]:
        """Select k experiences with diversity consideration"""
        if len(scored_experiences) <= k:
            return [exp for _, exp in scored_experiences]

        selected = []
        remaining = scored_experiences.copy()

        # Always select the top one
        if remaining:
            selected.append(remaining[0][1])
            remaining.pop(0)

        # Select rest with diversity
        while len(selected) < k and remaining:
            best_score = -1
            best_idx = 0

            for idx, (base_score, exp) in enumerate(remaining):
                # Calculate diversity from already selected
                diversity = self._calculate_diversity(exp, selected)

                # Re-score with diversity
                final_score = (
                    base_score * (1 - diversity_weight) +
                    diversity * diversity_weight
                )

                if final_score > best_score:
                    best_score = final_score
                    best_idx = idx

            selected.append(remaining[best_idx][1])
            remaining.pop(best_idx)

        return selected

    def _calculate_diversity(self, exp: Experience, selected: List[Experience]) -> float:
        """Calculate how diverse this experience is from already selected ones"""
        if not selected:
            return 1.0

        # Check strategy diversity
        strategy_diversity = sum(
            1.0 for s in selected if s.strategy_type != exp.strategy_type
        ) / len(selected)

        # Check semantic diversity
        semantic_diversities = []
        for s in selected:
            sim = self._cosine_similarity(exp.embedding, s.embedding)
            semantic_diversities.append(1.0 - sim)  # Diversity is inverse of similarity

        avg_semantic_diversity = np.mean(semantic_diversities)

        return 0.5 * strategy_diversity + 0.5 * avg_semantic_diversity

    def report_helpfulness(self, exp_id: str, was_helpful: bool):
        """Report whether a retrieved experience was actually helpful"""
        if exp_id in self.experiences:
            if was_helpful:
                self.experiences[exp_id].helpful_count += 1
                self.stats['helpful_retrievals'] += 1

    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get statistics about the experience pool"""
        stats = self.stats.copy()
        stats['agents_contributed'] = len(stats['agents_contributed'])

        if stats['total_experiences'] > 0:
            stats['success_rate'] = (
                stats['successful_experiences'] / stats['total_experiences']
            )
        else:
            stats['success_rate'] = 0.0

        if stats['total_retrievals'] > 0:
            stats['helpfulness_rate'] = (
                stats['helpful_retrievals'] / stats['total_retrievals']
            )
        else:
            stats['helpfulness_rate'] = 0.0

        # Top performing experiences
        sorted_exps = sorted(
            self.experiences.values(),
            key=lambda x: x.effectiveness_score(),
            reverse=True
        )
        stats['top_experiences'] = [
            {
                'exp_id': exp.exp_id,
                'problem': exp.problem[:100],
                'effectiveness': exp.effectiveness_score(),
                'usage_count': exp.usage_count
            }
            for exp in sorted_exps[:5]
        ]

        return stats

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not a or not b:
            return 0.0
        a_np = np.array(a)
        b_np = np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np) + 1e-10)

    @staticmethod
    def _extract_keywords(text1: str, text2: str) -> List[str]:
        """Extract keywords from text (simple implementation)"""
        # Combine texts
        text = f"{text1} {text2}".lower()

        # Simple keyword extraction (in production, use more sophisticated NLP)
        words = text.split()

        # Filter stopwords (basic list)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                    'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                    'can', 'could', 'may', 'might', 'must', 'this', 'that', 'these', 'those'}

        keywords = [w for w in words if w not in stopwords and len(w) > 3]

        # Return unique keywords (top 10 by frequency)
        from collections import Counter
        keyword_freq = Counter(keywords)
        return [kw for kw, _ in keyword_freq.most_common(10)]

    @staticmethod
    def _estimate_difficulty(reasoning_trace: List[ReasoningStep],
                            success_metrics: Dict[str, float]) -> float:
        """Estimate difficulty of a problem based on reasoning and metrics"""
        # Factors:
        # 1. Length of reasoning trace (more steps = harder)
        # 2. Average confidence (lower confidence = harder)
        # 3. Success metrics (lower performance = harder)

        if not reasoning_trace:
            return 0.5

        trace_length_factor = min(len(reasoning_trace) / 10.0, 1.0)

        avg_confidence = np.mean([step.confidence for step in reasoning_trace])
        confidence_factor = 1.0 - avg_confidence

        # Get performance from metrics (assuming lower is harder)
        performance = success_metrics.get('accuracy', success_metrics.get('success_rate', 0.5))
        performance_factor = 1.0 - performance

        difficulty = (
            0.3 * trace_length_factor +
            0.4 * confidence_factor +
            0.3 * performance_factor
        )

        return min(max(difficulty, 0.0), 1.0)  # Clamp to [0, 1]

    @staticmethod
    def _get_difficulty_bucket(difficulty: float) -> str:
        """Get difficulty bucket name"""
        if difficulty < 0.33:
            return "easy"
        elif difficulty < 0.67:
            return "medium"
        else:
            return "hard"

    def save(self, save_path: Optional[str] = None):
        """Save the experience pool to disk"""
        path = save_path or self.save_path
        if not path:
            return

        data = {
            'experiences': {
                exp_id: exp.to_dict()
                for exp_id, exp in self.experiences.items()
            },
            'embeddings': self.embeddings,
            'stats': {
                k: v if not isinstance(v, set) else list(v)
                for k, v in self.stats.items()
            },
            'exp_count': self.exp_count
        }

        with open(f"{path}/experience_pool.json", 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, save_path: str):
        """Load the experience pool from disk"""
        try:
            with open(f"{save_path}/experience_pool.json", 'r') as f:
                data = json.load(f)

            # Rebuild experiences
            for exp_id, exp_data in data['experiences'].items():
                # Rebuild reasoning trace
                reasoning_trace = [
                    ReasoningStep(**step_data)
                    for step_data in exp_data['reasoning_trace']
                ]
                exp_data['reasoning_trace'] = reasoning_trace

                # Create experience
                exp = Experience(**exp_data)
                self.experiences[exp_id] = exp

                # Rebuild indices
                for kw in exp.keywords:
                    self.keyword_index[kw.lower()].append(exp_id)
                self.agent_index[exp.agent_id].append(exp_id)
                self.strategy_index[exp.strategy_type].append(exp_id)
                difficulty_bucket = self._get_difficulty_bucket(exp.difficulty)
                self.difficulty_buckets[difficulty_bucket].append(exp_id)

            self.embeddings = data['embeddings']
            self.exp_count = data['exp_count']

            # Rebuild stats
            self.stats = data['stats']
            if 'agents_contributed' in self.stats:
                self.stats['agents_contributed'] = set(self.stats['agents_contributed'])

        except FileNotFoundError:
            pass  # Pool doesn't exist yet


# Global singleton instance
_global_experience_pool = None

def get_global_experience_pool(save_path: Optional[str] = None) -> StreamingExperiencePool:
    """Get or create the global experience pool"""
    global _global_experience_pool
    if _global_experience_pool is None:
        _global_experience_pool = StreamingExperiencePool(save_path)
    return _global_experience_pool
