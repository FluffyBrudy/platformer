from typing import TYPE_CHECKING, Callable, Dict, Literal, Optional, Tuple
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
from utils.editor_utils import sorted_pos_tuple
from widget import KeyboardHelp, NotificationBar


if TYPE_CHECKING:
    from objects.tilemap import Tile

TEventMapKey = Tuple[int, Optional[int]]
TEventMapValue = Callable[[Event], None]
TEventMapType = Dict[TEventMapKey, TEventMapValue]
TTileTypes = Literal["grass", "stone", "decor", "largedecor", "enemy"]


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
            "enemy": load_key_images(ASSETS_PATH / "tiles" / "spawners", 2),
        }

        # Tilemap
        self.tilelist = list(self.assets.keys())
        self.tile_group: int = 0
        self.tile_variant: int = 0
        self.tile_rotation: int = 0  # TODO: expreimental, not yet on tilemap
        self.tilemap: Tilemap = Tilemap(self, TILE_SIZE[0])  # type:ignore
        self.ongrid = True

        # autotile
        self.autotile_types = ("grass", "stone")
        self.autotile_map = {
            sorted_pos_tuple((0, 1), (1, 0)): 0,
            sorted_pos_tuple((1, 0), (0, 1), (-1, 0)): 1,
            sorted_pos_tuple((0, 1), (-1, 0)): 2,
            sorted_pos_tuple((-1, 0), (0, -1), (0, 1)): 3,
            sorted_pos_tuple((0, -1), (-1, 0)): 4,
            sorted_pos_tuple((0, -1), (1, 0), (-1, 0)): 5,
            sorted_pos_tuple((0, -1), (1, 0)): 6,
            sorted_pos_tuple((0, -1), (0, 1), (1, 0)): 7,
            sorted_pos_tuple((0, -1), (0, 1), (1, 0), (-1, 0)): 8,
        }

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
            (pygame.KEYDOWN, pygame.K_t): lambda e: self.autotile(),
            (pygame.KEYDOWN, pygame.K_s): lambda e: self.handle_hotkey(e.key),
            (pygame.KEYDOWN, pygame.K_h): lambda e: self.keyboard_help.toggle(),
        }

        # Global mouse pos
        self.mouse_pos = pygame.mouse.get_pos()

        # some extra widgets
        self.font = pygame.font.SysFont(None, 15)
        self.notification_bar = NotificationBar(self.screen)
        self.keyboard_help = KeyboardHelp(pygame.font.SysFont(None, 25))

        self.load()

    def save(self):
        self.notification_bar.display_start("saving map data...")
        try:
            self.tilemap.dump_mapdata(BASE_PATH / "mapdata.json")
            self.notification_bar.display_end("success")
        except json.JSONDecodeError:
            print("bad json chunks")
            self.notification_bar.display_end("parsing error")

    def load(self):
        data = self.tilemap.load_tilemap_data(BASE_PATH / "mapdata.json")
        if not data:
            return

    def autotile(self):
        for loc in self.tilemap.tilemap:
            tile = self.tilemap.tilemap[loc]
            neighbours = set()

            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = tile.pos[0] + shift[0], tile.pos[1] + shift[1]
                if check_loc in self.tilemap.tilemap:
                    if self.tilemap.tilemap[check_loc].ttype == tile.ttype:
                        neighbours.add(shift)

            neighbours = tuple(sorted(tuple(neighbours)))
            if tile.ttype in self.autotile_types and neighbours in self.autotile_map:
                self.tilemap.tilemap[tile.pos] = Tile(
                    tile.ttype, tile.pos, self.autotile_map[neighbours]
                )

    def toggle_ongrid(self):
        self.ongrid = not self.ongrid

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
        grid_x, grid_y = self.convert_coor_to_grid()
        draw_x = grid_x * TILE_SIZE[0] - self.scroll[0]
        draw_y = grid_y * TILE_SIZE[1] - self.scroll[1]
        self.screen.blit(tile_img, (draw_x, draw_y))

    def preview_selected_offgrid_tile(self):
        tile_img = self.get_current_tile_image()
        tile_img.set_alpha(150)
        pos_x, pos_y = self.get_raw_world_coor(omit_offset=True)
        self.screen.blit(
            tile_img, (pos_x - tile_img.width // 2, pos_y - tile_img.height // 2)
        )

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
        w, h = self.get_current_tile_image().size
        ttype = self.tilelist[self.tile_group]
        pos_x, pos_y = self.get_raw_world_coor()
        pos = (pos_x - w // 2, pos_y - h // 2)
        self.tilemap.offgrid_tiles.append(
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
            event_attr = getattr(event, "key", None) or getattr(event, "button", None)
            unary_event = self.event_map.get((event.type, None))
            handler = self.event_map.get((event.type, event_attr)) or unary_event
            if handler:
                handler(event)

    def update(self) -> None:
        self.mouse_pos = pygame.mouse.get_pos()

        self.camera_movement()

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

        if self.ongrid:
            self.preview_selected_ongrid_tile()
        else:
            self.preview_selected_offgrid_tile()
        self.notification_bar.draw()
        self.keyboard_help.draw(self.screen)

    def run(self) -> None:
        while self.running:
            self.screen.fill(Color.BLACK)
            self.handle_event()
            self.update()
            self.draw()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    editor = Editor()
    editor.run()
