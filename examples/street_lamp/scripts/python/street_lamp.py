from anvil.api.blocks.blocks import Block
from anvil.api.blocks.components import (
    BlockCollisionBox,
    BlockCustomComponent,
    BlockDestructibleByMining,
    BlockGeometry,
    BlockLightEmission,
    BlockMaterialInstance,
    BlockMovable,
    BlockPlacementFilter,
    BlockSelectionBox,
    InstanceSpec,
    InstanceVariant,
)
from anvil.api.core.filters import Filter
from anvil.api.features import CoordinateRange, FeatureRule, MultiBlockFeature
from anvil.api.items.components import ItemBlockPlacer, ItemIcon
from anvil.api.items.crafting.shaped import ShapedCraftingRecipe
from anvil.api.logic.molang import Query
from anvil.api.pbr.texture_set import TextureComponents
from anvil.api.vanilla.biomes import MinecraftBiomeTags
from anvil.api.vanilla.items import MinecraftItemTypes
from anvil.lib.jsonmodel.enums import (
    BlockFaceValues,
    BlockSoundGroup,
    FeatureRulePlacementPass,
    ItemCategory,
    MultiblockPartState,
)

MODEL = "street_lamp"

BOTTOM = Query.BlockState(MultiblockPartState.Part) == 0
TOP = Query.BlockState(MultiblockPartState.Part) == 1
LIT = Query.BlockState("lit")


class LampSwitch(BlockCustomComponent):
    identifier = "lamp_switch"


def material(texture: str) -> BlockMaterialInstance:
    return BlockMaterialInstance().add_instance(
        spec=InstanceSpec(blockbench=MODEL, variations=[InstanceVariant(color=texture)])
    )


def post_geometry() -> BlockGeometry:
    geometry = BlockGeometry(blockbench=MODEL, collection="post")
    culling = geometry.block_culling(culling_shape="custom")
    culling.add_rule(BlockFaceValues.Down, "post", BlockFaceValues.Down, cube_index=0)
    culling.add_rule(BlockFaceValues.Up, "post", BlockFaceValues.Up, cube_index=1)
    return geometry


def lamp_geometry() -> BlockGeometry:
    geometry = BlockGeometry(blockbench=MODEL, collection="lamp")
    culling = geometry.block_culling(culling_shape="custom")
    culling.add_rule(BlockFaceValues.Down, "lamp", BlockFaceValues.Down, cube_index=0)
    return geometry


def register_street_lamp() -> Block:
    block = Block("street_lamp")
    block.server.description.set_menu_category(ItemCategory.Items)
    block.server.description.add_state("lit", (False, True))
    block.server.description.traits.set_multi_block("up", 2)

    block.server.components.add(
        post_geometry(),
        material("street_lamp"),
        BlockCollisionBox(origin=(-1, 0, -1), size=(2, 16, 2)),
        BlockSelectionBox(origin=(-3, 0, -3), size=(6, 16, 6)),
        BlockDestructibleByMining(seconds_to_destroy=1.5),
        BlockMovable(movement_type="immovable"),
        BlockPlacementFilter().add_condition(allowed_faces=[BlockFaceValues.Up]),
        LampSwitch(),
    )

    block.server.permutation(TOP).add(
        lamp_geometry(),
        BlockCollisionBox(origin=(-4, 0, -4), size=(8, 14, 8)),
        BlockSelectionBox(origin=(-4, 0, -4), size=(8, 14, 8)),
    )
    block.server.permutation(LIT).add(material("street_lamp_lit"))
    block.server.permutation(TOP & LIT).add(BlockLightEmission(value=15))

    block.client.sound_group(BlockSoundGroup.Lantern)

    block.item.server.description.set_menu_category(ItemCategory.Items)
    block.item.server.components.add(
        ItemIcon(textures=TextureComponents(color="street_lamp")),
        ItemBlockPlacer(block=block, replace_block_item=True),
    )
    block.queue()

    iron = MinecraftItemTypes.IronIngot()
    recipe = ShapedCraftingRecipe("street_lamp")
    recipe.ingredients(
        [
            [None, MinecraftItemTypes.GlowstoneDust(), None],
            [None, iron, None],
            [None, iron, None],
        ]
    )
    recipe.result(block)
    recipe.unlock_items([MinecraftItemTypes.GlowstoneDust()])
    recipe.queue()

    return block


def register_street_lamp_generation(block: Block) -> None:
    lamp = MultiBlockFeature("street_lamp_feature", block)
    lamp.may_replace(["minecraft:air"])
    lamp.queue()

    rule = FeatureRule(
        "street_lamp_feature_rule", lamp, FeatureRulePlacementPass.SurfacePass
    )
    rule.biome_filter(Filter.has_biome_tag(MinecraftBiomeTags.Plains))
    rule.distribution(
        iterations=1,
        scatter_chance=5,
        x=CoordinateRange("uniform", (0, 15)),
        y="query.heightmap(variable.worldx, variable.worldz)",
        z=CoordinateRange("uniform", (0, 15)),
    )
    rule.queue()
