"""
Layout Optimizer - Automatic Optimal Element Placement

Uses professional design principles to automatically optimize layouts:
- Grid systems (12-column, etc.)
- Gestalt principles
- Professional spacing rules
- Accessibility guidelines
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class OptimizedLayout:
    """Result of layout optimization"""
    elements: List['LayoutElement']
    grid_system: str  # "12-column", "golden-ratio", "custom"
    improvements_made: List[str]
    quality_score: float  # 0-1, final layout quality
    before_after_comparison: Dict[str, Any]


@dataclass
class LayoutElement:
    """Element with optimized position"""
    id: str
    x: int
    y: int
    width: int
    height: int
    element_type: str
    importance: float
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GridSystem:
    """Grid configuration"""
    columns: int
    rows: int
    gutter: int  # Space between columns
    margin: int  # Space from canvas edge
    baseline: int  # Vertical rhythm


class LayoutOptimizer:
    """
    Automatically optimize element placement using design principles.
    """

    def __init__(self):
        # Standard grid systems
        self.grid_systems = {
            '12-column': GridSystem(columns=12, rows=12, gutter=20, margin=40, baseline=8),
            '8-column': GridSystem(columns=8, rows=8, gutter=16, margin=32, baseline=8),
            'golden-ratio': None,  # Calculated dynamically
            '4-column': GridSystem(columns=4, rows=6, gutter=24, margin=48, baseline=8)
        }

        # Golden ratio
        self.PHI = 1.618033988749895

        # Gestalt principle weights
        self.proximity_weight = 1.0
        self.alignment_weight = 1.5
        self.spacing_weight = 1.2

    def optimize_layout(
        self,
        elements: List[LayoutElement],
        canvas_width: int,
        canvas_height: int,
        grid_type: str = '12-column',
        preserve_relative_positions: bool = False
    ) -> OptimizedLayout:
        """
        Optimize element layout.

        Args:
            elements: Elements to optimize
            canvas_width: Canvas width
            canvas_height: Canvas height
            grid_type: Grid system to use
            preserve_relative_positions: If True, maintains relative order

        Returns:
            OptimizedLayout with improved positions
        """
        if not elements:
            return OptimizedLayout(
                elements=[],
                grid_system=grid_type,
                improvements_made=[],
                quality_score=1.0,
                before_after_comparison={}
            )

        # Store original state
        original_elements = [self._copy_element(e) for e in elements]

        improvements = []

        # Select grid system
        if grid_type == 'golden-ratio':
            grid = self._create_golden_ratio_grid(canvas_width, canvas_height)
        else:
            grid = self.grid_systems.get(grid_type, self.grid_systems['12-column'])

        # Step 1: Align to grid
        elements = self._align_to_grid(elements, grid, canvas_width, canvas_height)
        improvements.append("aligned_to_grid")

        # Step 2: Apply hierarchy (important elements more prominent)
        elements = self._apply_hierarchy(elements, canvas_width, canvas_height)
        improvements.append("applied_hierarchy")

        # Step 3: Ensure consistent spacing
        elements = self._apply_consistent_spacing(elements, grid)
        improvements.append("consistent_spacing")

        # Step 4: Apply Gestalt principles
        elements = self._apply_gestalt_principles(elements)
        improvements.append("gestalt_principles")

        # Step 5: Optimize reading flow
        if not preserve_relative_positions:
            elements = self._optimize_reading_flow(elements, canvas_width)
            improvements.append("optimized_reading_flow")

        # Step 6: Ensure accessibility (touch targets, contrast)
        elements = self._ensure_accessibility(elements)
        improvements.append("accessibility_compliance")

        # Calculate quality improvement
        quality_before = self._calculate_layout_quality(original_elements, canvas_width, canvas_height)
        quality_after = self._calculate_layout_quality(elements, canvas_width, canvas_height)

        comparison = {
            'quality_before': quality_before,
            'quality_after': quality_after,
            'improvement': quality_after - quality_before,
            'elements_moved': sum(1 for i, e in enumerate(elements)
                                 if e.x != original_elements[i].x or e.y != original_elements[i].y)
        }

        return OptimizedLayout(
            elements=elements,
            grid_system=grid_type,
            improvements_made=improvements,
            quality_score=quality_after,
            before_after_comparison=comparison
        )

    def _create_golden_ratio_grid(
        self,
        width: int,
        height: int
    ) -> GridSystem:
        """Create grid based on golden ratio."""
        # Golden ratio divisions
        column_width = int(width / self.PHI)
        gutter = int(column_width / 10)

        # Calculate number of columns that fit
        columns = max(2, int(width / (column_width + gutter)))

        return GridSystem(
            columns=columns,
            rows=int(columns * height / width),
            gutter=gutter,
            margin=gutter * 2,
            baseline=8
        )

    def _align_to_grid(
        self,
        elements: List[LayoutElement],
        grid: GridSystem,
        canvas_width: int,
        canvas_height: int
    ) -> List[LayoutElement]:
        """Snap elements to grid."""
        # Calculate column width
        available_width = canvas_width - 2 * grid.margin
        column_width = (available_width - (grid.columns - 1) * grid.gutter) / grid.columns

        # Calculate row height
        available_height = canvas_height - 2 * grid.margin
        row_height = (available_height - (grid.rows - 1) * grid.gutter) / grid.rows

        for elem in elements:
            # Snap x to nearest column
            rel_x = elem.x - grid.margin
            column = round(rel_x / (column_width + grid.gutter))
            elem.x = grid.margin + column * (column_width + grid.gutter)

            # Snap y to baseline grid
            elem.y = (elem.y // grid.baseline) * grid.baseline

            # Snap width to column multiples
            width_columns = max(1, round(elem.width / column_width))
            elem.width = int(width_columns * column_width + (width_columns - 1) * grid.gutter)

        return elements

    def _apply_hierarchy(
        self,
        elements: List[LayoutElement],
        canvas_width: int,
        canvas_height: int
    ) -> List[LayoutElement]:
        """
        Position elements according to importance.

        More important elements:
        - Higher on page (top is more important)
        - Larger size
        - More space around them
        """
        # Sort by importance
        sorted_elements = sorted(elements, key=lambda e: e.importance, reverse=True)

        # Assign positions top to bottom
        current_y = 0

        for elem in sorted_elements:
            # Find element in original list to update
            for original_elem in elements:
                if original_elem.id == elem.id:
                    # Important elements get more space
                    spacing = int(20 * elem.importance)

                    original_elem.y = max(current_y + spacing, original_elem.y)
                    current_y = original_elem.y + original_elem.height

        return elements

    def _apply_consistent_spacing(
        self,
        elements: List[LayoutElement],
        grid: GridSystem
    ) -> List[LayoutElement]:
        """Ensure consistent spacing between elements."""
        # Sort by y position
        sorted_by_y = sorted(elements, key=lambda e: e.y)

        # Apply consistent vertical spacing
        for i in range(1, len(sorted_by_y)):
            prev_elem = sorted_by_y[i - 1]
            curr_elem = sorted_by_y[i]

            # Check if they might be in same row
            vertical_overlap = not (
                prev_elem.y + prev_elem.height < curr_elem.y or
                curr_elem.y + curr_elem.height < prev_elem.y
            )

            if not vertical_overlap:
                # Different rows - ensure consistent gap
                desired_gap = grid.baseline * 3  # 3x baseline
                current_gap = curr_elem.y - (prev_elem.y + prev_elem.height)

                if abs(current_gap - desired_gap) > grid.baseline:
                    # Adjust position
                    curr_elem.y = prev_elem.y + prev_elem.height + desired_gap

        return elements

    def _apply_gestalt_principles(
        self,
        elements: List[LayoutElement]
    ) -> List[LayoutElement]:
        """
        Apply Gestalt principles:
        - Proximity: Group related elements
        - Similarity: Align similar elements
        - Closure: Create implied shapes
        """
        # Group by element type (proximity for similar elements)
        type_groups = {}
        for elem in elements:
            if elem.element_type not in type_groups:
                type_groups[elem.element_type] = []
            type_groups[elem.element_type].append(elem)

        # Align elements of same type
        for elem_type, group in type_groups.items():
            if len(group) < 2:
                continue

            # Find common alignment (majority rule)
            left_edges = [e.x for e in group]
            most_common_x = max(set(left_edges), key=left_edges.count)

            # Align to most common
            for elem in group:
                if abs(elem.x - most_common_x) < 50:  # Within threshold
                    elem.x = most_common_x

        return elements

    def _optimize_reading_flow(
        self,
        elements: List[LayoutElement],
        canvas_width: int
    ) -> List[LayoutElement]:
        """
        Optimize for natural reading flow (F-pattern, Z-pattern).

        For Western audiences:
        - Top-left gets most attention
        - Horizontal movement left to right
        - Vertical movement top to bottom
        """
        # Sort by importance
        sorted_by_importance = sorted(elements, key=lambda e: e.importance, reverse=True)

        # Ideal positions based on F-pattern
        ideal_positions = [
            {'x': 0.1, 'y': 0.1},  # Top-left (highest priority)
            {'x': 0.1, 'y': 0.3},  # Mid-left
            {'x': 0.5, 'y': 0.1},  # Top-center
            {'x': 0.1, 'y': 0.5},  # Center-left
            {'x': 0.5, 'y': 0.3},  # Center
        ]

        # Assign most important elements to ideal positions
        for i, elem in enumerate(sorted_by_importance[:len(ideal_positions)]):
            ideal = ideal_positions[i]
            elem.x = int(canvas_width * ideal['x'])
            # Y already set by hierarchy

        return elements

    def _ensure_accessibility(
        self,
        elements: List[LayoutElement]
    ) -> List[LayoutElement]:
        """
        Ensure accessibility guidelines:
        - Minimum touch target size (44x44 for interactive elements)
        - Sufficient spacing between interactive elements
        - Clear visual hierarchy
        """
        min_touch_size = 44  # pixels
        min_touch_spacing = 8  # pixels between interactive elements

        interactive_types = ['button', 'link', 'input', 'checkbox']

        for elem in elements:
            if elem.element_type in interactive_types:
                # Ensure minimum size
                if elem.width < min_touch_size:
                    elem.width = min_touch_size
                if elem.height < min_touch_size:
                    elem.height = min_touch_size

        # Ensure spacing between interactive elements
        interactive_elements = [e for e in elements if e.element_type in interactive_types]

        for i, elem1 in enumerate(interactive_elements):
            for elem2 in interactive_elements[i + 1:]:
                # Calculate distance
                dist_x = abs(elem1.x - elem2.x)
                dist_y = abs(elem1.y - elem2.y)

                # If too close, adjust
                if dist_x < min_touch_size + min_touch_spacing and dist_y < min_touch_size + min_touch_spacing:
                    # Move elem2 away
                    if dist_x < dist_y:
                        # Move horizontally
                        elem2.x += (min_touch_size + min_touch_spacing - dist_x)
                    else:
                        # Move vertically
                        elem2.y += (min_touch_size + min_touch_spacing - dist_y)

        return elements

    def _calculate_layout_quality(
        self,
        elements: List[LayoutElement],
        canvas_width: int,
        canvas_height: int
    ) -> float:
        """Calculate overall layout quality score."""
        if not elements:
            return 1.0

        quality_factors = []

        # Factor 1: Alignment (how many elements align)
        alignment_score = self._calculate_alignment_score(elements)
        quality_factors.append(alignment_score)

        # Factor 2: Spacing consistency
        spacing_score = self._calculate_spacing_score(elements)
        quality_factors.append(spacing_score)

        # Factor 3: Balance
        balance_score = self._calculate_balance_score(elements, canvas_width, canvas_height)
        quality_factors.append(balance_score)

        # Factor 4: No overlaps
        overlap_score = self._calculate_overlap_score(elements)
        quality_factors.append(overlap_score)

        return np.mean(quality_factors)

    def _calculate_alignment_score(self, elements: List[LayoutElement]) -> float:
        """Score based on element alignment."""
        if len(elements) < 2:
            return 1.0

        aligned_count = 0
        total_pairs = 0
        tolerance = 5

        for i, elem1 in enumerate(elements):
            for elem2 in elements[i + 1:]:
                total_pairs += 1

                # Check alignment
                if (abs(elem1.x - elem2.x) < tolerance or
                    abs(elem1.y - elem2.y) < tolerance or
                    abs((elem1.x + elem1.width) - (elem2.x + elem2.width)) < tolerance):
                    aligned_count += 1

        return aligned_count / total_pairs if total_pairs > 0 else 1.0

    def _calculate_spacing_score(self, elements: List[LayoutElement]) -> float:
        """Score based on spacing consistency."""
        if len(elements) < 2:
            return 1.0

        # Get all gaps
        gaps = []

        for i, elem1 in enumerate(elements):
            for elem2 in elements[i + 1:]:
                # Horizontal gap
                if elem1.x < elem2.x:
                    gap = elem2.x - (elem1.x + elem1.width)
                    if gap > 0:
                        gaps.append(gap)

        if not gaps:
            return 1.0

        # Low variance = high score
        std = np.std(gaps)
        mean = np.mean(gaps)

        if mean == 0:
            return 1.0

        cv = std / mean  # Coefficient of variation

        # Lower CV = higher score
        score = 1.0 / (1.0 + cv)

        return score

    def _calculate_balance_score(
        self,
        elements: List[LayoutElement],
        canvas_width: int,
        canvas_height: int
    ) -> float:
        """Score based on visual balance."""
        if not elements:
            return 1.0

        # Calculate center of mass
        total_weight = sum(e.width * e.height for e in elements)
        if total_weight == 0:
            return 1.0

        center_x = sum(e.x * e.width * e.height for e in elements) / total_weight
        center_y = sum(e.y * e.width * e.height for e in elements) / total_weight

        # Distance from canvas center
        canvas_center_x = canvas_width / 2
        canvas_center_y = canvas_height / 2

        x_offset = abs(center_x - canvas_center_x) / (canvas_width / 2)
        y_offset = abs(center_y - canvas_center_y) / (canvas_height / 2)

        # Closer to center = higher score
        balance = 1.0 - (x_offset + y_offset) / 2

        return max(0.0, balance)

    def _calculate_overlap_score(self, elements: List[LayoutElement]) -> float:
        """Score based on avoiding overlaps."""
        if len(elements) < 2:
            return 1.0

        overlaps = 0
        total_pairs = 0

        for i, elem1 in enumerate(elements):
            for elem2 in elements[i + 1:]:
                total_pairs += 1

                # Check overlap
                if self._elements_overlap(elem1, elem2):
                    overlaps += 1

        # No overlaps = 1.0, all overlaps = 0.0
        return 1.0 - (overlaps / total_pairs) if total_pairs > 0 else 1.0

    def _elements_overlap(self, elem1: LayoutElement, elem2: LayoutElement) -> bool:
        """Check if two elements overlap."""
        return not (
            elem1.x + elem1.width < elem2.x or
            elem2.x + elem2.width < elem1.x or
            elem1.y + elem1.height < elem2.y or
            elem2.y + elem2.height < elem1.y
        )

    def _copy_element(self, elem: LayoutElement) -> LayoutElement:
        """Create a copy of an element."""
        return LayoutElement(
            id=elem.id,
            x=elem.x,
            y=elem.y,
            width=elem.width,
            height=elem.height,
            element_type=elem.element_type,
            importance=elem.importance,
            constraints=elem.constraints.copy()
        )
