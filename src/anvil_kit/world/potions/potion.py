"""`Potion`: one custom potion, its variants and brewing recipes."""

import re
from dataclasses import dataclass
from typing import Annotated

from anvil.api.actors.entity import Entity
from anvil.api.core.core import CONFIG
from anvil.api.items.components import ItemCustomComponent
from anvil.api.items.crafting import PotionMixingRecipe
from anvil.api.items.items import Item
from anvil.api.vanilla.items import MinecraftItemTypes
from anvil.lib.jsonmodel import InRange, json_field

from .projectile import add_render_controller, create_projectile
from .scaffold import write_typescript
from .variants import Drinkable, Lingering, PotionVariant, Splash

_KEY = re.compile(r"[a-z][a-z0-9_]*")
_HEX_COLOR = re.compile(r"#?([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")


@dataclass(frozen=True)
class _Recipe:
    result: PotionVariant
    reagent: Item | str
    source: PotionVariant | None


class Potion:
    """A custom potion. Add its variants and brewing recipes, then `queue()` it:

    ```python
    stasis = Potion(key="stasis", title="Stasis", color="#FFC710")
    drinkable = stasis.drinkable(duration=240)
    splash = stasis.splash(duration=240)
    stasis.brew(result=drinkable, reagent=MinecraftItemTypes.Redstone())
    stasis.brew(result=splash, reagent=MinecraftItemTypes.Gunpowder(), source=drinkable)
    items = stasis.queue()
    ```
    """

    _queued: list["Potion"] = []
    _projectile: Entity | None = None
    _effect_component: type | None = None

    def __init__(
        self,
        *,
        key: str,
        title: str,
        color: str,
    ) -> None:
        """
        Args:
            key: The effect the potion applies, registered with `effectManager` in TypeScript.
                Also names the items and textures: lowercase letters, digits and underscores.
            title: Shown in item names, like "Stasis" in "Potion of Stasis".
            color: Particle colour, like "#FF8000".
        """
        name = f"Potion {key!r}"
        if not isinstance(key, str) or not _KEY.fullmatch(key):
            raise ValueError(
                f"{name}: key must be lowercase letters, digits and underscores, "
                "starting with a letter, like 'night_vision'."
            )
        if not isinstance(color, str) or not _HEX_COLOR.fullmatch(color):
            raise ValueError(f"{name}: color must be a hex colour like '#FF8000', got {color!r}.")

        self.key = key
        self.title = title
        self.color = color
        self.variants: list[PotionVariant] = []
        self.effect_id = -1
        """Set by `queue()`: tells the potion projectile which potion it carries."""
        self._recipes: list[_Recipe] = []

    def drinkable(
        self, *, amplifier: int = 0, duration: float = 180, use_duration: float = 1.5
    ) -> Drinkable:
        """Add a potion you drink. `amplifier` counts from 0 like the game (1 is "II"),
        `duration` and `use_duration` are seconds."""
        return self._add(Drinkable(amplifier=amplifier, duration=duration, use_duration=use_duration))

    def splash(
        self, *, amplifier: int = 0, duration: float = 135, range: float = 4
    ) -> Splash:
        """Add a splash potion. `amplifier` counts from 0 like the game, `duration` is seconds,
        `range` is the radius in blocks it reaches."""
        self._check_positive("splash", range=range)
        return self._add(Splash(amplifier=amplifier, duration=duration, range=range))

    def lingering(
        self,
        *,
        amplifier: int = 0,
        duration: float = 45,
        radius: float = 3,
        lifetime: float = 30,
    ) -> Lingering:
        """Add a lingering potion. `amplifier` counts from 0 like the game, `duration` is seconds,
        `radius` is the cloud's starting radius in blocks and `lifetime` how many seconds it
        lasts if no entity shrinks it."""
        self._check_positive("lingering", radius=radius, lifetime=lifetime)
        return self._add(
            Lingering(amplifier=amplifier, duration=duration, radius=radius, lifetime=lifetime)
        )

    def brew(
        self,
        *,
        result: PotionVariant,
        reagent: Item | str,
        source: PotionVariant | None = None,
    ) -> None:
        """Brew `source` with `reagent` into `result`, both variants of this potion. Leave
        `source` out to brew from an awkward potion."""
        for role, variant in (("result", result), ("source", source)):
            if variant is not None and not any(variant is own for own in self.variants):
                raise ValueError(
                    f"Potion '{self.key}': the brewing {role} isn't one of its variants. "
                    f"Use what Potion '{self.key}'.drinkable(), .splash() or .lingering() returned."
                )
        self._recipes.append(_Recipe(result, reagent, source))

    def queue(self) -> list[Item]:
        """Make the items, projectile events and brewing recipes, and rewrite the potions'
        TypeScript in `scripts/javascript/potions`. Returns the items in the order the
        variants were added."""
        if not self.variants:
            raise ValueError(
                f"Potion '{self.key}' has no variants. Add one with .drinkable(), .splash() "
                "or .lingering() before queue()."
            )
        if any(other.key == self.key for other in Potion._queued):
            raise ValueError(f"A potion with key '{self.key}' is already queued.")

        self.effect_id = len(Potion._queued)
        projectile = Potion._get_projectile()
        effect_component = Potion._get_effect_component()

        items = []
        textures = []
        for index, variant in enumerate(self.variants):
            items.append(variant._create_item(self, index, effect_component, projectile))
            variant._setup_projectile(self, index, projectile)
            texture = f"{self.key}_{variant.potion_type}_potion"
            if texture not in textures:
                textures.append(texture)
        add_render_controller(projectile, self, textures)

        for number, recipe in enumerate(self._recipes):
            source = (
                MinecraftItemTypes.Potion("awkward")
                if recipe.source is None
                else items[self._index(recipe.source)]
            )
            brewing = PotionMixingRecipe(f"brew_{self.key}_{number}")
            brewing.unlock_items([recipe.reagent])
            brewing.recipe(source, recipe.reagent, items[self._index(recipe.result)])
            brewing.queue()

        Potion._queued.append(self)
        write_typescript(Potion._queued)
        return items

    def _check_positive(self, variant: str, **values: float) -> None:
        for field, value in values.items():
            if value <= 0:
                raise ValueError(
                    f"Potion '{self.key}': {variant}({field}=...) must be above 0, got {value!r}."
                )

    def _add[V: PotionVariant](self, variant: V) -> V:
        self.variants.append(variant)
        return variant

    def _index(self, variant: PotionVariant) -> int:
        return next(index for index, own in enumerate(self.variants) if own is variant)

    @classmethod
    def _get_projectile(cls) -> Entity:
        if Potion._projectile is None:
            Potion._projectile = create_projectile()
        return Potion._projectile

    @classmethod
    def _get_effect_component(cls) -> type:
        """The `<namespace>:potion_effect` item component every drinkable shares. Its `effect`
        names the effect drinkable.ts applies."""
        if Potion._effect_component is None:

            class PotionEffect(ItemCustomComponent):
                identifier = f"{CONFIG.NAMESPACE}:potion_effect"

                effect: str = json_field()
                amplifier: Annotated[float, InRange(0.0, 255.0)] = json_field()
                duration: float = json_field()

            Potion._effect_component = PotionEffect
        return Potion._effect_component
