"""The configuration of one potion."""

from dataclasses import dataclass

from .brewing import Brewing
from .variants import PotionVariantType


@dataclass
class PotionConfig:
    """Complete potion configuration"""

    effect_key: str
    effect_title: str
    effect_id: int
    color_hex: str
    variants: list[PotionVariantType]
    brewing: list[Brewing] | None = None
    splash_range: float = 4
    """Radius in blocks a splash potion reaches."""
    lingering_radius: float = 3
    """Starting radius in blocks of a lingering potion's cloud."""
    lingering_lifetime: float = 30
    """Seconds a lingering potion's cloud lasts, if no entity shrinks it."""

