import pytest
from anvil.api.actors.materials import MaterialsObject
from anvil.lib import config
from anvil.lib.lib import AnvilIO
from anvil.lib.translator import AnvilTranslator

from anvil_kit.actors.materials import add_entity_outline

jsonschema = pytest.importorskip("jsonschema")


@pytest.fixture(autouse=True)
def project(monkeypatch):
    monkeypatch.setattr(MaterialsObject, "_instance", None)
    monkeypatch.setattr(AnvilTranslator, "add_localization_entry", lambda *a: None)
    with config.override(NAMESPACE="testns", PROJECT_NAME="proj"):
        yield


def _check(file):
    schema = type(file).__schema__()
    jsonschema.Draft202012Validator.check_schema(schema)
    exported = AnvilIO._normalize_json_like(file._document)
    jsonschema.validate(exported, schema, cls=jsonschema.Draft202012Validator)
    return exported


def test_entity_outline_materials():
    add_entity_outline(xray_mode=True).queue()
    materials = _check(MaterialsObject())["materials"]
    assert materials["testns.entity_outline_base:entity_alphatest"]["stencilRef"] == 3
    outline = materials["testns.entity_outline:entity_alphatest"]
    assert outline["depthFunc"] == "Always"
    assert outline["frontFace"] == {"stencilFunc": "NotEqual"}
