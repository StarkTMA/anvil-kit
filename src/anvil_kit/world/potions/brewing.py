"""Brewing stand recipes between a potion's variants."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anvil.api.items.crafting import PotionMixingRecipe
from anvil.api.items.items import Item
from anvil.api.vanilla.items import MinecraftItemTypes

from .variants import PotionVariant

if TYPE_CHECKING:
    from .config import PotionConfig


@dataclass
class Brewing:
    """Brewing recipe: `source` plus `reagent` in a brewing stand gives `result`.

    `result` and `source` are variants from the same `PotionConfig.variants`;
    leave `source` out to brew from an awkward potion.
    """

    result: PotionVariant
    reagent: str
    source: PotionVariant | None = None



def setup_brewing(config: "PotionConfig", items: list[Item]) -> None:
    """Queue a brewing recipe for each of `config.brewing`. `items` are the items of
    `config.variants`, in the same order."""

    def item_for(variant: PotionVariant) -> Item:
        for index, candidate in enumerate(config.variants):
            if candidate is variant:
                return items[index]
        raise ValueError(
            f"Potion '{config.effect_key}' brews a variant that isn't in its variants list."
        )

    for number, recipe in enumerate(config.brewing or []):
        source = (
            MinecraftItemTypes.Potion("awkward")
            if recipe.source is None
            else item_for(recipe.source)
        )
        brewing_recipe = PotionMixingRecipe(f"brew_{config.effect_key}_{number}")
        brewing_recipe.unlock_items([recipe.reagent])
        brewing_recipe.recipe(source, recipe.reagent, item_for(recipe.result))
        brewing_recipe.queue()
