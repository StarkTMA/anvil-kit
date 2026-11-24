# Changelog

## 0.1.4

- Potions are made with one keyword-only class: `Potion(key=, title=, color=, ...)`, then `drinkable()`, `splash(range=)` and `lingering(radius=, lifetime=)` to add variants (call one again with a higher `amplifier` for a stronger potion), `brew(result=, reagent=, source=None)`, and `queue()`, which returns the items. `PotionAPI`, `PotionConfig`, `Brewing` and the variant classes are no longer exported, and `effect_id` is gone: potions are numbered in the order they're queued. `effect_key`, `effect_title` and `color_hex` are now `key`, `title` and `color`.
- Splash range and lingering cloud radius and lifetime are set per variant (`splash(range=4)`, `lingering(radius=3, lifetime=30)`) instead of per potion. The potion projectile carries them as `splash_range`, `lingering_radius` and `lingering_lifetime` properties, and `POTIONS` entries no longer hold them.
- The potions' TypeScript is split into small modules in `scripts/javascript/potions`: `index.ts` (the `POTIONS` table and `registerPotions()`), `potion.ts` (shared type and helpers), then one file per potion type: `drinkable.ts`, `splash.ts` and `lingering.ts`. `registerPotions(startup)` is unchanged; `startPotions()` is gone. Delete the old `potions.ts` by hand when upgrading.
- `index.ts` exports each potion as its own object, `<effectKey>Potion` (`stasisPotion`), and `POTIONS` is built from them, so effects can read a potion's `id` and `color` directly.
- Drinkable potions share one `<namespace>:potion_effect` item component instead of one `<namespace>:<key>_potion_effect` per potion; its params carry the `effect` name next to `amplifier` and `duration`.
- `Potion` checks its values when it's created and says what to fix: the `key` format and `color`; `splash()` and `lingering()` reject a range, radius or lifetime that isn't above 0. `queue()` raises on a potion without variants or a key queued twice.
- `brew()` raises right away when its `result` or `source` isn't one of the potion's own variants.
- Lingering potion items were queued twice.
- A brewing `reagent` takes an item as well as an identifier.
- The kit docs have a Potions section: a full example, the files written into the project, and the TypeScript wiring.

## 0.1.3

- Three beginner examples lead up to the wood set in `examples/`: `hello_item` (one item with a texture and a recipe), `simple_block` (a stool modelled in Blockbench) and `street_lamp` (a two-part lamp with Blockbench collections, a block state, permutations, a script, voxel shape culling and world generation).
- The README lists every example in reading order under Examples.
- The wood set example's item textures no longer carry embedded editor metadata.

## 0.1.2

- `Brewing(result, reagent, source=None)` takes the variant objects instead of `from_index`/`to_index`; leave `source` out to brew from an awkward potion. Recipes name themselves `brew_<effect_key>_<n>`, so two recipes for the same result no longer clash. Potion variants are keyword-only (`Drinkable(duration=240)`).
- Potion variants take only `amplifier`, counted from 0 like the game (`0` is "I", `1` is "II"); `strength` is gone, and the numeral in the item name comes from the amplifier so the two always agree. `amplifier` defaults to 0, and the potion projectile's `amplifier` property now starts at 0.
- `anvil_kit.world.potions` now writes the potions' TypeScript into `scripts/javascript/potions`, like the wood set does. It handles drinking, splashing and lingering clouds, which used to be `effectManager.registerPotion()` in `@starktma/minecraft-utils`. `index.ts` holds a `POTIONS` table (key, id, colour, splash and lingering settings) generated from the Python, and `registerPotions(startup)` applies each potion with `effectManager.addEffect(entity, effect_key, amplifier, duration)`, so register an effect of the same name with `@starktma/minecraft-utils`. The scripts read the namespace with `getNamespace()` from `@starktma/minecraft-utils`, so call `setNamespace()` before startup.
- `PotionConfig` takes `splash_range`, `lingering_radius` and `lingering_lifetime` (seconds); they used to be set in TypeScript.
- `PotionAPI.register()` raises when two potions share an `effect_key` or an `effect_id`.
- Potion colours are hex everywhere: `POTIONS` holds a hex `color`, and the potion projectile and the `<effect>_potion_effect` item component no longer carry colour channels.
- `anvil_kit.world.potions` and `anvil_kit.blocks.wood_set` are split into focused modules, and their TypeScript lives in each package's `scaffold.py` instead of template and `.ts` files. Public imports are unchanged.

## 0.1.0

- Moved out of Anvil: `anvil.kit` is now `anvil_kit`, installed with `pip install mcanvil-kit`.
- The `ldtk` extra moved too: `pip install mcanvil-kit[ldtk]`.
- The Anvil samples now live in `examples/`.
