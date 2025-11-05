"""
Advanced Compositing System

Perfect layer compositing with no artifacts.
"""

from PIL import Image
import numpy as np

class AdvancedCompositingSystem:
    """Professional compositing for multi-layer images."""

    def composite_layers(self, layers: list) -> Image.Image:
        """Composite multiple layers into single image."""
        if not layers:
            return Image.new('RGBA', (1024, 1024), (255, 255, 255, 0))

        # Start with base layer
        result = layers[0].copy().convert('RGBA')

        # Composite each layer
        for layer in layers[1:]:
            layer_rgba = layer.convert('RGBA')
            result = Image.alpha_composite(result, layer_rgba)

        return result
