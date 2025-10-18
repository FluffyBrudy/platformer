from pathlib import Path
from dataclasses import dataclass

BASE_PATH = Path(__file__).parent
ASSETS_PATH = BASE_PATH / "assets" / "data" / "images"


FPS = 60
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
BASE_SPEED = 80


@dataclass
class Color:
    BG_COLOR = (14, 219, 248, 255)
    BLACK = (0, 0, 0, 255)
    RED = (255, 0, 0, 255)
