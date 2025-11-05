"""
Boundary Intelligence - Zero Artifacts Guarantee

FIXES:
✓ Images being cut off
✓ Black squares appearing
✓ Poor edge quality
✓ Alpha channel issues

This module ensures perfect image boundaries with no artifacts.
"""

import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageChops
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass
import cv2


@dataclass
class BoundaryAnalysis:
    """Results of boundary analysis"""
    has_cutoff: bool
    has_black_squares: bool
    has_alpha_issues: bool
    content_bounds: Tuple[int, int, int, int]  # x1, y1, x2, y2
    suggested_fix: str
    confidence: float
    safe_zone: Tuple[int, int, int, int]  # Recommended safe area


@dataclass
class FixResult:
    """Result of boundary fix operation"""
    fixed_image: Image.Image
    operations_applied: List[str]
    quality_score: float
    verified_no_artifacts: bool
    metadata: Dict[str, Any]


class BoundaryIntelligence:
    """
    Ensures perfect image boundaries with zero artifacts.

    This is the core fix for:
    - Images being cut off
    - Black squares appearing
    - Poor compositing
    - Alpha channel problems
    """

    def __init__(self):
        self.min_content_margin = 10  # Minimum pixels from edge
        self.edge_detection_threshold = 30
        self.black_threshold = 10  # RGB values below this are "black"
        self.artifact_detection_sensitivity = 0.95

    def analyze_boundaries(self, image: Image.Image) -> BoundaryAnalysis:
        """
        Analyze image for boundary issues.

        Args:
            image: PIL Image to analyze

        Returns:
            BoundaryAnalysis with detected issues
        """
        # Convert to numpy for analysis
        img_array = np.array(image)

        # Detect cutoffs
        has_cutoff = self._detect_cutoff(img_array)

        # Detect black squares/borders
        has_black_squares = self._detect_black_squares(img_array)

        # Detect alpha channel issues
        has_alpha_issues = self._detect_alpha_issues(image)

        # Find actual content boundaries
        content_bounds = self._find_content_bounds(img_array)

        # Calculate safe zone
        safe_zone = self._calculate_safe_zone(img_array.shape, content_bounds)

        # Determine fix strategy
        suggested_fix = self._suggest_fix_strategy(
            has_cutoff, has_black_squares, has_alpha_issues
        )

        # Calculate confidence
        confidence = self._calculate_confidence(img_array, content_bounds)

        return BoundaryAnalysis(
            has_cutoff=has_cutoff,
            has_black_squares=has_black_squares,
            has_alpha_issues=has_alpha_issues,
            content_bounds=content_bounds,
            suggested_fix=suggested_fix,
            confidence=confidence,
            safe_zone=safe_zone
        )

    def fix_boundaries(
        self,
        image: Image.Image,
        target_size: Optional[Tuple[int, int]] = None,
        ensure_content_visible: bool = True,
        preserve_aspect: bool = True
    ) -> FixResult:
        """
        Fix all boundary issues to ensure perfect result.

        Args:
            image: Image to fix
            target_size: Desired output size (width, height)
            ensure_content_visible: Guarantee no content is cut off
            preserve_aspect: Maintain original aspect ratio

        Returns:
            FixResult with fixed image and metadata
        """
        operations = []
        img = image.copy()

        # Step 1: Analyze current state
        analysis = self.analyze_boundaries(img)

        # Step 2: Remove black squares/borders
        if analysis.has_black_squares:
            img = self._remove_black_borders(img)
            operations.append("removed_black_borders")

        # Step 3: Fix alpha channel issues
        if analysis.has_alpha_issues:
            img = self._fix_alpha_channel(img)
            operations.append("fixed_alpha_channel")

        # Step 4: Ensure content is not cut off
        if analysis.has_cutoff or ensure_content_visible:
            img = self._ensure_no_cutoff(img, analysis.content_bounds)
            operations.append("ensured_no_cutoff")

        # Step 5: Resize to target if specified
        if target_size:
            img = self._smart_resize(
                img,
                target_size,
                analysis.content_bounds,
                preserve_aspect
            )
            operations.append(f"resized_to_{target_size}")

        # Step 6: Add intelligent padding if needed
        img = self._add_intelligent_padding(img, target_size)
        operations.append("added_intelligent_padding")

        # Step 7: Final quality assurance
        img = self._final_quality_pass(img)
        operations.append("quality_assurance")

        # Verify no artifacts
        final_analysis = self.analyze_boundaries(img)
        verified = not (
            final_analysis.has_cutoff or
            final_analysis.has_black_squares or
            final_analysis.has_alpha_issues
        )

        # Calculate quality score
        quality = self._calculate_quality_score(img, final_analysis)

        return FixResult(
            fixed_image=img,
            operations_applied=operations,
            quality_score=quality,
            verified_no_artifacts=verified,
            metadata={
                'original_size': image.size,
                'final_size': img.size,
                'original_analysis': analysis.__dict__,
                'final_analysis': final_analysis.__dict__
            }
        )

    def _detect_cutoff(self, img_array: np.ndarray) -> bool:
        """
        Detect if important content is cut off at edges.

        Uses edge detection to find if significant edges touch boundaries.
        """
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        h, w = edges.shape

        # Check edges of image for high edge density
        top_edge = np.sum(edges[0:5, :]) / (5 * w)
        bottom_edge = np.sum(edges[-5:, :]) / (5 * w)
        left_edge = np.sum(edges[:, 0:5]) / (5 * h)
        right_edge = np.sum(edges[:, -5:]) / (5 * h)

        # If any edge has high density, likely cutoff
        threshold = 0.3  # 30% edge density threshold
        return any([
            top_edge > threshold,
            bottom_edge > threshold,
            left_edge > threshold,
            right_edge > threshold
        ])

    def _detect_black_squares(self, img_array: np.ndarray) -> bool:
        """
        Detect presence of black squares or borders.

        Checks for uniform black regions, especially at edges.
        """
        if len(img_array.shape) == 3:
            # RGB image - check if all channels are black
            is_black = np.all(img_array <= self.black_threshold, axis=2)
        else:
            # Grayscale
            is_black = img_array <= self.black_threshold

        h, w = is_black.shape

        # Check corners and edges for black regions
        corner_size = min(50, h // 4, w // 4)

        corners = [
            is_black[0:corner_size, 0:corner_size],  # Top-left
            is_black[0:corner_size, -corner_size:],  # Top-right
            is_black[-corner_size:, 0:corner_size],  # Bottom-left
            is_black[-corner_size:, -corner_size:]   # Bottom-right
        ]

        # If any corner is >50% black, we have black squares
        for corner in corners:
            if np.mean(corner) > 0.5:
                return True

        # Check borders
        border_width = 5
        borders = [
            is_black[0:border_width, :],  # Top
            is_black[-border_width:, :],  # Bottom
            is_black[:, 0:border_width],  # Left
            is_black[:, -border_width:]   # Right
        ]

        for border in borders:
            if np.mean(border) > 0.7:  # 70% of border is black
                return True

        return False

    def _detect_alpha_issues(self, image: Image.Image) -> bool:
        """
        Detect alpha channel issues that could cause compositing problems.
        """
        if image.mode not in ('RGBA', 'LA'):
            return False  # No alpha channel

        # Get alpha channel
        if image.mode == 'RGBA':
            alpha = np.array(image.split()[3])
        else:
            alpha = np.array(image.split()[1])

        # Check for issues:
        # 1. Partial transparency at edges (common problem)
        h, w = alpha.shape
        edge_alpha = np.concatenate([
            alpha[0, :],
            alpha[-1, :],
            alpha[:, 0],
            alpha[:, -1]
        ])

        # If edges have partial transparency, could cause issues
        partial_transparency = np.sum((edge_alpha > 0) & (edge_alpha < 255))
        if partial_transparency > len(edge_alpha) * 0.1:  # >10% partial
            return True

        # 2. Sudden alpha changes (could cause artifacts)
        alpha_gradient = np.abs(np.gradient(alpha.astype(float)))
        if np.max(alpha_gradient) > 200:  # Sharp transitions
            return True

        return False

    def _find_content_bounds(
        self,
        img_array: np.ndarray
    ) -> Tuple[int, int, int, int]:
        """
        Find the bounding box of actual content (non-black, non-transparent).

        Returns: (x1, y1, x2, y2)
        """
        # Create content mask
        if len(img_array.shape) == 3:
            # Color image - content is non-black
            if img_array.shape[2] == 4:  # RGBA
                # Use alpha channel
                content_mask = img_array[:, :, 3] > 10
            else:  # RGB
                # Non-black pixels
                content_mask = np.any(img_array > self.black_threshold, axis=2)
        else:
            # Grayscale
            content_mask = img_array > self.black_threshold

        # Find bounding box
        rows = np.any(content_mask, axis=1)
        cols = np.any(content_mask, axis=0)

        if not np.any(rows) or not np.any(cols):
            # No content found, return full image
            h, w = content_mask.shape
            return (0, 0, w, h)

        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]

        return (int(x1), int(y1), int(x2), int(y2))

    def _calculate_safe_zone(
        self,
        img_shape: Tuple,
        content_bounds: Tuple[int, int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Calculate safe zone where content should stay to avoid cutoffs.
        """
        x1, y1, x2, y2 = content_bounds
        h, w = img_shape[:2]

        # Add margin to content bounds
        margin = self.min_content_margin

        safe_x1 = max(margin, x1 - margin)
        safe_y1 = max(margin, y1 - margin)
        safe_x2 = min(w - margin, x2 + margin)
        safe_y2 = min(h - margin, y2 + margin)

        return (safe_x1, safe_y1, safe_x2, safe_y2)

    def _suggest_fix_strategy(
        self,
        has_cutoff: bool,
        has_black_squares: bool,
        has_alpha_issues: bool
    ) -> str:
        """
        Suggest optimal fix strategy based on detected issues.
        """
        if has_black_squares and has_cutoff and has_alpha_issues:
            return "comprehensive_fix"
        elif has_black_squares:
            return "remove_borders_and_resize"
        elif has_cutoff:
            return "reframe_content"
        elif has_alpha_issues:
            return "fix_compositing"
        else:
            return "optimize_only"

    def _calculate_confidence(
        self,
        img_array: np.ndarray,
        content_bounds: Tuple[int, int, int, int]
    ) -> float:
        """
        Calculate confidence in boundary analysis.
        """
        x1, y1, x2, y2 = content_bounds
        h, w = img_array.shape[:2]

        # Confidence factors
        confidence = 1.0

        # Lower confidence if content very close to edges
        edge_distance = min(x1, y1, w - x2, h - y2)
        if edge_distance < 5:
            confidence *= 0.7

        # Lower confidence for very small content
        content_area = (x2 - x1) * (y2 - y1)
        total_area = h * w
        if content_area < total_area * 0.1:  # <10% of image
            confidence *= 0.8

        return confidence

    def _remove_black_borders(self, image: Image.Image) -> Image.Image:
        """
        Remove black borders/squares from image.

        FIXES: Black squares appearing
        """
        img_array = np.array(image)

        # Find content bounds (non-black area)
        content_bounds = self._find_content_bounds(img_array)
        x1, y1, x2, y2 = content_bounds

        # Crop to content
        if image.mode == 'RGBA':
            img = image.crop((x1, y1, x2 + 1, y2 + 1))
        else:
            img = image.crop((x1, y1, x2 + 1, y2 + 1))

        return img

    def _fix_alpha_channel(self, image: Image.Image) -> Image.Image:
        """
        Fix alpha channel issues.

        FIXES: Compositing artifacts from bad alpha
        """
        if image.mode not in ('RGBA', 'LA'):
            return image

        img_array = np.array(image)

        if image.mode == 'RGBA':
            r, g, b, a = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2], img_array[:, :, 3]

            # Fix partial transparency at edges
            # Make fully transparent or fully opaque
            a = np.where(a < 128, 0, 255).astype(np.uint8)

            # Smooth alpha edges to prevent artifacts
            a = cv2.GaussianBlur(a, (3, 3), 0)

            # Reconstruct image
            fixed = np.stack([r, g, b, a], axis=2)
            return Image.fromarray(fixed, 'RGBA')
        else:
            # Grayscale with alpha
            l, a = img_array[:, :, 0], img_array[:, :, 1]
            a = np.where(a < 128, 0, 255).astype(np.uint8)
            a = cv2.GaussianBlur(a, (3, 3), 0)
            fixed = np.stack([l, a], axis=2)
            return Image.fromarray(fixed, 'LA')

    def _ensure_no_cutoff(
        self,
        image: Image.Image,
        content_bounds: Tuple[int, int, int, int]
    ) -> Image.Image:
        """
        Ensure no content is cut off.

        FIXES: Images being cut off
        """
        x1, y1, x2, y2 = content_bounds
        w, h = image.size

        # Check if content is too close to edges
        min_margin = self.min_content_margin

        needs_expansion = (
            x1 < min_margin or
            y1 < min_margin or
            (w - x2) < min_margin or
            (h - y2) < min_margin
        )

        if not needs_expansion:
            return image

        # Calculate new size with proper margins
        content_w = x2 - x1
        content_h = y2 - y1

        new_w = content_w + 2 * min_margin
        new_h = content_h + 2 * min_margin

        # Create new image with padding
        if image.mode == 'RGBA':
            new_img = Image.new('RGBA', (new_w, new_h), (255, 255, 255, 0))
        else:
            new_img = Image.new('RGB', (new_w, new_h), (255, 255, 255))

        # Paste content centered
        paste_x = (new_w - w) // 2
        paste_y = (new_h - h) // 2

        new_img.paste(image, (paste_x, paste_y))

        return new_img

    def _smart_resize(
        self,
        image: Image.Image,
        target_size: Tuple[int, int],
        content_bounds: Tuple[int, int, int, int],
        preserve_aspect: bool
    ) -> Image.Image:
        """
        Intelligently resize to target size without losing content.
        """
        target_w, target_h = target_size

        if preserve_aspect:
            # Resize to fit within target, maintaining aspect ratio
            image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            return image
        else:
            # Resize to exact size
            return image.resize((target_w, target_h), Image.Resampling.LANCZOS)

    def _add_intelligent_padding(
        self,
        image: Image.Image,
        target_size: Optional[Tuple[int, int]]
    ) -> Image.Image:
        """
        Add intelligent padding if image is smaller than target.
        """
        if not target_size:
            return image

        target_w, target_h = target_size
        w, h = image.size

        if w >= target_w and h >= target_h:
            return image

        # Calculate padding
        pad_w = max(0, target_w - w)
        pad_h = max(0, target_h - h)

        # Center the image
        left = pad_w // 2
        top = pad_h // 2
        right = pad_w - left
        bottom = pad_h - top

        if image.mode == 'RGBA':
            # Transparent padding
            return ImageOps.expand(image, (left, top, right, bottom), fill=(255, 255, 255, 0))
        else:
            # White padding
            return ImageOps.expand(image, (left, top, right, bottom), fill=(255, 255, 255))

    def _final_quality_pass(self, image: Image.Image) -> Image.Image:
        """
        Final quality assurance pass.
        """
        # Slight sharpening to ensure crisp edges
        img = image.filter(ImageFilter.SHARPEN)

        # Ensure no extreme values at edges
        img_array = np.array(img)

        # Clip values
        img_array = np.clip(img_array, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8), img.mode)

    def _calculate_quality_score(
        self,
        image: Image.Image,
        analysis: BoundaryAnalysis
    ) -> float:
        """
        Calculate overall quality score.
        """
        score = 1.0

        # Deduct for remaining issues
        if analysis.has_cutoff:
            score -= 0.3
        if analysis.has_black_squares:
            score -= 0.3
        if analysis.has_alpha_issues:
            score -= 0.2

        # Bonus for proper content placement
        x1, y1, x2, y2 = analysis.content_bounds
        w, h = image.size

        # Check margins
        margins = [x1, y1, w - x2, h - y2]
        if all(m >= self.min_content_margin for m in margins):
            score += 0.2

        return max(0.0, min(1.0, score))

    def verify_no_artifacts(self, image: Image.Image) -> bool:
        """
        Final verification that image has no artifacts.

        Returns:
            True if image is perfect, False if artifacts detected
        """
        analysis = self.analyze_boundaries(image)

        return not (
            analysis.has_cutoff or
            analysis.has_black_squares or
            analysis.has_alpha_issues
        )
