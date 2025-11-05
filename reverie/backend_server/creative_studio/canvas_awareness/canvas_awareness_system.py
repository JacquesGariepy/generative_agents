"""
Canvas Awareness System - Main Integration Module

Combines:
- Spatial Reasoning Engine
- Boundary Intelligence
- Layout Optimizer

Provides complete canvas understanding and optimization.
"""

from typing import Optional, List, Tuple, Dict, Any
from PIL import Image
from dataclasses import dataclass

from .spatial_reasoning import SpatialReasoningEngine, CompositionAnalysis, Element
from .boundary_intelligence import BoundaryIntelligence, BoundaryAnalysis, FixResult
from .layout_optimizer import LayoutOptimizer, LayoutElement, OptimizedLayout


@dataclass
class CanvasState:
    """Complete canvas state and analysis"""
    canvas_size: Tuple[int, int]
    image: Optional[Image.Image]
    elements: List[LayoutElement]
    composition_analysis: Optional[CompositionAnalysis]
    boundary_analysis: Optional[BoundaryAnalysis]
    quality_score: float
    suggestions: List[str]


class CanvasAwarenessSystem:
    """
    Main canvas awareness system.

    Provides:
    - Perfect canvas consciousness
    - Automatic problem detection and fixing
    - Intelligent layout optimization
    - Professional composition analysis
    """

    def __init__(self):
        self.spatial_reasoning = SpatialReasoningEngine()
        self.boundary_intelligence = BoundaryIntelligence()
        self.layout_optimizer = LayoutOptimizer()

    def analyze_canvas(
        self,
        image: Optional[Image.Image] = None,
        elements: Optional[List[LayoutElement]] = None,
        canvas_size: Optional[Tuple[int, int]] = None
    ) -> CanvasState:
        """
        Complete canvas analysis.

        Args:
            image: Rendered canvas image
            elements: List of canvas elements
            canvas_size: Canvas dimensions

        Returns:
            CanvasState with full analysis
        """
        # Determine canvas size
        if image:
            canvas_size = image.size
        elif canvas_size is None and elements:
            # Infer from elements
            max_x = max((e.x + e.width) for e in elements)
            max_y = max((e.y + e.height) for e in elements)
            canvas_size = (max_x + 100, max_y + 100)  # Add padding
        elif canvas_size is None:
            raise ValueError("Must provide either image, canvas_size, or elements")

        # Composition analysis
        composition_analysis = None
        if image or elements:
            # Convert LayoutElements to Elements for spatial reasoning
            spatial_elements = self._convert_to_spatial_elements(elements) if elements else None

            composition_analysis = self.spatial_reasoning.analyze_composition(
                image=image,
                elements=spatial_elements,
                canvas_size=canvas_size
            )

        # Boundary analysis
        boundary_analysis = None
        if image:
            boundary_analysis = self.boundary_intelligence.analyze_boundaries(image)

        # Calculate overall quality
        quality_score = self._calculate_overall_quality(
            composition_analysis,
            boundary_analysis
        )

        # Collect all suggestions
        suggestions = []
        if composition_analysis:
            suggestions.extend(composition_analysis.suggested_improvements)
        if boundary_analysis and boundary_analysis.suggested_fix != "optimize_only":
            suggestions.append(f"Fix boundaries: {boundary_analysis.suggested_fix}")

        return CanvasState(
            canvas_size=canvas_size,
            image=image,
            elements=elements or [],
            composition_analysis=composition_analysis,
            boundary_analysis=boundary_analysis,
            quality_score=quality_score,
            suggestions=suggestions
        )

    def fix_all_issues(
        self,
        image: Image.Image,
        target_size: Optional[Tuple[int, int]] = None
    ) -> FixResult:
        """
        Automatically fix all detected issues.

        FIXES:
        - Images being cut off ✓
        - Black squares ✓
        - Alpha channel issues ✓
        - Poor composition (through optimization) ✓

        Args:
            image: Image to fix
            target_size: Optional target size

        Returns:
            FixResult with perfect image
        """
        return self.boundary_intelligence.fix_boundaries(
            image=image,
            target_size=target_size,
            ensure_content_visible=True,
            preserve_aspect=True
        )

    def optimize_layout(
        self,
        elements: List[LayoutElement],
        canvas_width: int,
        canvas_height: int,
        grid_type: str = '12-column'
    ) -> OptimizedLayout:
        """
        Optimize element layout using professional design principles.

        Args:
            elements: Elements to optimize
            canvas_width: Canvas width
            canvas_height: Canvas height
            grid_type: Grid system to use

        Returns:
            OptimizedLayout with improved positions
        """
        return self.layout_optimizer.optimize_layout(
            elements=elements,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            grid_type=grid_type
        )

    def suggest_layout(
        self,
        intent: Dict[str, Any],
        canvas_size: Tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Suggest optimal layout based on intent.

        Args:
            intent: User intent (from Intent Understanding Module)
            canvas_size: Canvas dimensions

        Returns:
            Layout suggestion with grid, positions, etc.
        """
        width, height = canvas_size

        # Determine appropriate grid based on intent
        goal = intent.get('primary_goal', '')
        style = intent.get('style_preference', 'balanced')

        if 'ad' in goal.lower() or 'marketing' in goal.lower():
            # Ads: Rule of thirds, clear focal point
            grid_type = 'golden-ratio'
            focal_position = (width // 3, height // 3)  # Rule of thirds intersection
        elif 'presentation' in goal.lower():
            # Presentations: 12-column grid, hierarchical
            grid_type = '12-column'
            focal_position = (width // 2, height // 4)  # Top center
        elif 'social' in goal.lower() or 'instagram' in goal.lower():
            # Social media: Center-focused
            grid_type = '4-column'
            focal_position = (width // 2, height // 2)  # Center
        else:
            # Default: 12-column
            grid_type = '12-column'
            focal_position = (width // 3, height // 3)

        return {
            'grid_type': grid_type,
            'focal_position': focal_position,
            'suggested_margins': self._calculate_margins(width, height),
            'reading_flow': self._suggest_reading_flow(goal),
            'visual_hierarchy': self._suggest_hierarchy(intent)
        }

    def verify_quality(
        self,
        image: Image.Image,
        quality_threshold: float = 0.85
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify image quality meets standards.

        Args:
            image: Image to verify
            quality_threshold: Minimum acceptable quality (0-1)

        Returns:
            (passes, details) tuple
        """
        # Analyze
        state = self.analyze_canvas(image=image)

        # Check if passes
        passes = state.quality_score >= quality_threshold

        details = {
            'quality_score': state.quality_score,
            'threshold': quality_threshold,
            'passes': passes,
            'issues_found': [],
            'suggestions': state.suggestions
        }

        # List specific issues
        if state.boundary_analysis:
            if state.boundary_analysis.has_cutoff:
                details['issues_found'].append('content_cutoff')
            if state.boundary_analysis.has_black_squares:
                details['issues_found'].append('black_squares')
            if state.boundary_analysis.has_alpha_issues:
                details['issues_found'].append('alpha_issues')

        if state.composition_analysis:
            if state.composition_analysis.balance_score < 0.6:
                details['issues_found'].append('poor_balance')
            if state.composition_analysis.harmony_score < 0.6:
                details['issues_found'].append('low_harmony')

        return passes, details

    def _convert_to_spatial_elements(
        self,
        layout_elements: List[LayoutElement]
    ) -> List[Element]:
        """Convert LayoutElements to Elements for spatial reasoning."""
        return [
            Element(
                x=elem.x,
                y=elem.y,
                width=elem.width,
                height=elem.height,
                visual_weight=elem.importance,
                element_type=elem.element_type,
                importance=elem.importance
            )
            for elem in layout_elements
        ]

    def _calculate_overall_quality(
        self,
        composition: Optional[CompositionAnalysis],
        boundary: Optional[BoundaryAnalysis]
    ) -> float:
        """Calculate overall canvas quality."""
        scores = []

        if composition:
            scores.extend([
                composition.balance_score,
                composition.harmony_score,
                composition.negative_space_quality,
                (composition.golden_ratio_alignment + composition.rule_of_thirds_alignment) / 2
            ])

        if boundary:
            # Perfect boundaries = 1.0, issues = penalties
            boundary_score = 1.0
            if boundary.has_cutoff:
                boundary_score -= 0.4
            if boundary.has_black_squares:
                boundary_score -= 0.3
            if boundary.has_alpha_issues:
                boundary_score -= 0.2

            scores.append(max(0.0, boundary_score))

        if not scores:
            return 0.5  # Neutral

        return sum(scores) / len(scores)

    def _calculate_margins(
        self,
        width: int,
        height: int
    ) -> Dict[str, int]:
        """Calculate recommended margins."""
        # Responsive margins: 5-10% of width
        base_margin = int(width * 0.06)

        return {
            'top': base_margin,
            'right': base_margin,
            'bottom': int(base_margin * 1.2),  # Slightly larger bottom
            'left': base_margin
        }

    def _suggest_reading_flow(self, goal: str) -> str:
        """Suggest reading flow pattern based on goal."""
        goal_lower = goal.lower()

        if 'ad' in goal_lower or 'poster' in goal_lower:
            return "Z-pattern"  # Top-left → top-right → bottom-left → bottom-right
        elif 'article' in goal_lower or 'blog' in goal_lower:
            return "F-pattern"  # Top → left side → middle → left side
        elif 'landing' in goal_lower or 'hero' in goal_lower:
            return "center-outward"  # Center focal point, expand outward
        else:
            return "left-to-right-top-to-bottom"  # Natural reading

    def _suggest_hierarchy(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest visual hierarchy levels."""
        goal = intent.get('primary_goal', '')

        if 'ad' in goal.lower():
            return [
                {'level': 1, 'element': 'headline', 'size_multiplier': 2.5, 'weight': 'bold'},
                {'level': 2, 'element': 'product_image', 'size_multiplier': 2.0, 'weight': 'normal'},
                {'level': 3, 'element': 'cta_button', 'size_multiplier': 1.5, 'weight': 'bold'},
                {'level': 4, 'element': 'body_text', 'size_multiplier': 1.0, 'weight': 'normal'},
                {'level': 5, 'element': 'disclaimer', 'size_multiplier': 0.8, 'weight': 'light'}
            ]
        else:
            return [
                {'level': 1, 'element': 'title', 'size_multiplier': 2.0, 'weight': 'bold'},
                {'level': 2, 'element': 'subtitle', 'size_multiplier': 1.5, 'weight': 'normal'},
                {'level': 3, 'element': 'content', 'size_multiplier': 1.0, 'weight': 'normal'},
                {'level': 4, 'element': 'metadata', 'size_multiplier': 0.9, 'weight': 'light'}
            ]

    def get_canvas_insights(self, state: CanvasState) -> Dict[str, Any]:
        """
        Get actionable insights about canvas state.

        Args:
            state: Canvas state from analyze_canvas()

        Returns:
            Dictionary of insights and recommendations
        """
        insights = {
            'overall_quality': state.quality_score,
            'quality_rating': self._quality_rating(state.quality_score),
            'strengths': [],
            'weaknesses': [],
            'priority_fixes': [],
            'optional_improvements': []
        }

        if state.composition_analysis:
            comp = state.composition_analysis

            # Strengths
            if comp.balance_score > 0.8:
                insights['strengths'].append('Excellent visual balance')
            if comp.harmony_score > 0.8:
                insights['strengths'].append('Strong visual harmony')
            if comp.golden_ratio_alignment > 0.7:
                insights['strengths'].append('Good use of golden ratio')

            # Weaknesses
            if comp.balance_score < 0.5:
                insights['weaknesses'].append('Poor visual balance')
                insights['priority_fixes'].append('Rebalance composition')
            if comp.harmony_score < 0.5:
                insights['weaknesses'].append('Inconsistent visual harmony')
                insights['priority_fixes'].append('Improve spacing and alignment')

        if state.boundary_analysis:
            bound = state.boundary_analysis

            # Critical issues
            if bound.has_cutoff:
                insights['weaknesses'].append('Content is cut off')
                insights['priority_fixes'].append('Fix content boundaries')
            if bound.has_black_squares:
                insights['weaknesses'].append('Black squares/borders present')
                insights['priority_fixes'].append('Remove black borders')

        # Optional improvements from suggestions
        insights['optional_improvements'] = state.suggestions

        return insights

    def _quality_rating(self, score: float) -> str:
        """Convert quality score to rating."""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.75:
            return "Good"
        elif score >= 0.6:
            return "Fair"
        elif score >= 0.4:
            return "Needs Improvement"
        else:
            return "Poor"
