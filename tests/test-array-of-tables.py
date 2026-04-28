# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pydantic",
#     "tomlantic @ ${PROJECT_ROOT}/",
#     "tomlkit",
# ]
# ///


from pydantic import BaseModel
from tomlkit import dumps, loads  # pyright: ignore[reportUnknownVariableType]

import tomlantic


class Item(BaseModel):
    name: str
    value: int
    active: bool


class ConfigWithArray(BaseModel):
    title: str
    items: list[Item] = []


ARRAY_TEST_EXAMPLE = """
title = "Test Array"

[[items]]
name = "first"
value = 1
active = true

[[items]]
name = "second"
value = 2
active = false
"""


def build_toml():
    return tomlantic.ModelBoundTOML(ConfigWithArray, loads(ARRAY_TEST_EXAMPLE))


def test_dump_round_trip():
    """test array of tables (list[BaseModel])"""

    toml = build_toml()
    _ = dumps(toml.model_dump_toml())


def test_modify_existing_item():
    toml = build_toml()
    toml.model.items[0].value = 10
    dumped = dumps(toml.model_dump_toml())
    assert "value = 10" in dumped
    assert "value = 2" in dumped


def add_third_item(toml):
    toml.model.items.append(
        Item(
            name="third",
            value=3,
            active=True,
        )
    )


def test_add_new_item():
    toml = build_toml()
    add_third_item(toml)
    dumped = dumps(toml.model_dump_toml())
    assert 'name = "third"' in dumped


def test_remove_item_rebuilds_array():
    toml = build_toml()
    add_third_item(toml)
    toml.model.items.pop(0)
    dumped = dumps(toml.model_dump_toml())
    assert 'name = "first"' not in dumped
    assert 'name = "second"' in dumped
    assert 'name = "third"' in dumped


if __name__ == "__main__":
    test_dump_round_trip()
    test_modify_existing_item()
    test_add_new_item()
    test_remove_item_rebuilds_array()
