import pytest

from anvil_kit.world.potions import Brewing, Drinkable, PotionAPI, PotionConfig, Splash
from anvil_kit.world.potions.brewing import setup_brewing
from anvil_kit.world.potions.scaffold import OUTPUT_DIRECTORY, write_typescript


def _config(key: str, effect_id: int, **values) -> PotionConfig:
    return PotionConfig(
        effect_key=key,
        effect_title=key.title(),
        effect_id=effect_id,
        color_hex="#FF8000",
        variants=[Drinkable()],
        **values,
    )


def test_index_lists_each_potion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_typescript([_config("stasis", 0), _config("magnet", 7, splash_range=7, lingering_lifetime=10)])

    index = (tmp_path / OUTPUT_DIRECTORY / "index.ts").read_text(encoding="utf-8")
    assert "NAMESPACE" not in index
    assert "effectManager.addEffect(entity, potion.id" in (tmp_path / OUTPUT_DIRECTORY / "potions.ts").read_text(encoding="utf-8")
    assert '\t0: {\n\t\tid: "stasis",' in index
    assert '\t7: {\n\t\tid: "magnet",' in index
    assert "effectId" not in index
    assert "splashRange: 7," in index
    assert "lingeringLifetime: 200," in index
    assert 'color: "#ff8000",' in index
    assert "{{" not in index
    potions = (tmp_path / OUTPUT_DIRECTORY / "potions.ts").read_text(encoding="utf-8")
    assert "getNamespace()" in potions


def test_rewriting_the_same_index_leaves_the_file_alone(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_typescript([_config("stasis", 0)])
    index = tmp_path / OUTPUT_DIRECTORY / "index.ts"
    first = index.stat().st_mtime_ns
    write_typescript([_config("stasis", 0)])
    assert index.stat().st_mtime_ns == first


def test_potions_need_their_own_key_and_id(monkeypatch):
    monkeypatch.setattr(PotionAPI, "_configs", {"stasis": _config("stasis", 0)})
    with pytest.raises(ValueError, match="effect_key 'stasis'"):
        PotionAPI.register(_config("stasis", 1))
    with pytest.raises(ValueError, match="effect_id 0"):
        PotionAPI.register(_config("magnet", 0))


def test_brewing_refers_to_variants(monkeypatch):
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

    monkeypatch.setattr("anvil_kit.world.potions.brewing.PotionMixingRecipe", FakeRecipe)
    drinkable, splash = Drinkable(), Splash()
    config = _config("stasis", 0)
    config.variants = [drinkable, splash]
    config.brewing = [Brewing(drinkable, "redstone"), Brewing(splash, "gunpowder", source=drinkable)]

    setup_brewing(config, ["drink_item", "splash_item"])

    assert recipes[0][2:] == ("redstone", "drink_item")
    assert recipes[1] == ("brew_stasis_1", "drink_item", "gunpowder", "splash_item")

    config.brewing = [Brewing(Splash(), "gunpowder")]
    with pytest.raises(ValueError, match="isn't in its variants"):
        setup_brewing(config, ["drink_item", "splash_item"])
