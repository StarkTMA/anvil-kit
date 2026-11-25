"""The potion variants: drinkable, splash and lingering, each made into one item. Made with
`Potion.drinkable()`, `Potion.splash()` and `Potion.lingering()`."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

from anvil.api.actors.entity import Entity
from anvil.api.items.components import (
    ItemCustomComponent,
    ItemDisplayName,
    ItemFood,
    ItemIcon,
    ItemMaxStackSize,
    ItemProjectile,
    ItemStackedByData,
    ItemThrowable,
    ItemUseAnimation,
    ItemUseModifiers,
)
from anvil.api.items.items import Item
from anvil.api.pbr.texture_set import TextureComponents
from anvil.api.vanilla import MinecraftItemTypes
from anvil.lib.jsonmodel import InRange, json_field
from anvil.lib.jsonmodel.component import JsonCustomComponent
from anvil.lib.jsonmodel.enums import ItemCategory

if TYPE_CHECKING:
    from .potion import Potion


class PotionEffectParameters(JsonCustomComponent, abstract=True):
    """The effect a custom component applies: `id`, `amplifier` and `duration` in ticks, the
    same shape as `EffectObject` in TypeScript. Mix it into an item or block custom component
    and fill it from `PotionVariant.effect()`:

        class TrapPotionEffect(PotionEffectParameters, BlockCustomComponent):
            identifier = "trap_potion_effect"
            trap_range: float = json_field()

        TrapPotionEffect(**variant.effect(potion), trap_range=3)
    """

    id: str = json_field()
    amplifier: Annotated[int, InRange(0, 255)] = json_field()
    duration: int = json_field()


class PotionEffect(PotionEffectParameters, ItemCustomComponent):
    """The item component every drinkable shares, applied by drinkable.ts."""

    identifier = "potion_effect"


_NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")


@dataclass(kw_only=True, eq=False)
class PotionVariant:
    """One item of a potion."""

    amplifier: int = 0
    """Effect level counted from 0 like the game: 0 is "I", 1 is "II"."""
    duration: float = 180
    """Effect duration in seconds."""

    potion_type = "base"
    """Names the item and its texture: `<key>_<potion_type>_potion`."""
    potion_display = "Potion"

    def effect(self, potion: "Potion") -> dict[str, str | int]:
        """This variant's effect, ready for a `PotionEffectParameters` component:
        `{"id": "burn", "amplifier": 0, "duration": 400}`, the duration in ticks."""
        return {
            "id": potion.key,
            "amplifier": self.amplifier,
            "duration": round(self.duration * 20),
        }

    @property
    def _numeral(self) -> str:
        if 0 <= self.amplifier < len(_NUMERALS):
            return _NUMERALS[self.amplifier]
        return str(self.amplifier + 1)

    def _create_item(self, potion: "Potion", index: int, projectile: Entity) -> Item:
        minutes, seconds = divmod(int(self.duration), 60)
        title = f"{self.potion_display} of {potion.title}"
        subtitle = f"§9{potion.title} {self._numeral} ({minutes:02d}:{seconds:02d})"

        item = Item(f"{self.potion_type}_{potion.key}_potion_{index}")
        item.server.description.set_menu_category(
            ItemCategory.Equipment, is_hidden_in_commands=True
        )
        item.server.components.add(
            ItemDisplayName(value=f"{title}\\n{subtitle}"),
            ItemIcon(
                textures=TextureComponents(
                    color=f"{potion.key}_{self.potion_type}_potion"
                ),
                blockbench="potion_model",
            ),
            ItemMaxStackSize(value=1),
            ItemStackedByData(value=False),
        )
        item.queue()
        return item

    def _setup_projectile(
        self, potion: "Potion", index: int, projectile: Entity
    ) -> None:
        pass


@dataclass(kw_only=True, eq=False)
class Drinkable(PotionVariant):
    """Applies to whoever drinks it, and leaves a glass bottle."""

    use_duration: float = 1.5
    """Seconds it takes to drink."""

    def _create_item(self, potion: "Potion", index: int, projectile: Entity) -> Item:
        item = super()._create_item(potion, index, projectile)
        item.server.components.add(
            PotionEffect(**self.effect(potion)),
            ItemUseModifiers(use_duration=self.use_duration),
            ItemFood(
                can_always_eat=True,
                nutrition=0,
                saturation_modifier=0,
                using_converts_to=MinecraftItemTypes.GlassBottle(),
            ),
            ItemUseAnimation(value="drink"),
        )
        return item


@dataclass(kw_only=True, eq=False)
class _Thrown(PotionVariant):
    """Thrown as the shared potion projectile, which applies it where it lands."""

    _projectile_type = 0
    """The projectile's `type` property, read by splash.ts (1) and lingering.ts (2)."""

    def _event_name(self, potion: "Potion", index: int) -> str:
        return f"{potion.key}_{self.potion_type}_{index}"

    def _create_item(self, potion: "Potion", index: int, projectile: Entity) -> Item:
        item = super()._create_item(potion, index, projectile)
        item.server.components.add(
            ItemThrowable(),
            ItemProjectile(
                projectile_entity=f"{projectile}<{self._event_name(potion, index)}>",
                minimum_critical_power=1,
            ),
        )
        return item

    def _setup_projectile(
        self, potion: "Potion", index: int, projectile: Entity
    ) -> None:
        event = projectile.server.event(self._event_name(potion, index))
        properties = {
            "duration": round(self.duration * 20),
            "amplifier": self.amplifier,
            "type": self._projectile_type,
            "effect_id": potion.effect_id,
            **self._projectile_properties(),
        }
        for prop, value in properties.items():
            event.add_property(prop, value)

    def _projectile_properties(self) -> dict[str, float]:
        return {}


@dataclass(kw_only=True, eq=False)
class Splash(_Thrown):
    """Applies to every entity within `range` of where it lands."""

    duration: float = 135
    range: float = 4
    """Radius in blocks it reaches."""
    potion_type = "splash"
    potion_display = "Splash Potion"
    _projectile_type = 1

    def _projectile_properties(self) -> dict[str, float]:
        return {"splash_range": self.range}


@dataclass(kw_only=True, eq=False)
class Lingering(_Thrown):
    """Leaves a cloud that applies to entities walking into it."""

    duration: float = 45
    radius: float = 3
    """Starting radius in blocks of the cloud."""
    lifetime: float = 30
    """Seconds the cloud lasts, if no entity shrinks it."""
    potion_type = "lingering"
    potion_display = "Lingering Potion"
    _projectile_type = 2

    def _projectile_properties(self) -> dict[str, float]:
        return {
            "lingering_radius": self.radius,
            "lingering_lifetime": round(self.lifetime * 20),
        }
