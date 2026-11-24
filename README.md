# Anvil Kit

Ready-made content for [Anvil](https://github.com/StarkTMA/Anvil), the Python framework for Minecraft Bedrock add-ons: call one function, get a working feature.

```bash
pip install mcanvil-kit
pip install mcanvil-kit[ldtk]   # for anvil_kit.world.ldtk
```

```python
from anvil_kit.blocks.wood_set import WoodBlock, create_wood_set

create_wood_set("maple", WoodBlock.SAPLING)
```

## Kits

| Kit | What it makes |
| --- | --- |
| `anvil_kit.blocks.wood_set` | A complete wood set: planks, logs, slabs, stairs, fences, doors, signs, boats, leaves, saplings, with recipes and scripts. |
| `anvil_kit.world.potions` | Potion variants (drinkable, splash, lingering) and brewing recipes. |
| `anvil_kit.world.ldtk` | A Minecraft world from an [LDtk](https://ldtk.io) map. Needs the `ldtk` extra. |
| `anvil_kit.actors.materials` | Entity outline materials. |

The kit is opinionated and may change between minor versions. `anvil.api` is the stable layer.

## Examples

Complete Anvil projects you can build as is, in [`examples/`](examples/):

| Example | What it shows |
| --- | --- |
| [Hello Item](examples/hello_item/) | Start here. One custom item with a texture, a display name and a crafting recipe. |
| [Simple Block](examples/simple_block/) | A block that is not a full cube, its model and texture from one Blockbench file. |
| [Street Lamp](examples/street_lamp/) | A two-block-tall lamp you switch on and off: a multi-part block, Blockbench collections, a state, permutations and a script. |
| [Wood Set](examples/wood_set/) | Everything above at scale, from a reusable kit. Two custom woods from `anvil_kit.blocks.wood_set`: maple from one call, and willow with its own tree and leaves that drop sticks. |

```bash
cd examples/wood_set
npm install
anvil build
```

## Development

```bash
pip install -e ../anvil      # a local Anvil checkout
pip install -e .[test]
pytest
```

## License

MIT ([LICENSE](LICENSE)), for the kit and everything in `examples/`, code and assets: use it in your own add-ons, free or paid.
