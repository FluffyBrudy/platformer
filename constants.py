from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, TypedDict

BASE_PATH = Path(__file__).parent
ASSETS_PATH = BASE_PATH / "assets" / "data" / "images"


FPS = 60
SCREEN_WIDTH = 704
SCREEN_HEIGHT = 512
BASE_SPEED = 100
TILE_SIZE = (32, 32)


@dataclass
class Color:
    BG_COLOR = (14, 219, 248, 255)
    BLACK = (0, 0, 0, 255)
    RED = (255, 0, 0, 255)
