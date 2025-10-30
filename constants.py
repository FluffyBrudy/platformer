from pathlib import Path
from dataclasses import dataclass

BASE_PATH = Path(__file__).parent
ASSETS_PATH = BASE_PATH / "assets" / "data" / "images"


FPS = 60
SCREEN_WIDTH = 704 + 32 * 5
SCREEN_HEIGHT = 512 + 32 * 5
BASE_SPEED = 100
TILE_SIZE = (32, 32)


BASE_DECAY_FACTOR = 0.1

DASH_POWER = 60
DASH_SPEED_MULT = 5
DASH_DECAY_THRESHOLD = 50
JUMP_BASE = -3

BASE_PROJECTILE_RANGE = 300


@dataclass
class Color:
    BG_COLOR = (14, 219, 248, 255)
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)
    RED = (255, 0, 0, 255)
    GRAY = (100, 100, 100, 255)
    LIGHT_GRAY = (200, 200, 200, 255)
