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


def test():
    """test array of tables (list[BaseModel])"""

    toml = tomlantic.ModelBoundTOML(ConfigWithArray, loads(ARRAY_TEST_EXAMPLE))

    # Test 1: initial dump should work
    _ = dumps(toml.model_dump_toml())

    # Test 2: modify existing item
    toml.model.items[0].value = 10
    dumped = dumps(toml.model_dump_toml())
    assert "value = 10" in dumped
    assert "value = 2" in dumped

    # Test 3: add new item
    toml.model.items.append(
        Item(
            name="third",
            value=3,
            active=True,
        )
    )
    dumped = dumps(toml.model_dump_toml())
    assert 'name = "third"' in dumped

    # Test 4: remove item (test array rebuild)
    toml.model.items.pop(0)
    dumped = dumps(toml.model_dump_toml())
    assert 'name = "first"' not in dumped
    assert 'name = "second"' in dumped
    assert 'name = "third"' in dumped


if __name__ == "__main__":
    test()
