# Hello Item

The smallest Anvil project: one custom item, the **Ruby**, with a texture, a name and a crafting recipe. Start here.

## What you get

- A Ruby in the Items tab of the creative menu, stacking to 64.
- A shaped recipe: four redstone dust in a square make one ruby. It unlocks in the recipe book once you pick up redstone.

## The code

[`scripts/python/ruby.py`](scripts/python/ruby.py) builds the item and its recipe.

```python
item = Item("ruby")
item.server.components.add(
    ItemIcon(textures=TextureComponents(color="ruby")),
    ItemDisplayName(value="Ruby"),
    ItemMaxStackSize(value=64),
)
item.queue()
```

- `Item("ruby")` gets the project namespace from `anvilconfig.json`, so the item is `anvil_hi:ruby`.
- `color="ruby"` points at [`assets/textures/items/ruby.png`](assets/textures/items/ruby.png). Anvil copies it into the resource pack and writes `item_texture.json`.
- `ItemDisplayName(value="Ruby")` becomes a key in `localization.csv` and the `.lang` files. You never write the key yourself.
- `queue()` is what exports the item. Anything you don't queue is left out of the packs.

The recipe takes the item object itself as its result, so the identifier can never be mistyped:

```python
recipe.ingredients([[redstone, redstone], [redstone, redstone]])
recipe.result(item)
```

[`scripts/python/main.py`](scripts/python/main.py) registers the ruby and compiles the project.

## What Anvil writes

From that one short file: the item and recipe in the behavior pack, the texture and `item_texture.json` in the resource pack, both manifests, and the language files of both packs.

## Next

[Simple Block](../simple_block/) adds a block with a model from Blockbench.
