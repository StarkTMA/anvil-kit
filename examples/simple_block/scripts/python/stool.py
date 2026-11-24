from anvil.api.blocks.blocks import Block
from anvil.api.blocks.components import (
    BlockCollisionBox,
    BlockDestructibleByMining,
    BlockGeometry,
    BlockMaterialInstance,
    BlockSelectionBox,
    InstanceSpec,
    InstanceVariant,
)
from anvil.api.items.crafting.shaped import ShapedCraftingRecipe
from anvil.api.vanilla.items import MinecraftItemTypes
from anvil.lib.jsonmodel.enums import BlockSoundGroup, ItemCategory

MODEL = "stool"


def register_stool() -> Block:
    block = Block("stool")
    block.server.description.set_menu_category(ItemCategory.Items)

    block.server.components.add(
        BlockGeometry(blockbench=MODEL),
        BlockMaterialInstance().add_instance(
            spec=InstanceSpec(
                blockbench=MODEL,
                variations=[InstanceVariant(color="stool")],
            )
        ),
        BlockCollisionBox(origin=(-6, 0, -6), size=(12, 10, 12)),
        BlockSelectionBox(origin=(-6, 0, -6), size=(12, 10, 12)),
        BlockDestructibleByMining(seconds_to_destroy=1),
    )
    block.client.sound_group(BlockSoundGroup.Wood)

    block.queue()

    slab = MinecraftItemTypes.OakSlab()
    stick = MinecraftItemTypes.Stick()
    recipe = ShapedCraftingRecipe("stool")
    recipe.ingredients([[slab, slab, slab], [stick, None, stick]])
    recipe.result(block)
    recipe.unlock_items([slab])
    recipe.queue()

    return block
