from typing import Annotated, Any, Literal

import msgspec.toml
import platformdirs

from .network import check_alive, mac_bytes


class Target(msgspec.Struct, kw_only=True, forbid_unknown_fields=True):
    _name: Annotated[
        str,
        msgspec.Meta(
            description='Name to show in main table',
        ),
    ] = msgspec.field(name='name', default='')

    ip: Annotated[
        str,
        msgspec.Meta(
            description='IP address for broadcast',
            examples=['192.168.0.14', 'fd00:7a65:6576:726f::52'],
            extra_json_schema={'anyOf': [{'format': 'ipv4'}, {'format': 'ipv6'}]},
        ),
    ]

    mac_str: Annotated[
        str,
        msgspec.Meta(
            description='MAC address for magic packet',
            pattern=r'^[0-9A-Fa-f]{2}([\s:-]*[0-9A-Fa-f]{2}){5}$',
        ),
    ] = msgspec.field(name='mac')

    @property
    def name(self) -> str:
        return self._name or self.ip

    @property
    def mac(self) -> bytes:
        return mac_bytes(self.mac_str)

    @property
    def is_alive(self) -> bool:
        return check_alive(self.ip)

    def json(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'ip': self.ip,
            'mac': self.mac_str,
            'isAlive': self.is_alive,
        }


class Config(msgspec.Struct, kw_only=True, forbid_unknown_fields=True, rename='kebab'):
    log_level: Annotated[
        Literal['debug', 'info', 'warning', 'error', 'critical'],
        msgspec.Meta(
            description='Log level for server',
        ),
    ] = 'info'

    port: Annotated[
        int,
        msgspec.Meta(
            description='WoL packet destination port',
            gt=0,
            le=0xFFFF,
        ),
    ] = 9

    wake_check_time: Annotated[
        float,
        msgspec.Meta(
            description='Time to wait after wake before checking liveness',
            ge=0.5,
            le=10,
        ),
    ] = 8

    targets: Annotated[
        list[Target],
        msgspec.Meta(
            description='Target hosts',
        ),
    ] = msgspec.field(name='target', default_factory=list)


def load_config() -> Config:
    for d in platformdirs.PlatformDirs('wol-server', appauthor=False).iter_config_paths():
        try:
            return msgspec.toml.decode(d.joinpath('config.toml').read_bytes(), type=Config)
        except FileNotFoundError:
            pass
    return Config()
