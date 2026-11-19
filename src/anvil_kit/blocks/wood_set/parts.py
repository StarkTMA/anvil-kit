"""The parts a wood set can contain, and the file in `blocks/` that creates each."""

from enum import Flag, auto
from typing import NamedTuple

from anvil.api.actors.entity import Entity
from anvil.api.blocks.blocks import Block
from anvil.api.items.items import Item

from .blocks import (
    boat,
    button,
    chest_boat,
    door,
    fence,
    fence_gate,
    hanging_sign,
    leaves,
    log,
    log_stripped,
    planks,
    pressure_plate,
    sapling,
    sign,
    slab,
    stairs,
    trapdoor,
    wood,
    wood_stripped,
)


class WoodBlock(Flag):
    """The blocks a wood set can contain. Combine them with `|` and remove them with `& ~`."""

    PLANKS = auto()
    BUTTON = auto()
    PRESSURE_PLATE = auto()
    FENCE = auto()
    FENCE_GATE = auto()
    STAIRS = auto()
    DOOR = auto()
    TRAPDOOR = auto()
    SLAB = auto()
    LOG = auto()
    LOG_STRIPPED = auto()
    WOOD = auto()
    WOOD_STRIPPED = auto()
    SIGN = auto()
    HANGING_SIGN = auto()
    BOAT = auto()
    CHEST_BOAT = auto()
    LEAVES = auto()
    SAPLING = auto()

    ALL = (
        PLANKS
        | BUTTON
        | PRESSURE_PLATE
        | FENCE
        | FENCE_GATE
        | STAIRS
        | DOOR
        | TRAPDOOR
        | SLAB
        | LOG
        | LOG_STRIPPED
        | WOOD
        | WOOD_STRIPPED
        | SIGN
        | HANGING_SIGN
        | BOAT
        | CHEST_BOAT
        | LEAVES
        | SAPLING
    )


class WoodSetPart(NamedTuple):
    """A part of a wood set: what it places and the item that places it."""

    block: Block | Entity
    """The block, or the entity for boats and chest boats."""
    item: Item
    """The item in the inventory. For a block it is `block.item`."""


ENTITY_PARTS = {WoodBlock.BOAT, WoodBlock.CHEST_BOAT}

BLOCKS = {
    WoodBlock.PLANKS: planks.create,
    WoodBlock.BUTTON: button.create,
    WoodBlock.PRESSURE_PLATE: pressure_plate.create,
    WoodBlock.FENCE: fence.create,
    WoodBlock.FENCE_GATE: fence_gate.create,
    WoodBlock.STAIRS: stairs.create,
    WoodBlock.DOOR: door.create,
    WoodBlock.TRAPDOOR: trapdoor.create,
    WoodBlock.SLAB: slab.create,
    WoodBlock.LOG: log.create,
    WoodBlock.LOG_STRIPPED: log_stripped.create,
    WoodBlock.WOOD: wood.create,
    WoodBlock.WOOD_STRIPPED: wood_stripped.create,
    WoodBlock.SIGN: sign.create,
    WoodBlock.HANGING_SIGN: hanging_sign.create,
    WoodBlock.BOAT: boat.create,
    WoodBlock.CHEST_BOAT: chest_boat.create,
    WoodBlock.LEAVES: leaves.create,
    WoodBlock.SAPLING: sapling.create,
}
