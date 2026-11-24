# Street Lamp

A **two-block-tall lamp** that you switch on and off by using it. It shows a multi-part block, one Blockbench model split into collections, a block state, permutations, a custom component handled by a script, culling with voxel shapes and a feature that places lamps in the world.

## What you get

- A street lamp that places as two blocks: an iron post at the bottom and the lamp on top. Breaking either part breaks both.
- Using either part switches the lamp. When it is on, the glass glows and the top gives off light level 15.
- Faces hidden by the other part, or by the ground, are culled so the game does not draw them.
- Lamps appear now and then in plains biomes when new chunks generate.
- A recipe: glowstone dust on top of two iron ingots.

## The model

[`assets/bbmodels/street_lamp.bbmodel`](assets/bbmodels/street_lamp.bbmodel) holds both parts, each in its own **Blockbench collection**: `post` and `lamp`. Anvil exports every collection as its own geometry, `geometry.anvil_sl.street_lamp.post` and `geometry.anvil_sl.street_lamp.lamp`, so one file serves both blocks of the lamp.

The model has two textures, `street_lamp` and `street_lamp_lit`. They only differ in the glass.

Each collection also holds **bounding boxes** (Blockbench's *Add Bounding Box*). They are not drawn; Anvil turns them into the part's voxel shape, `anvil_sl:street_lamp.post_culling_shape` and `anvil_sl:street_lamp.lamp_culling_shape`.

## The code

[`scripts/python/street_lamp.py`](scripts/python/street_lamp.py) builds the block.

```python
block.server.description.add_state("lit", (False, True))
block.server.description.traits.set_multi_block("up", 2)
```

- `add_state` declares `anvil_sl:lit`, a state the script changes.
- `set_multi_block("up", 2)` makes the block two parts stacked upwards. The game numbers them in `minecraft:multi_block_part`: 0 at the bottom, 1 on top.
- A multi-block must say how pistons treat it, so the lamp adds `BlockMovable(movement_type="immovable")`, like a door. Without it the game rejects the whole block.

The root components describe the bottom part. Permutations change what differs:

```python
block.server.permutation(TOP).add(
    lamp_geometry(),
    BlockCollisionBox(origin=(-4, 0, -4), size=(8, 14, 8)),
    BlockSelectionBox(origin=(-4, 0, -4), size=(8, 14, 8)),
)
block.server.permutation(LIT).add(material("street_lamp_lit"))
block.server.permutation(TOP & LIT).add(BlockLightEmission(value=15))
```

- `TOP`, `LIT` and `TOP & LIT` are Molang conditions built in Python, `Query.BlockState(...)`. A component in a permutation replaces the root component with the same identifier.
- `lamp_geometry()` uses the `lamp` collection of the model for the top part. See [Culling](#culling).

`LampSwitch` is a custom component. It has no parameters, it only tells the script which blocks to handle:

```python
class LampSwitch(BlockCustomComponent):
    identifier = "lamp_switch"
```

## Culling

A voxel shape tells the game which part of the block is solid to its neighbours. Culling rules say which faces to skip when a neighbour covers them:

```python
def post_geometry() -> BlockGeometry:
    geometry = BlockGeometry(blockbench=MODEL, collection="post")
    culling = geometry.block_culling(culling_shape="custom")
    culling.add_rule(BlockFaceValues.Down, "post", BlockFaceValues.Down, cube_index=0)
    culling.add_rule(BlockFaceValues.Up, "post", BlockFaceValues.Up, cube_index=1)
    return geometry
```

- `culling_shape="custom"` builds the voxel shape from the bounding boxes of the `post` collection and writes it to `shapes/`.
- Each rule names a direction to check, a bone, a face and a cube of that bone (counted from 0, in the model's order). Here the bottom of the base is skipped when the ground covers it, and the top of the pole when the lamp part sits on it.
- `lamp_geometry()` does the same for the top part: the bottom of its pole is skipped against the post.

Anvil checks every bone and cube index against the exported geometry, so a typo fails the build instead of the game.

## World generation

Two files place lamps in the world:

```python
lamp = MultiBlockFeature("street_lamp_feature", block)
lamp.may_replace(["minecraft:air"])
lamp.queue()

rule = FeatureRule("street_lamp_feature_rule", lamp, FeatureRulePlacementPass.SurfacePass)
rule.biome_filter(Filter.has_biome_tag(MinecraftBiomeTags.Plains))
rule.distribution(
    iterations=1,
    scatter_chance=5,
    x=CoordinateRange("uniform", (0, 15)),
    y="query.heightmap(variable.worldx, variable.worldz)",
    z=CoordinateRange("uniform", (0, 15)),
)
rule.queue()
```

- The **feature** says *what* is placed: a multi-block feature places both parts of the lamp, only into air.
- The **feature rule** says *where* and *how often*: in plains, during the surface pass, in 5% of chunks, at a random spot on the surface (`query.heightmap`).

Lamps only appear in chunks generated after the add-on is applied. Try `/place feature anvil_sl:street_lamp_feature` to place one where you stand.

## The script

[`scripts/javascript/main.ts`](scripts/javascript/main.ts) registers `anvil_sl:lamp_switch` and flips the state on every part, so the post and the lamp always agree:

```ts
for (const part of block.getParts() ?? [block]) {
	part.setPermutation(part.permutation.withState(LIT, lit));
}
```

## Next

[Wood Set](../wood_set/) puts all of this together at scale: dozens of blocks, multi-part doors, states, collections and scripts, generated from a reusable kit.
