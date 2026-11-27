"""The one projectile entity shared by every thrown potion."""

from typing import TYPE_CHECKING

from anvil.api.actors.components import (
    BandwidthValues,
    EntityBodyRotationBlocked,
    EntityCollisionBox,
    EntityConditionalBandwidthOptimization,
    EntityPhysics,
    EntityProjectile,
    EntityPushableByBlock,
    EntityPushableByEntity,
)
from anvil.api.actors.entity import Entity
from anvil.api.logic.molang import Molang, Query
from anvil.api.pbr.texture_set import TextureComponents

if TYPE_CHECKING:
    from .potion import Potion


def create_projectile() -> Entity:
    """Create a single universal projectile entity for all potion types"""
    entity = Entity("potion_projectile")
    entity.server.description.config(is_spawnable=False)

    entity.server.description.add_int_property("amplifier", (0, 255), default=0)
    entity.server.description.add_int_property("duration", (1, 2**31 - 1), default=1)
    entity.server.description.add_int_property(
        "type", (0, 2**31 - 1), default=0, client_sync=True
    )
    entity.server.description.add_int_property(
        "effect_id", (0, 2**31 - 1), default=0, client_sync=True
    )
    entity.server.description.add_float_property("splash_range", (0, 256), default=4)
    entity.server.description.add_float_property(
        "lingering_radius", (0, 256), default=3
    )
    entity.server.description.add_int_property(
        "lingering_lifetime", (1, 2**31 - 1), default=600
    )

    entity.client.description.animation("potion_model", "face_camera", True)
    entity.client.description.add_geometry("potion_model")

    entity.server.components.add(
        EntityCollisionBox(height=0.25, width=0.25),
        EntityPhysics(),
        EntityPushableByBlock(),
        EntityPushableByEntity(),
        EntityProjectile(
            angle_offset=-20,
            gravity=0.05,
            hit_sound="glass",
            power=0.5,
        ).set_on_hit(douse_fire=True),
        EntityConditionalBandwidthOptimization(
            default_values=BandwidthValues(
                max_optimized_distance=80,
                max_dropped_ticks=10,
                use_motion_prediction_hints=True,
            )
        ),
        EntityBodyRotationBlocked(),
    )

    entity.queue()
    return entity


def add_render_controller(
    projectile: Entity, potion: "Potion", textures: list[str]
) -> None:
    """Draw `potion`'s textures on the projectile while it carries `potion.effect_id`."""
    for texture in textures:
        projectile.client.description.add_texture(
            blockbench="potion_model", color=texture
        )

    rc = projectile.client.description.render_controller(
        f"potion_{potion.key}", Query.Property("effect_id") == potion.effect_id
    )
    rc.set_geometry("potion_model")
    rc.texture_array(f"potion_{potion.key}", textures, Query.Property("type"))
