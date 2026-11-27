from anvil.api.items.components import ItemDisplayName, ItemIcon, ItemMaxStackSize
from anvil.api.items.crafting.shaped import ShapedCraftingRecipe
from anvil.api.items.items import Item
from anvil.api.vanilla import MinecraftItemTypes
from anvil.lib.jsonmodel.enums import ItemCategory


def register_ruby() -> Item:
    item = Item("ruby")
    item.server.description.set_menu_category(ItemCategory.Items)
    item.server.components.add(
        ItemIcon(color="ruby"),
        ItemDisplayName(value="Ruby"),
        ItemMaxStackSize(value=64),
    )
    item.queue()

    redstone = MinecraftItemTypes.Redstone()
    recipe = ShapedCraftingRecipe("ruby")
    recipe.ingredients([[redstone, redstone], [redstone, redstone]])
    recipe.result(item)
    recipe.unlock_items([redstone])
    recipe.queue()

    return item
