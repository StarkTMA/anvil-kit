import re

import pytest
from anvil.api.blocks.components import BlockCustomComponent
from anvil.lib.jsonmodel import json_field

from anvil_kit.world.potions import Potion, PotionEffectParameters
from anvil_kit.world.potions import potion as potion_module
from anvil_kit.world.potions.scaffold import OUTPUT_DIRECTORY, SCRIPTS, potion_name, write_typescript
from anvil_kit.world.potions.variants import Drinkable, Lingering, PotionEffect, PotionVariant, Splash


def _potion(key: str, effect_id: int, **values) -> Potion:
    potion = Potion(key=key, title=key.title(), color="#FF8000", **values)
    potion.effect_id = effect_id
    return potion


def _read(tmp_path, name: str) -> str:
    return (tmp_path / OUTPUT_DIRECTORY / name).read_text(encoding="utf-8")


def test_index_lists_each_potion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_typescript([_potion("stasis", 0), _potion("magnet", 7)])

    index = _read(tmp_path, "index.ts")
    assert "NAMESPACE" not in index
    assert 'export const stasisPotion: Potion = {\n\tid: "stasis",' in index
    assert 'export const magnetPotion: Potion = {\n\tid: "magnet",' in index
    assert "\t0: stasisPotion,\n\t7: magnetPotion,\n" in index
    assert "effectId" not in index
    assert "splashRange" not in index
    assert 'color: "#ff8000",' in index
    assert "{{" not in index


def test_runtime_is_split_into_modules(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_typescript([_potion("stasis", 0)])

    written = sorted(path.name for path in (tmp_path / OUTPUT_DIRECTORY).iterdir())
    assert written == sorted(["index.ts", *(f"{name}.ts" for name in SCRIPTS)])

    index = _read(tmp_path, "index.ts")
    for name in ("drinkable", "lingering", "splash"):
        assert f'from "./{name}";' in index
    assert "registerDrinkable(init);" in index
    assert "subscribeSplash(POTIONS)" in index
    assert "subscribeLingering(POTIONS)" in index

    drinkable = _read(tmp_path, "drinkable.ts")
    assert "`${getNamespace()}:potion_effect`" in drinkable
    assert "const drinkableComponent: ItemCustomComponent = { onConsume };" in drinkable
    assert "export function thrownPotion(" in _read(tmp_path, "potion.ts")
    splash = _read(tmp_path, "splash.ts")
    assert "thrownPotion(projectile, potions, SPLASH)" in splash
    assert ":splash_range`" in splash
    assert "export function splash(\n\tdimension: Dimension,\n\tlocation: Vector3," in splash
    lingering = _read(tmp_path, "lingering.ts")
    assert "thrownPotion(projectile, potions, LINGERING)" in lingering
    assert ":lingering_radius`" in lingering
    assert ":lingering_lifetime`" in lingering
    for name in SCRIPTS:
        assert "NAMESPACE" not in _read(tmp_path, f"{name}.ts")


def test_every_import_points_at_a_written_module(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_typescript([_potion("stasis", 0)])

    for path in (tmp_path / OUTPUT_DIRECTORY).iterdir():
        for module in re.findall(r'from "\./(\w+)";', path.read_text(encoding="utf-8")):
            assert (path.parent / f"{module}.ts").is_file(), f"{path.name} imports ./{module}"


def test_rewriting_the_same_index_leaves_the_file_alone(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_typescript([_potion("stasis", 0)])
    index = tmp_path / OUTPUT_DIRECTORY / "index.ts"
    first = index.stat().st_mtime_ns
    write_typescript([_potion("stasis", 0)])
    assert index.stat().st_mtime_ns == first


def test_potion_objects_are_named_after_the_effect():
    assert potion_name(_potion("stasis", 0)) == "stasisPotion"
    assert potion_name(_potion("night_vision", 1)) == "nightVisionPotion"


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"key": "Night Vision"}, "key must be lowercase"),
        ({"color": "orange"}, "color must be a hex colour"),
    ],
)
def test_potion_explains_mistakes(values, message):
    with pytest.raises(ValueError, match=message):
        Potion(**({"key": "stasis", "title": "Stasis", "color": "#FF8000"} | values))


def test_ranges_must_be_above_zero():
    stasis = _potion("stasis", 0)
    with pytest.raises(ValueError, match=r"splash\(range=...\) must be above 0"):
        stasis.splash(range=0)
    with pytest.raises(ValueError, match=r"lingering\(lifetime=...\) must be above 0"):
        stasis.lingering(lifetime=-1)
    assert stasis.variants == []


def test_arguments_are_keyword_only():
    with pytest.raises(TypeError):
        Potion("stasis", "Stasis", "#FF8000")
    with pytest.raises(TypeError):
        _potion("stasis", 0).drinkable(1)


