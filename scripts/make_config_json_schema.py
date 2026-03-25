import contextlib
import json
import pathlib
from typing import Any

import msgspec.json

from wol_server.config import Config


JSON_SCHEMA_PATH = pathlib.Path(__file__).parents[1].joinpath('config.schema.json')


def generate_schema() -> dict[str, Any]:
    _, schema_defs = msgspec.json.schema_components([Config], ref_template='#/$defs/{name}')

    for schema_def in schema_defs.values():
        schema_def.pop('title', None)
        schema_def.pop('description', None)

    schema_defs['Target']['x-tombi-table-keys-order'] = 'schema'

    return {
        '$schema': 'https://json-schema.org/draft-07/schema',
        '$id': 'http://zeevro.com/schemas/wol-server/config.json',
        'title': 'wol-server configuration',
        'description': '',
        **schema_defs.pop('Config'),
        '$defs': schema_defs,
        'x-tombi-string-formats': ['ipv4', 'ipv6'],
    }


def main() -> None:
    new_text = json.dumps(generate_schema(), indent=2) + '\n'

    with contextlib.suppress(Exception):
        if new_text == JSON_SCHEMA_PATH.read_text():
            return

    JSON_SCHEMA_PATH.write_text(new_text)


if __name__ == '__main__':
    main()
