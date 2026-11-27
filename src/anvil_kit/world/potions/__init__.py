"""Custom potions: drinkable, splash and lingering variants, brewing recipes, and the
TypeScript that applies them in game."""

from .potion import Potion
from .variants import PotionEffectParameters, PotionVariant

__all__ = ["Potion", "PotionEffectParameters", "PotionVariant"]
