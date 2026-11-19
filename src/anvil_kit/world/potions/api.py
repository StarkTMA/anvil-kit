"""`PotionAPI`, which turns a `PotionConfig` into items, projectile events, brewing recipes
and the potions' TypeScript."""

from typing import Annotated

from anvil.api.actors.entity import Entity
from anvil.api.core.core import CONFIG
from anvil.api.items.components import ItemCustomComponent
from anvil.api.items.items import Item
from anvil.lib.jsonmodel import InRange, json_field

from .brewing import setup_brewing
from .config import PotionConfig
from .projectile import add_render_controller, create_projectile
from .scaffold import write_typescript


class PotionAPI:
    """Registers potions."""

    _projectile: Entity | None = None
    _component_cache: dict[str, type] = {}
    _catalog: list = []
    _configs: dict[str, PotionConfig] = {}

    @classmethod
    def register(cls, config: PotionConfig) -> list[Item]:
        """Register a complete potion configuration.

        Also writes the potions' TypeScript into `scripts/javascript/potions`, see `scaffold.py`.
        """
        cls._check_unique(config)
        effect_component = cls._effect_component(config.effect_key)
        projectile = cls._get_projectile()

        items = []
        textures = []
        for index, variant in enumerate(config.variants):
            items.append(
                variant._create_item(config, index, effect_component, projectile)
            )
            variant._setup_projectile(config, index, projectile)

            texture = f"{config.effect_key}_{variant.potion_type}_potion"
            if texture not in textures:
                textures.append(texture)

        add_render_controller(projectile, config, textures)
        setup_brewing(config, items)

        cls._catalog.append({config.effect_key: items})
        cls._configs[config.effect_key] = config
        write_typescript(cls._configs.values())
        return items

    @classmethod
    def _check_unique(cls, config: PotionConfig) -> None:
        if config.effect_key in cls._configs:
            raise ValueError(
                f"A potion with effect_key '{config.effect_key}' is already registered."
            )
        for other in cls._configs.values():
            if other.effect_id == config.effect_id:
                raise ValueError(
                    f"Potions '{other.effect_key}' and '{config.effect_key}' both use effect_id {config.effect_id}. "
                    "Each potion needs its own effect_id."
                )

    @classmethod
    def _get_projectile(cls) -> Entity:
        if cls._projectile is None:
            cls._projectile = create_projectile()
        return cls._projectile

    @classmethod
    def _effect_component(cls, effect_key: str) -> type:
        """The item component that applies the effect when a drinkable is consumed."""
        if effect_key not in cls._component_cache:

            class DynamicPotionEffect(ItemCustomComponent):
                identifier = f"{CONFIG.NAMESPACE}:{effect_key}_potion_effect"

                amplifier: Annotated[float, InRange(0.0, 255.0)] = json_field()
                duration: float = json_field()

            cls._component_cache[effect_key] = DynamicPotionEffect
        return cls._component_cache[effect_key]
