"""
Spatial Reasoning Engine - AI-Powered Composition Analysis

Provides deep understanding of:
- Visual composition and balance
- Design hierarchy and flow
- Golden ratio and rule of thirds
- Negative space utilization
- Visual weight distribution
"""

import numpy as np
from PIL import Image
from typing import Tuple, Dict, List, Any, Optional
from dataclasses import dataclass
import cv2
from scipy import ndimage


@dataclass
class CompositionAnalysis:
    """Complete composition analysis results"""
    balance_score: float  # 0-1, how balanced the composition is
    balance_type: str  # "symmetric", "asymmetric", "radial"
    hierarchy_map: np.ndarray  # Visual importance heat map
    flow_direction: str  # "left-to-right", "top-to-bottom", "circular", etc.
    focal_points: List[Tuple[int, int]]  # (x, y) coordinates
    tension_points: List[Tuple[int, int, float]]  # (x, y, severity)
    harmony_score: float  # 0-1, overall visual harmony
    golden_ratio_alignment: float  # 0-1, alignment with golden ratio
    rule_of_thirds_alignment: float  # 0-1, alignment with rule of thirds
    negative_space_quality: float  # 0-1, effectiveness of white space
    visual_weight_distribution: Dict[str, float]  # Weight in each quadrant
    suggested_improvements: List[str]


@dataclass
class Element:
    """Visual element on canvas"""
    x: int
    y: int
    width: int
    height: int
    visual_weight: float  # 0-1, how much it attracts attention
    element_type: str  # "text", "image", "shape", "button"
    importance: float  # 0-1, hierarchical importance


