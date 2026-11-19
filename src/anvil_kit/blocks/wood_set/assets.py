"""The project files a wood set needs besides its blocks: the base Blockbench models and the
optional creative group."""

import shutil
from pathlib import Path

import click

from anvil.api.items.crafting import CraftingItemCatalog
from anvil.api.items.items import Item
from anvil.lib.jsonmodel.enums import ItemCategory

from .blocks import BOAT_MODEL, MODEL

BASE_MODELS = Path(__file__).parent / "models"


def copy_base_models() -> None:
    """Copies the base Blockbench models into the project when they aren't there.

    Nothing is ever overwritten: a model that exists is the user's. Each copy is reported,
    so the user knows which model to finish with the set's textures.
    """
    models = Path("assets") / "bbmodels"
    missing = [
        name
        for name in (MODEL, BOAT_MODEL)
        if not (models / f"{name}.bbmodel").exists()
    ]
    if not missing:
        return

    models.mkdir(parents=True, exist_ok=True)
    for name in missing:
        shutil.copy(BASE_MODELS / f"{name}.bbmodel", models)
        click.echo(
            click.style(
                f"\r[INFO]: {name}.bbmodel not found in {models}. Copied the base wood set model there to finish.",
                fg="yellow",
            )
        )


def add_creative_group(name: str, items: list[Item]) -> None:
    """Move the items out of their vanilla groups into a group of their own."""
    CraftingItemCatalog().add_group(
        ItemCategory.Construction,
        f"{name.replace('_', ' ').title()} Wood",
        items[0],
        items,
    ).queue()
