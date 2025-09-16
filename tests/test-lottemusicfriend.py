# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pydantic",
#     "tomlantic @ ${PROJECT_ROOT}/",
#     "tomlkit",
# ]
# ///

from typing import Literal

from pydantic import BaseModel
from tomlkit import dumps, loads

from tomlantic import ModelBoundTOML


class TelegramServiceConfig(BaseModel):
    api_id: int
    api_hash: str


class TelegramTargetConfig(BaseModel):
    channel_id: int
    send_message_as_id: int | None = None  # optional


class TelegramConfig(BaseModel):
    service: TelegramServiceConfig
    target: TelegramTargetConfig


class LastFMServiceConfig(BaseModel):
    url: Literal["https://www.last.fm", "https://libre.fm"] = "https://www.last.fm"
    api_key: str
    api_secret: str
    username: str
    md5_password: str


class LastFMTargetConfig(BaseModel):
    username: str


class LastFMConfig(BaseModel):
    service: LastFMServiceConfig
    target: LastFMTargetConfig


class LotteMusicFriendConfig(BaseModel):
    lastfm: LastFMConfig
    telegram: TelegramConfig


EmptyLotteMusicFriendConfigText: str = """
[telegram]

# https://my.telegram.org
service.api_id = "000"
service.api_hash = "xxx"

target.channel_id = "000"
target.send_message_as_id = "000"  # optional

[lastfm]

service.url = "https://www.last.fm"

# https://www.last.fm/api/account/create
service.api_key = "xxx"
service.api_secret = "xxx"
service.username = "xxx"
service.md5_password = "xxx"

target.username = "xxx"
"""


def test() -> None:
    model = ModelBoundTOML(
        LotteMusicFriendConfig, loads(EmptyLotteMusicFriendConfigText)
    )

    ModelBoundTOML(
        LotteMusicFriendConfig,
        loads(
            EmptyLotteMusicFriendConfigText.replace(
                "https://www.last.fm", "https://libre.fm"
            )
        ),
    )

    try:
        ModelBoundTOML(
            LotteMusicFriendConfig,
            loads(
                EmptyLotteMusicFriendConfigText.replace(
                    "https://www.last.fm", "https://joshwel.co"
                )
            ),
        )
    except Exception:
        pass
    else:
        assert "field assigned a value not within literal choices"

    dumps(model.model_dump_toml())


if __name__ == "__main__":
    test()
