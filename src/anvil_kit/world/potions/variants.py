"""The potion variants: drinkable, splash, lingering and tick potions, each made into one item."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anvil.api.actors.entity import Entity
from anvil.api.items.components import (
    ItemBlockPlacer,
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
from anvil.api.vanilla.items import MinecraftItemTypes
from anvil.lib.jsonmodel.enums import ItemCategory
from anvil.lib.jsonmodel.types import Vector3D

if TYPE_CHECKING:
    from .config import PotionConfig

_duration_cache: dict[int, str] = {}

_NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")


def _format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds not in _duration_cache:
        minutes, remainder = divmod(int(seconds), 60)
        _duration_cache[seconds] = f"{minutes:02d}:{remainder:02d}"
    return _duration_cache[seconds]



@dataclass(kw_only=True)
class PotionVariant:
    """Base class for all potion variants with common functionality."""

    amplifier: int = 0
    duration: int = 180
    icon_suffix: str = ""
    potion_type: str = "base"
    potion_display: str = "Potion"

    @property
    def _numeral(self) -> str:
        return (
            _NUMERALS[self.amplifier]
            if 0 <= self.amplifier < len(_NUMERALS)
            else str(self.amplifier + 1)
        )

    def _create_item(
        self, config: "PotionConfig", index: int, effect_component, projectile: Entity
    ) -> Item:
        """Create the item for this variant."""

        duration_display = _format_duration(self.duration)

        title = f"{self.potion_display} of {config.effect_title}"
        subtitle = f"§9{config.effect_title} {self._numeral} ({duration_display})"
        display_name = f"{title}\\n{subtitle}"
        icon_name = f"{config.effect_key}_{self.potion_type}_potion"

        item = Item(f"{self.potion_type}_{config.effect_key}_potion_{index}")
        item.server.description.set_menu_category(
            ItemCategory.Equipment, is_hidden_in_commands=True
        )

        components = [
            ItemDisplayName(value=display_name),
            ItemIcon(
                textures=TextureComponents(color=icon_name), blockbench="potion_model"
            ),
            ItemMaxStackSize(value=1),
            ItemStackedByData(value=False),
        ]

        item.server.components.add(*components)
        item.queue()
        return item

    def _setup_projectile(
        self, config: "PotionConfig", index: int, projectile: Entity
    ) -> None:
        """Setup projectile configuration for this variant - override in subclasses."""
        pass


@dataclass(kw_only=True)
class Drinkable(PotionVariant):
    """Drinkable potion variant."""

    use_duration: float = 1.5
    potion_type: str = "base"
    potion_display: str = "Potion"

    def _create_item(
        self, config: "PotionConfig", index: int, effect_component, projectile: Entity
    ) -> Item:
        """Create base drinkable potion item."""
        item = super()._create_item(config, index, effect_component, projectile)

        components = [
            effect_component(
                amplifier=self.amplifier,
                duration=self.duration,
            ),
            ItemUseModifiers(use_duration=self.use_duration),
            ItemFood(
                can_always_eat=True,
                nutrition=0,
                saturation_modifier=0,
                using_converts_to=MinecraftItemTypes.GlassBottle(),
            ),
            ItemUseAnimation(value="drink"),
        ]

        item.server.components.add(*components)
        return item


@dataclass(kw_only=True)
class Splash(PotionVariant):
    """Splash potion variant."""

    duration: int = 135
    projectile_offset: Vector3D = (0, 0, 0.3)
    projectile_angle: float = -20
    potion_type: str = "splash"
    potion_display: str = "Splash Potion"

    def _create_item(
        self, config: "PotionConfig", index: int, effect_component, projectile: Entity
    ) -> Item:
        """Create base drinkable potion item."""
        item = super()._create_item(config, index, effect_component, projectile)
        event_name = f"{config.effect_key}_splash_{index}"

        components = [
            ItemThrowable(),
            ItemProjectile(
                projectile_entity=f"{projectile}<{event_name}>",
                minimum_critical_power=1,
            ),
        ]

        item.server.components.add(*components)
        return item

    def _setup_projectile(
        self, config: "PotionConfig", index: int, projectile: Entity
    ) -> None:
        """Setup splash projectile event."""
        event_name = f"{config.effect_key}_splash_{index}"
        event = projectile.server.event(event_name)

        properties = {
            "duration": self.duration,
            "amplifier": self.amplifier,
            "type": 1,
            "effect_id": config.effect_id,
        }

        for prop, value in properties.items():
            event.add_property(prop, value)


@dataclass(kw_only=True)
class Lingering(PotionVariant):
    """Lingering potion variant."""

    duration: int = int(180 * 0.25)
    projectile_offset: Vector3D = (0, 0, 0.3)
    projectile_angle: float = -20
    potion_type: str = "lingering"
    potion_display: str = "Lingering Potion"

    def _create_item(
        self, config: "PotionConfig", index: int, effect_component, projectile: Entity
    ) -> Item:
        item = super()._create_item(config, index, effect_component, projectile)
        event_name = f"{config.effect_key}_lingering_{index}"

        components = [
            ItemThrowable(),
            ItemProjectile(
                projectile_entity=f"{projectile}<{event_name}>",
                minimum_critical_power=1,
            ),
        ]

        item.server.components.add(*components)
        item.queue()
        return item

    def _setup_projectile(
        self, config: "PotionConfig", index: int, projectile: Entity
    ) -> None:
        """Setup lingering projectile event."""
        event_name = f"{config.effect_key}_lingering_{index}"
        cloud_duration = int(self.duration)
        event = projectile.server.event(event_name)

        properties = {
            "duration": cloud_duration,
            "amplifier": self.amplifier,
            "type": 2,
            "effect_id": config.effect_id,
        }

        for prop, value in properties.items():
            event.add_property(prop, value)


@dataclass(kw_only=True)
class Tick(PotionVariant):
    """Tick potion variant."""

    duration: int = 135
    projectile_offset: Vector3D = (0, 0, 0.3)
    projectile_angle: float = -20
    potion_type: str = "splash"
    potion_display: str = "Splash Potion"

    def _create_item(
        self, config: "PotionConfig", index: int, effect_component, projectile: Entity
    ) -> Item:
        """Create base drinkable potion item."""
        item = super()._create_item(config, index, effect_component, projectile)

        components = [ItemBlockPlacer()]

        item.server.components.add(*components)
        return item


PotionVariantType = Drinkable | Splash | Lingering
