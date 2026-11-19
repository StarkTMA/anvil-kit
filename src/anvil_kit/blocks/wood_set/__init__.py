"""A complete wood set from one call: `create_wood_set("rotten")`.

    WoodSet("rotten").tree(my_tree).leaf_drop(coconut, 0.02).build()   # tree and drops
    WoodSet("rotten").map_color("#5C4A32").build()                      # the color on maps
    WoodSet("rotten", [WoodBlock.DOOR, WoodBlock.BOAT]).tree(my_tree).build()   # all but these
    WoodSet("rotten", WoodBlock.SAPLING | WoodBlock.DOOR).build()      # no saplings: no tree
    create_wood_set("rotten", tree=my_tree)                            # a one-call shortcut

Every block and boat is its own file in `blocks/`: its `create(wood, selected)` builds it,
names it, queues it and registers the recipes that make it. The custom components the
blocks share their scripts through are in `components.py`. The TypeScript the
blocks use (`scaffold.py`) is then written to `scripts/javascript/blocks/wood_set`; register it from
`main.ts` with `registerWoodSet(init)`. The signs' script uses `@minecraft/server-ui`,
so it needs `scriptui` enabled in `anvilconfig.json`.

Expected textures: `<name>_planks`, `<name>_log`, `<name>_log_top`, `<name>_log_stripped`,
`<name>_log_stripped_top`, `<name>_door_bottom`, `<name>_door_top`, `<name>_trapdoor`,
`<name>_hanging_sign`, `<name>_standing_sign`, `<name>_boat`, `<name>_leaves`,
`<name>_sapling`, and the item icons `<name>_sign`,
`<name>_hanging_sign`, `<name>_boat` and `<name>_chest_boat` in `assets/textures/items/`.

Every wood set shares the same two blockbench models, so only the names differ between
sets. Each model holds the textures of every set, named as above:

- `wood_set` (`assets/bbmodels/wood_set.bbmodel`): the block collections. `hanging_sign`
  has a `top_bit` bone (on a wall) and a `top_chain` bone (under a block).
  It also needs a `sapling` collection (a crossed pair of planes) for the saplings.
- `wood_set_boat` (`assets/bbmodels/wood_set_boat.bbmodel`): both boats, facing north,
  with a `chest` bone and the `paddle`, `paddle_left`, `paddle_right` and `shake`
  animations.

Their names are `MODEL` and `BOAT_MODEL` in `blocks/__init__.py`. When one is missing
from `assets/bbmodels`, building a set copies Anvil's base model there (the files in
`models/`), and never overwrites an existing one.

Leaves and saplings: a leaves block's `natural` state is off for leaves a player placed,
which stay forever. Whatever generates leaves sets it on, and they then decay when no log of
the set is within `leaf_distance` blocks through leaves. A sapling grows into the `tree`
feature, which `/place feature` builds at its position. See docs/kit for the details.
"""

from .blocks.leaves import LeafDrop
from .builder import WoodSet, create_wood_set
from .parts import WoodBlock, WoodSetPart

__all__ = [
    "LeafDrop",
    "WoodBlock",
    "WoodSet",
    "WoodSetPart",
    "create_wood_set",
]
