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


class Flight(BaseModel):
    ident: str
    fa_flight_id: str
    status: str
    blocked: bool
    diverted: bool
    cancelled: bool
    position_only: bool
    ...


class PhonyplaneConfig(BaseModel):
    api_aeroapi_url: str
    api_aeroapi_key: str
    api_telegram_hash: str
    api_telegram_id: int
    target_chat_id: int
    journey: list[str]
    flights: dict[str, Flight] = {}


PHONYPLANE_EXAMPLE = """
api_aeroapi_url = "https://api.aeroapi.com"
api_aeroapi_key = "xxx"
api_telegram_hash = "xxx"
api_telegram_id = 999
target_chat_id = 999
journey = ["ABC123"]

[flights.ABC123]
ident = "ABC123"
fa_flight_id = "xxx"
status = "active"
blocked = false
diverted = false
cancelled = false
position_only = false
"""


def test():
    """recreation of https://github.com/markjoshwel/tomlantic/issues/10"""

    toml = tomlantic.ModelBoundTOML(PhonyplaneConfig, loads(PHONYPLANE_EXAMPLE))
    _ = dumps(toml.model_dump_toml())  # this should work

    # > the following pydantic model, of course, does work when adding new keys to flights
    # > but er, dumping to toml results in:
    # > ...
    # > tomlkit.exceptions.ConvertError: Unable to convert an object of <class '__main__.Flight'> to a TOML item

    # recreate: add to flights
    toml.model.flights["DEF456"] = Flight(
        ident="DEF456",
        fa_flight_id="xxx",
        status="active",
        blocked=False,
        diverted=False,
        cancelled=False,
        position_only=False,
    )
    _ = toml.model_dump_toml()


if __name__ == "__main__":
    test()
