# Examples

Each folder is a complete Anvil project you can build as is, read, and copy into your own add-ons.

| Example | What it shows |
| --- | --- |
| [Wood Set](wood_set/) | Two custom woods from `anvil_kit.blocks.wood_set`: maple from one call, and willow with its own tree and leaves that drop sticks. |

## Building an example

Requirements: Python 3.15, Node.js, and the kit (`pip install mcanvil-kit`, which installs Anvil).

```bash
cd examples/wood_set
npm install
anvil build
```

Everything in this folder is under the [MIT License](LICENSE).