def test_variants_come_from_the_potion():
    stasis = _potion("stasis", 0)
    drinkable = stasis.drinkable(duration=240)
    strong = stasis.drinkable(amplifier=1, duration=120)
    assert stasis.variants == [drinkable, strong]
    assert drinkable is not strong
    assert strong._numeral == "II"


def test_brewing_needs_the_potions_own_variants():
    stasis, magnet = _potion("stasis", 0), _potion("magnet", 1)
    splash = stasis.splash()
    with pytest.raises(ValueError, match="brewing result isn't one of its variants"):
        magnet.brew(result=splash, reagent="minecraft:redstone")
    with pytest.raises(ValueError, match="brewing source isn't one of its variants"):
        stasis.brew(result=splash, reagent="minecraft:redstone", source=magnet.drinkable())


def test_queue_needs_variants_and_a_new_key(monkeypatch):
    monkeypatch.setattr(Potion, "_queued", [_potion("stasis", 0)])
    with pytest.raises(ValueError, match="has no variants"):
        _potion("magnet", 0).queue()
    duplicate = _potion("stasis", 0)
    duplicate.drinkable()
    with pytest.raises(ValueError, match="key 'stasis' is already queued"):
        duplicate.queue()


def test_queue_numbers_potions_and_brews_their_items(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    recipes = []

    class FakeRecipe:
        def __init__(self, name):
            self.name = name

        def unlock_items(self, items):
            pass

        def recipe(self, source, reagent, result):
            recipes.append((self.name, source, reagent, result))

        def queue(self):
            pass

    monkeypatch.setattr(Potion, "_queued", [])
    monkeypatch.setattr(Potion, "_projectile", "projectile")
    monkeypatch.setattr(potion_module, "PotionMixingRecipe", FakeRecipe)
    monkeypatch.setattr(potion_module, "add_render_controller", lambda *args: None)
    monkeypatch.setattr(
        Drinkable, "_create_item", lambda self, potion, index, *rest: f"{potion.key}_{index}"
    )
    monkeypatch.setattr(PotionVariant, "_setup_projectile", lambda *args: None)

    first = Potion(key="stasis", title="Stasis", color="#FF8000")
    first.drinkable()
    second = Potion(key="recall", title="Recall", color="#C710FF")
    drinkable = second.drinkable()
    strong = second.drinkable(amplifier=1)
    second.brew(result=drinkable, reagent="minecraft:copper_ingot")
    second.brew(result=strong, reagent="minecraft:redstone", source=drinkable)

    assert first.queue() == ["stasis_0"]
    assert second.queue() == ["recall_0", "recall_1"]
    assert (first.effect_id, second.effect_id) == (0, 1)
    assert recipes[0][2:] == ("minecraft:copper_ingot", "recall_0")
    assert recipes[1] == ("brew_recall_1", "recall_0", "minecraft:redstone", "recall_1")
    assert "\t0: stasisPotion,\n\t1: recallPotion,\n" in _read(tmp_path, "index.ts")


def test_drinkables_share_one_effect_component():
    component = PotionEffect(**Drinkable(amplifier=1, duration=240).effect(_potion("stasis", 0)))
    assert component.__json__() == {
        "test:potion_effect": {"id": "stasis", "amplifier": 1, "duration": 4800}
    }


def test_effect_parameters_mix_into_other_components():
    class TrapPotionEffect(PotionEffectParameters, BlockCustomComponent):
        identifier = "trap_potion_effect"
        trap_range: float = json_field()

    effect = Drinkable(duration=20).effect(_potion("burn", 0))
    assert TrapPotionEffect(**effect, trap_range=3).__json__() == {
        "test:trap_potion_effect": {"id": "burn", "amplifier": 0, "duration": 400, "trap_range": 3}
    }


def test_thrown_variants_set_their_projectile_type():
    events = {}

    class FakeEvent:
        def __init__(self, name):
            self.properties = events.setdefault(name, {})

        def add_property(self, name, value):
            self.properties[name] = value

    class FakeProjectile:
        class server:
            event = FakeEvent

    stasis = _potion("stasis", 3)
    Splash(amplifier=1, range=2.5)._setup_projectile(stasis, 1, FakeProjectile)
    Lingering(duration=20, radius=4, lifetime=10)._setup_projectile(stasis, 2, FakeProjectile)

    assert events["stasis_splash_1"] == {
        "duration": 2700,
        "amplifier": 1,
        "type": 1,
        "effect_id": 3,
        "splash_range": 2.5,
    }
    assert events["stasis_lingering_2"] == {
        "duration": 400,
        "amplifier": 0,
        "type": 2,
        "effect_id": 3,
        "lingering_radius": 4,
        "lingering_lifetime": 200,
    }
