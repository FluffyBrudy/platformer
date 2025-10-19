from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, Literal, Optional, Tuple, cast
from numpy import tile
import pygame
import json
from pygame import Event
from constants import (
    ASSETS_PATH,
    BASE_PATH,
    Color,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
)
from objects.tilemap import Tile, Tilemap
from utils.image_utils import load_key_images
from widget import NotificationBar, ToggleSlider


if TYPE_CHECKING:
    from objects.tilemap import Tile

TEventMapKey = Tuple[int, Optional[int]]
TEventMapValue = Callable[[Event], None]
TEventMapType = Dict[TEventMapKey, TEventMapValue]
TTileTypes = Literal["grass", "stone", "decor", "largedecor"]


class Editor:
    def __init__(self) -> None:
        pygame.init()

        self.screen: pygame.Surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.running: bool = True
        self.movement: list[bool] = [False, False, False, False]

        # Game assets
        self.assets: dict[TTileTypes, dict[str, pygame.Surface]] = {
            "grass": load_key_images(ASSETS_PATH / "tiles" / "grass", TILE_SIZE),
            "stone": load_key_images(ASSETS_PATH / "tiles" / "stone", 2),
            "decor": load_key_images(ASSETS_PATH / "tiles" / "decor", 2),
            "largedecor": load_key_images(ASSETS_PATH / "tiles" / "large_decor", 2),
        }

        # Tilemap
        self.tilelist = list(self.assets.keys())
        self.tile_group: int = 0
        self.tile_variant: int = 0
        self.tile_rotation: int = 0  # TODO: expreimental, not yet on tilemap
        self.tilemap: Tilemap = Tilemap(self, TILE_SIZE[0])  # type:ignore
        self.ongrid = False

        # Camera
        self.scroll: pygame.math.Vector2 = pygame.math.Vector2(0, 0)

        # mouse
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.left_just_released: bool = False
        self.right_just_released: bool = False

        # Event map
        self.event_map: TEventMapType = {
            (pygame.QUIT, None): lambda e: self.stop(),
            (pygame.MOUSEBUTTONDOWN, 1): lambda e: self.handle_mouse_click(
                True, "left"
            ),
            (pygame.MOUSEBUTTONDOWN, 3): lambda e: self.handle_mouse_click(
                True, "right"
            ),
            (pygame.MOUSEBUTTONUP, 1): lambda e: self.handle_mouse_click(False, "left"),
            (pygame.MOUSEBUTTONUP, 3): lambda e: self.handle_mouse_click(
                False, "right"
            ),
            (pygame.MOUSEBUTTONUP, 4): lambda e: self._handle_scroll(-1),
            (pygame.MOUSEBUTTONUP, 5): lambda e: self._handle_scroll(1),
            (pygame.KEYDOWN, pygame.K_LEFT): lambda e: self.set_move(0, True),
            (pygame.KEYDOWN, pygame.K_RIGHT): lambda e: self.set_move(1, True),
            (pygame.KEYDOWN, pygame.K_UP): lambda e: self.set_move(2, True),
            (pygame.KEYDOWN, pygame.K_DOWN): lambda e: self.set_move(3, True),
            (pygame.KEYUP, pygame.K_LEFT): lambda e: self.set_move(0, False),
            (pygame.KEYUP, pygame.K_RIGHT): lambda e: self.set_move(1, False),
            (pygame.KEYUP, pygame.K_UP): lambda e: self.set_move(2, False),
            (pygame.KEYUP, pygame.K_DOWN): lambda e: self.set_move(3, False),
            (pygame.KEYDOWN, pygame.K_r): lambda e: self.set_tile_rotation(-1),
            (pygame.KEYDOWN, pygame.K_g): lambda _: self.toggle_ongrid(),
            (pygame.KEYDOWN, pygame.K_s): lambda e: self.handle_hotkey(e.key),
        }

        # Global mouse pos
        self.mouse_pos = pygame.mouse.get_pos()

        # some extra widgets just for help
        self.font = pygame.font.SysFont(None, 15)
        self.ongrid_toggle = ToggleSlider(
            (SCREEN_WIDTH - 55, 0),
            (55, 25),
            ["ongrid", "ongrid"],
            self.font,
            self.toggle_ongridbtn_callback,
        )
        self.notification_bar = NotificationBar(self.screen)

        self.load()

    def save(self):
        self.notification_bar.display_start("saving map data...")
        try:
            dump_mapdata(self.tilemap)
            self.notification_bar.display_end("success")
        except json.JSONDecodeError:
            print("bad json chunks")
            self.notification_bar.display_end("parsing error")

    def load(self):
        data = load_tilemap_data(BASE_PATH / "mapdata.json")
        if not data:
            return

        if data.get("tilemap", None) is not None:
            self.tilemap.set_tilemap(data.get("tilemap"))
        if data.get("offgrid", None) is not None:
            self.tilemap.set_offgrid_tiles(data.get("offgrid"))
        if data.get("tile_size", None) is not None:
            self.tilemap.set_tilesize(data.get("tile_size"))

    def toggle_ongridbtn_callback(self):
        """callback for ongrid_toggle button only
        not intended for regular use
        """
        self.ongrid = not self.ongrid

    def toggle_ongrid(self):
        self.ongrid = not self.ongrid
        self.ongrid_toggle.toggle()

    def stop(self) -> None:
        self.running = False

    def handle_hotkey(self, key: int):
        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_CTRL and key == pygame.K_s:
            self.save()

    def handle_mouse_click(self, state: bool, button: Literal["left", "right"]) -> None:
        if button == "left":
            self.left_pressed = state
        elif button == "right":
            self.right_pressed = state
        if not state and button == "left":
            self.left_just_released = True
        elif button == "right" and not state:
            self.right_just_released = True

    def _handle_scroll(self, direction: Literal[1, -1]) -> None:
        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_SHIFT:
            self.shift_and_scroll(direction)
        else:
            self.mouse_scroll(direction)

    def mouse_scroll(self, direction: Literal[1, -1]) -> None:
        self.tile_group = (self.tile_group + direction) % len(self.tilelist)
        self.tile_variant = 0

    def shift_and_scroll(self, direction: Literal[1, -1]) -> None:
        current_key = self.tilelist[self.tile_group]
        current_tile = self.assets[current_key]
        variant_count = len(current_tile)
        self.tile_variant = (self.tile_variant + direction) % variant_count

    def set_move(self, index: int, state: bool) -> None:
        self.movement[index] = state

    def set_tile_rotation(self, direction: Literal[1, -1]):
        self.tile_rotation += direction * 90

    def get_current_tile_image(self) -> pygame.Surface:
        current_tile = self.assets[self.tilelist[self.tile_group]]
        variant = current_tile[str(self.tile_variant)]
        return variant.copy()

    def convert_coor_to_grid(self, omit_offset=False):
        offset_flag = 1 - omit_offset
        mouse_x, mouse_y = self.mouse_pos
        tile_x, tile_y = (
            int((mouse_x + self.scroll[0] * offset_flag) // TILE_SIZE[0]),
            int((mouse_y + self.scroll[1] * offset_flag) // TILE_SIZE[1]),
        )
        return tile_x, tile_y

    def get_raw_world_coor(self, omit_offset=False):
        offset_flag = 1 - omit_offset
        mouse_x, mouse_y = self.mouse_pos
        tile_x, tile_y = (
            int(mouse_x + self.scroll[0] * offset_flag),
            int(mouse_y + self.scroll[1] * offset_flag),
        )
        return tile_x, tile_y

    def preview_selected_ongrid_tile(self):
        tile_img = self.get_current_tile_image()
        tile_img.set_alpha(150)
        pos_x, pos_y = self.convert_coor_to_grid(omit_offset=True)
        self.screen.blit(tile_img, (pos_x * TILE_SIZE[0], pos_y * TILE_SIZE[1]))

    def preview_selected_offgrid_tile(self):
        tile_img = self.get_current_tile_image()
        tile_img.set_alpha(150)
        pos_x, pos_y = self.get_raw_world_coor(omit_offset=True)
        self.screen.blit(tile_img, (pos_x, pos_y))

    def plot_tile_ongrid(self):
        pos = self.convert_coor_to_grid()
        ttype = self.tilelist[self.tile_group]
        self.tilemap.tilemap[pos] = Tile(
            ttype, pos, self.tile_variant, self.tile_rotation
        )

    def remove_tile_ongrid(self):
        pos = self.convert_coor_to_grid()
        self.tilemap.tilemap.pop(pos, None)

    def plot_tile_offgrid(self):
        pos = self.get_raw_world_coor()
        ttype = self.tilelist[self.tile_group]
        self.tilemap.offgrid_tiles.add(
            Tile(ttype, pos, self.tile_variant, self.tile_rotation)
        )

    def remove_tile_offgrid(self):
        pos = self.get_raw_world_coor()
        removable_tile: Optional[Tile] = None
        for tile in self.tilemap.offgrid_tiles:
            tilesurf = self.assets[self.tilelist[self.tile_group]][str(tile.variant)]
            rect = pygame.Rect(*tile.pos, *tilesurf.size)
            if rect.collidepoint(pos):
                removable_tile = tile
                break
        if removable_tile is not None:
            self.tilemap.offgrid_tiles.remove(removable_tile)

    def camera_movement(self):
        self.scroll[0] += int((self.movement[1] - self.movement[0]) * 2)
        self.scroll[1] += int((self.movement[3] - self.movement[2]) * 2)

    def handle_event(self) -> None:
        self.left_just_released = False
        self.right_just_released = False
        for event in pygame.event.get():
            self.ongrid_toggle.handle_event(event)
            event_attr = getattr(event, "key", None) or getattr(event, "button", None)
            unary_event = self.event_map.get((event.type, None))
            handler = self.event_map.get((event.type, event_attr)) or unary_event
            if handler:
                handler(event)

    def update(self) -> None:
        self.mouse_pos = pygame.mouse.get_pos()

        self.ongrid_toggle.update()
        self.camera_movement()

        if self.ongrid_toggle.is_hovered():
            return

        if self.ongrid and self.left_pressed:
            self.plot_tile_ongrid()
        elif self.ongrid and self.right_pressed:
            self.remove_tile_ongrid()
        elif not self.ongrid and self.left_just_released:
            self.plot_tile_offgrid()
        elif not self.ongrid and self.right_just_released:
            self.remove_tile_offgrid()

    def draw(self) -> None:
        self.tilemap.render(self.screen, self.scroll)
        self.ongrid_toggle.draw(self.screen)

        if self.ongrid_toggle.is_hovered():
            return
        if self.ongrid:
            self.preview_selected_ongrid_tile()
        else:
            self.preview_selected_offgrid_tile()
        self.notification_bar.draw()

    def run(self) -> None:
        while self.running:
            self.screen.fill(Color.BLACK)
            self.handle_event()
            self.update()
            self.draw()
            pygame.display.flip()
        pygame.quit()


def dump_mapdata(data: Tilemap):
    with open("mapdata.json", "w") as fp:
        serialized_tilemap_data = {
            ",".join(map(str, k)): v._asdict() for k, v in data.tilemap.items()
        }
        json.dump(
            {
                "tilemap": serialized_tilemap_data or dict(),
                "offgrid": list(data.offgrid_tiles) or [],
                "tile_size": (TILE_SIZE),
            },
            fp,
            indent=4,
        )


def load_tilemap_data(path: Path):
    if path.suffix != ".json":
        print("not map data")
        return None
    try:
        with open(path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("file not found")
    except JSONDecodeError:
        print("error parsing json file")
    except Exception as other_err:
        print(f"{other_err}")
    return None


if __name__ == "__main__":
    editor = Editor()
    editor.run()
