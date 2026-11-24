# Kit

`anvil_kit` holds ready-made content built on top of the [API](https://anvil.starktma.net/api/): call one function and get a complete, working feature such as a full wood set.

!!! warning "Stability"
The kit is opinionated and may change between minor versions: names, parameters and the content it generates can all change. Pin your kit version if you depend on a kit's exact output.

    The [API](https://anvil.starktma.net/api/) (`anvil.api`) is the stable layer. If you need full control or long-term stability, build on the API directly and use the kit as a reference.

## Optional dependencies

Some kits need packages that a plain `pip install mcanvil-kit` doesn't include. Install them through the matching extra:

| Kit                    | Extra           | Install                         |
| ---------------------- | --------------- | ------------------------------- |
| `anvil_kit.world.ldtk` | `ldtk` (Amulet) | `pip install mcanvil-kit[ldtk]` |

Importing a kit without its extra raises an `ImportError` naming the command to run.

## Available kits

### Blocks

- **`anvil_kit.blocks.wood_set`**: a complete wood set (planks, logs, wood, slabs, stairs, fences, gates, doors, trapdoors, buttons, pressure plates, signs (standing and wall in one block), hanging signs, boats and chest boats) with recipes, vanilla wood tags, fuel values, creative inventory placement and the TypeScript components they need.

```python
from anvil_kit.blocks.wood_set import WoodBlock, create_wood_set

create_wood_set("rotten", tree=my_tree)                      # everything; saplings grow `my_tree`
create_wood_set("rotten", WoodBlock.SAPLING)                 # everything but saplings: no tree needed
create_wood_set("rotten", WoodBlock.DOOR, tree=my_tree)      # everything but doors
create_wood_set("rotten", own_creative_group=True, tree=my_tree)  # in its own creative group
create_wood_set("rotten", map_color="#5C4A32", tree=my_tree)  # the color of every block on maps

WoodSet("rotten").sound_group(BlockSoundGroup.Mud)             # a vanilla sound group, for all parts
WoodSet("rotten").options(WoodBlock.DOOR, open_sound="rotten.door_open")  # a sound a script plays

wood = create_wood_set("rotten", tree=my_tree)
block, item = wood["planks"]                                # each part is a (block, item) pair
```

A set with saplings needs `tree`, the feature they grow into (a `Feature`, its identifier, or a function that builds it from the finished set: `tree=lambda wood: make_tree(wood["log"].block, wood["leaves"].block)`); the kit makes no trees. Build and queue it yourself: it can use the set's blocks by their identifiers (`<namespace>:<name>_log`, `<namespace>:<name>_leaves` with its `natural` state on).

### World

- **`anvil_kit.world.potions`**: potion variants (drinkable, splash, lingering), brewing recipes and the TypeScript that applies them in game. See [Potions](#potions).
- **`anvil_kit.world.ldtk`**: builds a Minecraft world from an [LDtk](https://ldtk.io) map. Needs the `ldtk` extra.

### Actors

- **`anvil_kit.actors.materials`**: an entity outline material.

## The `WoodSet` class

`create_wood_set` covers the simple case. For anything more, build the set with the class:

```python
palm = (
    WoodSet("palm", exclude=WoodBlock.CHEST_BOAT)
    .tree(lambda wood: make_palm(wood["log"].block, wood["leaves"].block))
    .leaf_drop(coconut, 0.02)  # drops when the leaves are broken (no shears) or decay
    .build()
)
palm["planks"].block
```

- `tree` is a feature, its identifier, or a function receiving the set once its blocks exist. Once built, `palm.tree_feature` is the resolved feature.
- `leaf_drop(item, chance, count=1)` takes an `Item` or an identifier like `minecraft:apple`.

## Potions

A potion is a `Potion`. Add its variants and brewing recipes, then `queue()` it, which returns one item per variant. Every argument is keyword-only:

```python
from anvil.api.vanilla.items import MinecraftItemTypes
from anvil_kit.world.potions import Potion

recall = Potion(
    key="recall",                  # the effectManager effect it applies
    title="Recall",                # "Potion of Recall"
    color="#C710FF",
)

drinkable = recall.drinkable(duration=12)                 # seconds
splash = recall.splash(duration=12, range=4)              # range in blocks
lingering = recall.lingering(duration=3, radius=3, lifetime=30)  # cloud radius in blocks, lifetime in seconds
strong_splash = recall.splash(amplifier=1, duration=24, range=6)  # counted from 0 like the game: 1 is "II"

recall.brew(result=drinkable, reagent=MinecraftItemTypes.CopperIngot())   # from an awkward potion
recall.brew(result=splash, reagent=MinecraftItemTypes.Gunpowder(), source=drinkable)
recall.brew(result=strong_splash, reagent=MinecraftItemTypes.Redstone(), source=splash)

items = recall.queue()
```

A stronger potion is the same variant again with a higher `amplifier`. Each splash and lingering potion has its own `range`, `radius` and `lifetime`, carried by the thrown projectile. `brew()` takes the variants this potion's `drinkable()`, `splash()` and `lingering()` returned. `Potion(...)` checks its values when it's created, and `queue()` raises when a potion has no variants or its key is already queued. Potions are numbered in the order they're queued; the TypeScript is written in the same build, so the numbers always match.

Items and the thrown projectile use the project's Blockbench model `assets/bbmodels/potion_model.bbmodel`, which needs a `face_camera` animation.

### In game

Every `register()` call writes the potions' TypeScript into `scripts/javascript/potions`. Don't edit these files, the next build overwrites them:

| File            | What it does                                                    |
| --------------- | --------------------------------------------------------------- |
| `index.ts`      | One exported object per potion, the `POTIONS` table of them, and `registerPotions()` |
| `potion.ts`     | The `Potion` type and helpers shared by the others              |
| `drinkable.ts`  | The `<namespace>:potion_effect` item component every drinkable shares |
| `splash.ts`     | Thrown splash potions landing, and the burst                    |
| `lingering.ts`  | Thrown lingering potions landing, and their clouds              |

`index.ts` exports each potion as `<key>Potion` in camelCase (`stasis` is `stasisPotion`, `night_vision` is `nightVisionPotion`), so an effect can read its potion's data instead of repeating it:

```ts
import { stasisPotion } from "../potions";

export const stasis = effectManager.registerEffect({
	id: stasisPotion.id,
	color: stasisPotion.color,
	handler(entity) { ... },
});
```

A potion only names its effect: register an effect with the same name as the potion's `key` with `effectManager` from `@starktma/minecraft-utils`, then register the potions at startup:

```ts
import { system } from "@minecraft/server";
import { setNamespace } from "@starktma/minecraft-utils";
import { effectManager } from "@starktma/minecraft-utils/minecraft";
import { NAMESPACE } from "./constants";
import { registerPotions } from "./potions";

export { stasis } from "./effects/stasis"; // effectManager.registerEffect({ id: "stasis", ... })

setNamespace(NAMESPACE);

system.beforeEvents.startup.subscribe((startup) => {
	registerPotions(startup);
	effectManager.start();
});
```
