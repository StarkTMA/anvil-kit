"""`WoodSet`, which configures and builds a wood set, and the `create_wood_set` shortcut."""

from collections.abc import Callable, Iterable

from anvil.api.actors.entity import Entity
from anvil.api.blocks.blocks import Block
from anvil.api.features import Feature
from anvil.api.items.items import Item
from anvil.lib.jsonmodel.enums import BlockSoundGroup
from anvil.lib.jsonmodel.types import Color

from .assets import add_creative_group, copy_base_models
from .blocks import MAP_COLOR, sapling
from .blocks.leaves import LeafDrop
from .parts import BLOCKS, ENTITY_PARTS, WoodBlock, WoodSetPart
from .scaffold import write_typescript


class WoodSet(dict[str, WoodSetPart]):
    """A wood set: configure it, then `build()` it. Once built it maps each part's name (the
    lowercase `WoodBlock` member, like "planks") to its `WoodSetPart`, and a part left out
    with `exclude` is missing.

        palm = (
            WoodSet("palm", exclude=WoodBlock.CHEST_BOAT)
            .tree(lambda wood: make_palm(wood["log"].block, wood["leaves"].block))
            .leaf_drop(coconut, 0.02)
            .map_color("#C2A56B")
            .build()
        )
        block, item = palm["planks"]

    The methods that configure the set return it, so they chain; all of them must come
    before `build()`.
    """

    def __init__(
        self,
        name: str,
        exclude: WoodBlock | Iterable[WoodBlock] = (),
        *,
        own_creative_group: bool = False,
    ) -> None:
        """
        Args:
            name (str): The name of the wood, which prefixes every block.
            exclude (WoodBlock | Iterable[WoodBlock]): The parts to leave out. Blocks that depend
                on an excluded one lose that part (a sign without planks has no recipe).
            own_creative_group (bool): Put the whole set in one "<Name> Wood" group under
                Construction, instead of next to the vanilla counterparts of each block.
        """
        super().__init__()
        self.name = name
        self.own_creative_group = own_creative_group
        self._tree = None
        self.tree_feature: Feature | str | None = None
        """The feature the saplings grow into, once the set is built."""
        self._drops: list[LeafDrop] = []
        self._leaf_distance = 4
        self._map_color: Color = MAP_COLOR
        self._options: list[tuple[WoodBlock, dict]] = []
        self._soil = list(sapling.DEFAULT_SOIL)
        self._built = False

        excluded = WoodBlock(0)
        for kind in [exclude] if isinstance(exclude, WoodBlock) else exclude:
            excluded |= kind
        self.blocks = WoodBlock.ALL & ~excluded

    def tree(
        self, tree: Feature | str | Callable[["WoodSet"], Feature | str]
    ) -> "WoodSet":
        """Sets the feature the saplings grow into: a `Feature`, its identifier, or a function
        that builds it from the set once its blocks exist (so the tree can use them). The
        caller queues the feature. It is required unless `WoodBlock.SAPLING` is excluded.
        """
        self._tree = tree
        return self

    def leaf_drop(
        self, item: Item | str, chance: float, count: int | tuple[int, int] = 1
    ) -> "WoodSet":
        """Adds an item the leaves drop by chance, like the apple of oak (`LeafDrop`)."""
        self._drops.append(LeafDrop(item, chance, count))
        return self

    def sapling_on(self, blocks: Iterable[str | object]) -> "WoodSet":
        """Sets the blocks the sapling can be planted on (by default dirt, grass, sand...).
        Accepts identifiers and block descriptors like `MinecraftBlockTypes.Sand()`."""
        self._soil = [str(block) for block in blocks]
        return self

    def leaf_distance(self, blocks: int) -> "WoodSet":
        """Sets how far a log can be from the leaves holding on to it (4 like vanilla), going
        through leaves. Set it to the distance of the farthest leaf of your trees."""
        self._leaf_distance = blocks
        return self

    def map_color(self, color: Color) -> "WoodSet":
        """Sets the color every block of the set has on a map (a "#RRGGBB" hex value or an
        [R, G, B] list from 0 to 255). By default it is "#e6d063". Boats are entities, so
        they have none."""
        self._map_color = color
        return self

    def sound_group(
        self, group: BlockSoundGroup | str, parts: WoodBlock = WoodBlock.ALL
    ) -> "WoodSet":
        """Sets the vanilla sound group of the parts, which play all of its sounds. By default
        the blocks have `BlockSoundGroup.Wood`, the hanging sign `HangingSign`, and the leaves
        and saplings `Grass`.

            WoodSet("rotten").sound_group(BlockSoundGroup.Mud)
            WoodSet("rotten").sound_group(BlockSoundGroup.Mud, WoodBlock.LOG | WoodBlock.WOOD)
        """
        return self.options(parts, sound_group=group)

    def options(self, parts: WoodBlock = WoodBlock.ALL, **options) -> "WoodSet":
        """Passes keyword arguments to the `create` of the parts, to change what their files
        document as options: the sound ids of the door (`open_sound`, `close_sound`), of the
        button and the pressure plate (`on_sound`, `off_sound`)...

            WoodSet("rotten").options(WoodBlock.DOOR, open_sound="rotten.door_open")

        A part that doesn't take an option raises when the set is built; a later call wins.
        """
        self._options.append((parts, options))
        return self

    def build(self) -> "WoodSet":
        """Creates and queues every block, and writes their scripts. Returns the set."""
        if self._built:
            return self
        if WoodBlock.SAPLING in self.blocks and self._tree is None:
            raise ValueError(
                f"The '{self.name}' wood set has saplings, so it needs the feature they grow "
                "into: call `.tree(...)`, or exclude WoodBlock.SAPLING."
            )

        copy_base_models()

        selected = {kind.name.lower() for kind in BLOCKS if kind in self.blocks}

        extra_arguments = {
            WoodBlock.LEAVES: lambda: (self._drops, self._leaf_distance),
            WoodBlock.SAPLING: lambda: (self._resolve_tree(), self._soil),
        }
        for kind, create in BLOCKS.items():
            if kind in self.blocks:
                arguments = extra_arguments.get(kind, lambda: ())()
                options = {}
                if kind not in ENTITY_PARTS:
                    options["map_color"] = self._map_color
                for parts, given in self._options:
                    if kind in parts:
                        options.update(given)
                self._add_part(kind, create(self.name, selected, *arguments, **options))

        if self.own_creative_group and self:
            add_creative_group(self.name, [part.item for part in self.values()])
        write_typescript([part.block for part in self.values()])
        self._built = True
        return self

    def _resolve_tree(self) -> Feature | str:
        """The tree feature, built now if it was given as a function."""
        self.tree_feature = self._tree(self) if callable(self._tree) else self._tree
        return self.tree_feature

    def _add_part(self, kind: WoodBlock, made: Block | tuple[Entity, Item]) -> None:
        """Stores what a `create` function made under the part's name: a block (its item is
        `block.item`), or an (entity, item) pair for boats."""
        block, item = made if isinstance(made, tuple) else (made, made.item)
        self[kind.name.lower()] = WoodSetPart(block, item)


def create_wood_set(
    name: str,
    exclude: WoodBlock | Iterable[WoodBlock] = (),
    *,
    tree: Feature | str | Callable[[WoodSet], Feature | str] | None = None,
    leaf_drops: Iterable[LeafDrop] = (),
    map_color: Color = MAP_COLOR,
    own_creative_group: bool = False,
) -> WoodSet:
    """Create every block of the `name` wood set except `exclude`, in one call.

    A shortcut for `WoodSet(name, exclude, ...)` with its `tree`, `leaf_drops` and `map_color`, built right
    away. Use the `WoodSet` class to add leaf drops step by step.

        block, item = create_wood_set("rotten", tree=my_tree)["planks"]
    """
    wood = WoodSet(name, exclude, own_creative_group=own_creative_group).map_color(
        map_color
    )
    if tree is not None:
        wood.tree(tree)
    for drop in leaf_drops:
        wood.leaf_drop(drop.item, drop.chance, drop.count)
    return wood.build()
