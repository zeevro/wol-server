#!/usr/bin/env python3
import json
import pathlib
import subprocess
from typing import NotRequired, TypedDict


SIZES = [32, 48, 72, 96, 128, 256, 512]

APP_ROOT = pathlib.Path(__file__).parents[1] / 'src/wol_server'
STATIC_DIR = APP_ROOT / 'static'
ICON_DIR = STATIC_DIR / 'icon'
MANIFEST_PATH = STATIC_DIR / 'manifest.json'
SVG_FN = 'icon.svg'

MANIFEST_ICON_DIR = ICON_DIR.relative_to(MANIFEST_PATH.parent)


class IconData(TypedDict):
    src: str
    sizes: NotRequired[str]
    type: NotRequired[str]
    purpose: NotRequired[str]


class Manifest(TypedDict, total=False):
    icons: list[IconData]


def generate(size: int) -> IconData:
    if not size:
        return {'src': str(MANIFEST_ICON_DIR / SVG_FN), 'sizes': 'any', 'type': 'image/svg+xml'}
    sz = f'{size}x{size}'
    fn = f'icon-{size}.png'
    subprocess.check_call(['ffmpeg', '-y', '-i', SVG_FN, '-s', sz, fn], cwd=ICON_DIR)  # noqa: S603, S607
    return {'src': str(MANIFEST_ICON_DIR / fn), 'sizes': sz, 'type': 'image/png'}


def main() -> None:
    manifest: Manifest = json.loads(MANIFEST_PATH.read_bytes())
    manifest['icons'] = [generate(s) for s in [*SIZES, 0]]
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
