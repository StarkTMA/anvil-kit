# Examples

Each folder is a complete Anvil project you can build as is, read, and copy into your own add-ons.
They build on each other, so read them in order: each one adds a few ideas to the last.

| Example | What it shows |
| --- | --- |
| [Hello Item](hello_item/) | Start here. One custom item with a texture, a display name and a crafting recipe. |
| [Simple Block](simple_block/) | A block that is not a full cube, its model and texture from one Blockbench file. |
| [Street Lamp](street_lamp/) | A two-block-tall lamp you switch on and off: a multi-part block, Blockbench collections, a state, permutations and a script. |
| [Wood Set](wood_set/) | Everything above at scale, from a reusable kit. Two custom woods from `anvil_kit.blocks.wood_set`: maple from one call, and willow with its own tree and leaves that drop sticks. |

## Building an example

Requirements: Python 3.15, Node.js, and the kit (`pip install mcanvil-kit`, which installs Anvil).

```bash
cd examples/wood_set
npm install
anvil build
```

Hello Item and Simple Block have no scripts, so they don't need `npm install`.

Everything in this folder is under the [MIT License](LICENSE).
