# Simple Block

A **Stool**: a block that is not a full cube, with its model and texture coming from one Blockbench file.

## What you get

- A wooden stool, a seat on four legs, 12 pixels wide and 10 tall, in the Items tab of the creative menu.
- A collision and selection box that match the model, wood sounds, and a recipe: three oak slabs on two sticks.

## The code

[`scripts/python/stool.py`](scripts/python/stool.py) builds the block.

```python
block.server.components.add(
    BlockGeometry(blockbench="stool"),
    BlockMaterialInstance().add_instance(
        spec=InstanceSpec(blockbench="stool", variations=[InstanceVariant(color="stool")])
    ),
    BlockCollisionBox(origin=(-6, 0, -6), size=(12, 10, 12)),
    BlockSelectionBox(origin=(-6, 0, -6), size=(12, 10, 12)),
    BlockDestructibleByMining(seconds_to_destroy=1),
)
block.client.sound_group(BlockSoundGroup.Wood)
```

- `blockbench="stool"` names [`assets/bbmodels/stool.bbmodel`](assets/bbmodels/stool.bbmodel). Its model identifier must be `stool`, the file name.
- Anvil exports the geometry and the texture from the `.bbmodel`, and writes `terrain_texture.json` and `blocks.json` for you.
- `color="stool"` is the name of a texture inside the `.bbmodel`. A name that is not there stops the build with an error, instead of a pink block in game.
- The boxes are in pixels from the bottom centre of the block, the same space as the model in Blockbench.

The recipe leaves the middle of the bottom row empty with `None`:

```python
recipe.ingredients([[slab, slab, slab], [stick, None, stick]])
```

## What Anvil writes

The block, its item and recipe in the behavior pack; the geometry, texture, `terrain_texture.json` and `blocks.json` in the resource pack; manifests and language files in both.

## Next

[Street Lamp](../street_lamp/) splits one model into parts and adds states and a script.