class SpatialReasoningEngine:
    """
    Deep spatial intelligence for composition analysis.

    Understands:
    - Design principles (balance, hierarchy, emphasis)
    - Gestalt principles (proximity, similarity, closure)
    - Mathematical ratios (golden, Fibonacci)
    - Cultural reading patterns (F-pattern, Z-pattern)
    - Color psychology and visual weight
    """

    def __init__(self):
        # Golden ratio constant
        self.PHI = 1.618033988749895

        # Rule of thirds lines (percentage of width/height)
        self.THIRDS = [1/3, 2/3]

        # Focal point strength threshold
        self.FOCAL_STRENGTH_THRESHOLD = 0.7

    def analyze_composition(
        self,
        image: Optional[Image.Image] = None,
        elements: Optional[List[Element]] = None,
        canvas_size: Optional[Tuple[int, int]] = None
    ) -> CompositionAnalysis:
        """
        Comprehensive composition analysis.

        Can analyze either:
        - A rendered image (pixel-based analysis)
        - A list of elements (layout-based analysis)
        - Both (most comprehensive)

        Args:
            image: PIL Image of rendered canvas
            elements: List of canvas elements
            canvas_size: (width, height) if analyzing elements only

        Returns:
            CompositionAnalysis with complete assessment
        """
        if image is None and elements is None:
            raise ValueError("Must provide either image or elements")

        # Determine canvas size
        if image:
            canvas_size = image.size
        elif canvas_size is None:
            raise ValueError("Must provide canvas_size when analyzing elements only")

        width, height = canvas_size

        # Analyze balance
        balance_score, balance_type = self._analyze_balance(image, elements, canvas_size)

        # Create hierarchy map
        hierarchy_map = self._create_hierarchy_map(image, elements, canvas_size)

        # Detect flow direction
        flow_direction = self._detect_flow_direction(hierarchy_map)

        # Find focal points
        focal_points = self._find_focal_points(hierarchy_map)

        # Detect tension points
        tension_points = self._detect_tension_points(image, elements, canvas_size)

        # Calculate harmony
        harmony_score = self._calculate_harmony(image, elements, canvas_size)

        # Check golden ratio alignment
        golden_alignment = self._check_golden_ratio(focal_points, canvas_size)

        # Check rule of thirds
        thirds_alignment = self._check_rule_of_thirds(focal_points, canvas_size)

        # Analyze negative space
        negative_space_quality = self._analyze_negative_space(image, elements, canvas_size)

        # Calculate visual weight distribution
        weight_dist = self._calculate_weight_distribution(image, elements, canvas_size)

        # Generate improvement suggestions
        suggestions = self._generate_suggestions(
            balance_score, harmony_score, golden_alignment,
            thirds_alignment, negative_space_quality, weight_dist
        )

        return CompositionAnalysis(
            balance_score=balance_score,
            balance_type=balance_type,
            hierarchy_map=hierarchy_map,
            flow_direction=flow_direction,
            focal_points=focal_points,
            tension_points=tension_points,
            harmony_score=harmony_score,
            golden_ratio_alignment=golden_alignment,
            rule_of_thirds_alignment=thirds_alignment,
            negative_space_quality=negative_space_quality,
            visual_weight_distribution=weight_dist,
            suggested_improvements=suggestions
        )

    def _analyze_balance(
        self,
        image: Optional[Image.Image],
        elements: Optional[List[Element]],
        canvas_size: Tuple[int, int]
    ) -> Tuple[float, str]:
        """
        Analyze visual balance of composition.

        Returns: (balance_score, balance_type)
        """
        width, height = canvas_size

        # Calculate center of visual mass
        if elements:
            # Use element positions and weights
            total_weight = sum(e.visual_weight for e in elements)
            if total_weight == 0:
                return 0.5, "unknown"

            center_x = sum(e.x * e.visual_weight for e in elements) / total_weight
            center_y = sum(e.y * e.visual_weight for e in elements) / total_weight
        elif image:
            # Use pixel intensity as weight
            img_array = np.array(image.convert('L'))  # Grayscale
            y_coords, x_coords = np.mgrid[0:height, 0:width]

            total_weight = np.sum(img_array)
            if total_weight == 0:
                return 0.5, "unknown"

            center_x = np.sum(x_coords * img_array) / total_weight
            center_y = np.sum(y_coords * img_array) / total_weight
        else:
            return 0.5, "unknown"

        # Calculate balance score based on how close to center
        canvas_center_x = width / 2
        canvas_center_y = height / 2

        x_offset = abs(center_x - canvas_center_x) / (width / 2)
        y_offset = abs(center_y - canvas_center_y) / (height / 2)

        # Balance score: 1.0 = perfectly centered, 0.0 = extreme offset
        balance_score = 1.0 - (x_offset + y_offset) / 2

        # Determine balance type
        if x_offset < 0.1 and y_offset < 0.1:
            balance_type = "symmetric"
        elif x_offset < 0.3 and y_offset < 0.3:
            balance_type = "asymmetric_balanced"
        else:
            balance_type = "asymmetric"

        # Check for radial balance
        if self._is_radial_balance(image, elements, canvas_size):
            balance_type = "radial"
            balance_score = max(balance_score, 0.8)  # Radial is also balanced

        return balance_score, balance_type

    def _is_radial_balance(
        self,
        image: Optional[Image.Image],
        elements: Optional[List[Element]],
        canvas_size: Tuple[int, int]
    ) -> bool:
        """Check if composition has radial balance."""
        # Simplified check - would be more sophisticated in production
        if not elements:
            return False

        width, height = canvas_size
        center_x, center_y = width / 2, height / 2

        # Check if elements are evenly distributed around center
        angles = []
        for elem in elements:
            elem_center_x = elem.x + elem.width / 2
            elem_center_y = elem.y + elem.height / 2

            angle = np.arctan2(elem_center_y - center_y, elem_center_x - center_x)
            angles.append(angle)

        if len(angles) < 3:
            return False

        # Check angle distribution uniformity
        angles = sorted(angles)
        angle_diffs = [angles[i+1] - angles[i] for i in range(len(angles)-1)]

        # If angles are evenly distributed, it's radial
        std_dev = np.std(angle_diffs)
        return std_dev < 0.5  # Threshold for "even" distribution

    def _create_hierarchy_map(
        self,
        image: Optional[Image.Image],
        elements: Optional[List[Element]],
        canvas_size: Tuple[int, int]
    ) -> np.ndarray:
        """
        Create visual importance heat map.

        Higher values = more visually important
        """
        width, height = canvas_size
        hierarchy_map = np.zeros((height, width))

        if elements:
            # Use element importance
            for elem in elements:
                x1, y1 = max(0, elem.x), max(0, elem.y)
                x2 = min(width, elem.x + elem.width)
                y2 = min(height, elem.y + elem.height)

                # Add importance to map
                hierarchy_map[y1:y2, x1:x2] += elem.importance * elem.visual_weight

        if image:
            # Use saliency detection
            img_array = np.array(image.convert('RGB'))

            # Simple saliency: edge detection + contrast
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            # Contrast map
            contrast = cv2.Laplacian(gray, cv2.CV_64F)
            contrast = np.abs(contrast)

            # Combine
            saliency = (edges.astype(float) + contrast) / 2

            # Blur to create heat map
            saliency = cv2.GaussianBlur(saliency, (21, 21), 0)

            # Add to hierarchy map
            hierarchy_map += saliency

        # Normalize
        if np.max(hierarchy_map) > 0:
            hierarchy_map = hierarchy_map / np.max(hierarchy_map)

        return hierarchy_map

    def _detect_flow_direction(self, hierarchy_map: np.ndarray) -> str:
        """
        Detect natural eye flow direction.

        Common patterns:
        - F-pattern (web pages)
        - Z-pattern (posters, ads)
        - Left-to-right (Western reading)
        - Top-to-bottom (vertical)
        - Circular/spiral
        """
        h, w = hierarchy_map.shape

        # Calculate average importance by region
        top_half = np.mean(hierarchy_map[:h//2, :])
        bottom_half = np.mean(hierarchy_map[h//2:, :])
        left_half = np.mean(hierarchy_map[:, :w//2])
        right_half = np.mean(hierarchy_map[:, w//2:])

        top_left = np.mean(hierarchy_map[:h//2, :w//2])
        top_right = np.mean(hierarchy_map[:h//2, w//2:])
        bottom_left = np.mean(hierarchy_map[h//2:, :w//2])
        bottom_right = np.mean(hierarchy_map[h//2:, w//2:])

        # Detect pattern
        if top_half > bottom_half * 1.3:
            if left_half > right_half:
                return "top-left_to_bottom-right (Z-pattern)"
            else:
                return "top-to-bottom"
        elif left_half > right_half * 1.3:
            return "left-to-right"
        elif top_left > other_quadrants_avg([top_right, bottom_left, bottom_right]):
            return "clockwise-spiral"
        else:
            return "center-outward"

    def _find_focal_points(
        self,
        hierarchy_map: np.ndarray
    ) -> List[Tuple[int, int]]:
        """
        Find natural focal points (areas that attract attention).
        """
        # Find local maxima in hierarchy map
        from scipy.ndimage import maximum_filter

        # Local maximum filter
        local_max = maximum_filter(hierarchy_map, size=20)

        # Find points where value equals local maximum (peaks)
        peaks = (hierarchy_map == local_max)

        # Filter by strength
        threshold = self.FOCAL_STRENGTH_THRESHOLD * np.max(hierarchy_map)
        strong_peaks = peaks & (hierarchy_map > threshold)

        # Get coordinates
        focal_points = list(zip(*np.where(strong_peaks)))

        # Convert (y, x) to (x, y) and limit to top 5
        focal_points = [(int(x), int(y)) for y, x in focal_points[:5]]

        return focal_points

    def _detect_tension_points(
        self,
        image: Optional[Image.Image],
        elements: Optional[List[Element]],
        canvas_size: Tuple[int, int]
    ) -> List[Tuple[int, int, float]]:
        """
        Detect visual tension points (conflicts, poor spacing).

        Returns: List of (x, y, severity) tuples
        """
        tension_points = []

        if elements:
            # Check element spacing and alignment
            for i, elem1 in enumerate(elements):
                for elem2 in elements[i+1:]:
                    # Check if too close but not aligned
                    dist_x = abs(elem1.x - elem2.x)
                    dist_y = abs(elem1.y - elem2.y)

                    # Poor spacing: too close but not touching
                    if 5 < dist_x < 20 or 5 < dist_y < 20:
                        # Calculate tension severity
                        severity = 1.0 - (min(dist_x, dist_y) / 20)

                        # Position between elements
                        tension_x = (elem1.x + elem2.x) // 2
                        tension_y = (elem1.y + elem2.y) // 2

                        tension_points.append((tension_x, tension_y, severity))

        # Limit to top 10 tension points
        tension_points = sorted(tension_points, key=lambda x: x[2], reverse=True)[:10]

        return tension_points

    def _calculate_harmony(
        self,
        image: Optional[Image.Image],
        elements: Optional[List[Element]],
        canvas_size: Tuple[int, int]
    ) -> float:
        """
        Calculate overall visual harmony.

        Considers:
        - Color harmony
        - Shape harmony
        - Spacing consistency
        - Alignment
        """
        harmony_scores = []

        # Color harmony (if image available)
        if image:
            color_harmony = self._calculate_color_harmony(image)
            harmony_scores.append(color_harmony)

        # Spacing consistency (if elements available)
        if elements and len(elements) > 1:
            spacing_harmony = self._calculate_spacing_harmony(elements)
            harmony_scores.append(spacing_harmony)

        # Alignment harmony
        if elements and len(elements) > 2:
            alignment_harmony = self._calculate_alignment_harmony(elements)
            harmony_scores.append(alignment_harmony)

        if not harmony_scores:
            return 0.5  # Neutral

        return np.mean(harmony_scores)

    def _calculate_color_harmony(self, image: Image.Image) -> float:
        """Calculate color harmony score."""
        # Get dominant colors
        img_small = image.resize((100, 100))
        img_array = np.array(img_small.convert('RGB'))

        # Flatten and get unique colors
        pixels = img_array.reshape(-1, 3)

        # Calculate color variance
        # Lower variance = more harmonious (limited palette)
        color_std = np.std(pixels, axis=0)
        avg_std = np.mean(color_std)

        # Normalize: lower std = higher harmony
        # Assume std range of 0-100
        harmony = 1.0 - min(avg_std / 100, 1.0)

        return harmony

    def _calculate_spacing_harmony(self, elements: List[Element]) -> float:
        """Calculate spacing consistency."""
        # Get all horizontal and vertical gaps
        h_gaps = []
        v_gaps = []

        for i, elem1 in enumerate(elements):
            for elem2 in elements[i+1:]:
                # Horizontal gap
                if elem1.y < elem2.y + elem2.height and elem2.y < elem1.y + elem1.height:
                    # Vertically overlapping - check horizontal gap
                    if elem1.x < elem2.x:
                        gap = elem2.x - (elem1.x + elem1.width)
                        if gap > 0:
                            h_gaps.append(gap)

                # Vertical gap
                if elem1.x < elem2.x + elem2.width and elem2.x < elem1.x + elem1.width:
                    # Horizontally overlapping - check vertical gap
                    if elem1.y < elem2.y:
                        gap = elem2.y - (elem1.y + elem1.height)
                        if gap > 0:
                            v_gaps.append(gap)

        # Calculate consistency (low variance = high harmony)
        gaps = h_gaps + v_gaps
        if not gaps:
            return 0.5

        std = np.std(gaps)
        mean_gap = np.mean(gaps)

        if mean_gap == 0:
            return 0.5

        # Coefficient of variation
        cv = std / mean_gap

        # Lower CV = higher harmony
        harmony = 1.0 - min(cv, 1.0)

        return harmony

    def _calculate_alignment_harmony(self, elements: List[Element]) -> float:
        """Calculate how well elements align."""
        # Check for common alignment lines
        left_edges = [e.x for e in elements]
        right_edges = [e.x + e.width for e in elements]
        top_edges = [e.y for e in elements]
        bottom_edges = [e.y + e.height for e in elements]

        all_edges = left_edges + right_edges + top_edges + bottom_edges

        # Count alignments (edges within 5px)
        alignments = 0
        tolerance = 5

        for i, edge1 in enumerate(all_edges):
            for edge2 in all_edges[i+1:]:
                if abs(edge1 - edge2) <= tolerance:
                    alignments += 1

        # More alignments = higher harmony
        max_possible = len(all_edges) * (len(all_edges) - 1) / 2
        alignment_ratio = alignments / max_possible if max_possible > 0 else 0

        return alignment_ratio

    def _check_golden_ratio(
        self,
        focal_points: List[Tuple[int, int]],
        canvas_size: Tuple[int, int]
    ) -> float:
        """
        Check alignment with golden ratio.

        Returns: 0-1 score
        """
        width, height = canvas_size

        # Golden ratio lines
        golden_x1 = width / self.PHI
        golden_x2 = width - golden_x1
        golden_y1 = height / self.PHI
        golden_y2 = height - golden_y1

        golden_lines_x = [golden_x1, golden_x2]
        golden_lines_y = [golden_y1, golden_y2]

        # Check how many focal points align
        aligned = 0
        tolerance = min(width, height) * 0.05  # 5% tolerance

        for fx, fy in focal_points:
            # Check x alignment
            x_aligned = any(abs(fx - gx) < tolerance for gx in golden_lines_x)
            # Check y alignment
            y_aligned = any(abs(fy - gy) < tolerance for gy in golden_lines_y)

            if x_aligned or y_aligned:
                aligned += 1

        if not focal_points:
            return 0.5

        return aligned / len(focal_points)

    def _check_rule_of_thirds(
        self,
        focal_points: List[Tuple[int, int]],
        canvas_size: Tuple[int, int]
    ) -> float:
        """
        Check alignment with rule of thirds.

        Returns: 0-1 score
        """
        width, height = canvas_size

        # Rule of thirds lines
        thirds_x = [width * t for t in self.THIRDS]
        thirds_y = [height * t for t in self.THIRDS]

        # Check alignment
        aligned = 0
        tolerance = min(width, height) * 0.05  # 5% tolerance

        for fx, fy in focal_points:
            x_aligned = any(abs(fx - tx) < tolerance for tx in thirds_x)
            y_aligned = any(abs(fy - ty) < tolerance for ty in thirds_y)

            if x_aligned or y_aligned:
                aligned += 1

        if not focal_points:
            return 0.5

        return aligned / len(focal_points)

    def _analyze_negative_space(
        self,
        image: Optional[Image.Image],
        elements: Optional[List[Element]],
        canvas_size: Tuple[int, int]
    ) -> float:
        """
        Analyze quality of negative/white space.

        Returns: 0-1 score
        """
        width, height = canvas_size
        total_area = width * height

        if elements:
            # Calculate occupied area
            occupied = sum(e.width * e.height for e in elements)
            empty_ratio = 1.0 - (occupied / total_area)

            # Optimal empty space: 30-50%
            if 0.3 <= empty_ratio <= 0.5:
                quality = 1.0
            elif empty_ratio < 0.3:
                # Too crowded
                quality = empty_ratio / 0.3
            else:
                # Too sparse
                quality = 1.0 - ((empty_ratio - 0.5) / 0.5)

            return max(0.0, min(1.0, quality))

        return 0.5  # Neutral if can't determine

    def _calculate_weight_distribution(
        self,
        image: Optional[Image.Image],
        elements: Optional[List[Element]],
        canvas_size: Tuple[int, int]
    ) -> Dict[str, float]:
        """
        Calculate visual weight distribution across quadrants.
        """
        width, height = canvas_size
        mid_x, mid_y = width / 2, height / 2

        quadrants = {
            'top_left': 0.0,
            'top_right': 0.0,
            'bottom_left': 0.0,
            'bottom_right': 0.0
        }

        if elements:
            for elem in elements:
                # Determine primary quadrant
                elem_center_x = elem.x + elem.width / 2
                elem_center_y = elem.y + elem.height / 2

                weight = elem.visual_weight

                if elem_center_x < mid_x and elem_center_y < mid_y:
                    quadrants['top_left'] += weight
                elif elem_center_x >= mid_x and elem_center_y < mid_y:
                    quadrants['top_right'] += weight
                elif elem_center_x < mid_x and elem_center_y >= mid_y:
                    quadrants['bottom_left'] += weight
                else:
                    quadrants['bottom_right'] += weight

            # Normalize
            total_weight = sum(quadrants.values())
            if total_weight > 0:
                quadrants = {k: v / total_weight for k, v in quadrants.items()}

        return quadrants

    def _generate_suggestions(
        self,
        balance_score: float,
        harmony_score: float,
        golden_alignment: float,
        thirds_alignment: float,
        negative_space: float,
        weight_dist: Dict[str, float]
    ) -> List[str]:
        """Generate actionable improvement suggestions."""
        suggestions = []

        if balance_score < 0.6:
            suggestions.append("Improve visual balance - composition is off-center")

        if harmony_score < 0.6:
            suggestions.append("Increase harmony - consider more consistent spacing and colors")

        if golden_alignment < 0.3 and thirds_alignment < 0.3:
            suggestions.append("Align key elements with golden ratio or rule of thirds")

        if negative_space < 0.4:
            suggestions.append("Add more white space - composition feels crowded")
        elif negative_space > 0.7:
            suggestions.append("Reduce empty space - composition feels too sparse")

        # Check weight distribution imbalance
        weights = list(weight_dist.values())
        if max(weights) > 0.6:
            suggestions.append("Redistribute visual weight - one quadrant dominates")

        if not suggestions:
            suggestions.append("Composition looks good - minor tweaks could make it excellent")

        return suggestions


def other_quadrants_avg(quadrants: List[float]) -> float:
    """Helper to calculate average of other quadrants."""
    return np.mean(quadrants) if quadrants else 0.0
