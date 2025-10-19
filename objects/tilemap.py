from pygame import Rect
from typing import Dict, List, Literal, NamedTuple, Tuple, TypedDict, Union, cast
from typing import TYPE_CHECKING

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from pgdebug import pgdebug, pgdebug_rect


if TYPE_CHECKING:
    from pygame import Vector2, Surface
    from game import Game
    from editor import TTileTypes


NEIGHBOUR_OFFSET = [
    [0, 0],
    [0, -1],
    [-1, -1],
    [-1, 0],
    [-1, 1],
    [0, 1],
    [1, 1],
    [1, 0],
    [1, -1],
]


class Tile(NamedTuple):
    ttype: "TTileTypes"
    pos: tuple[int, int]
    variant: int
    rotaion: int = 0

    @staticmethod
    def is_physics_tile(tile: "Tile"):
        return tile.ttype == "grass" or tile.ttype == "stone"


class Tilemap:
    def __init__(self, game: "Game", tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap: Dict[Tuple[int, int], Tile] = {}
        self.offgrid_tiles: set[Tile] = set()

    def set_tilemap(self, tilemap: Dict[str, dict]):
        """
        Sets the internal tilemap from a dictionary of tile data.

        External format:
            dict[str, dict] with keys like "x,y", values like
            {'ttype': 'grass', 'pos': [x,y], 'variant': 0, 'rotaion': 0}

        Converts to internal format:
            Dict[Tuple[int,int], Tile]
        """
        for key, tile_data in tilemap.items():
            pos = cast(Tuple[int, int], tuple(int(n) for n in key.split(",")))
            tile_data["pos"] = list(pos)
            self.tilemap[pos] = Tile(
                ttype=tile_data["ttype"],
                pos=pos,
                variant=tile_data.get("variant", 0),
                rotaion=tile_data.get("rotaion", 0),
            )

    def set_offgrid_tiles(self, offgrid_tiles: list[list]):
        """
        Sets offgrid tiles from external serialized list format:
            list of lists: [ttype:str, pos:[x,y], variant:int, rotaion:int]

        Converts to internal format:
            set[Tile]
        """
        self.offgrid_tiles = set(
            Tile(ttype=t[0], pos=tuple(t[1]), variant=t[2], rotaion=t[3])
            for t in offgrid_tiles
        )

    def set_tilesize(self, tile_size: Tuple[int, int]):
        self.tile_size = tile_size[0]

    def tiles_around(self, pos: Tuple[int, int]) -> List[Tile]:
        tiles = []
        tile_loc_x, tile_loc_y = (
            int(pos[0] // self.tile_size),
            int(pos[1] // self.tile_size),
        )
        for offset_x, offset_y in NEIGHBOUR_OFFSET:
            target_loc = offset_x + tile_loc_x, offset_y + tile_loc_y
            if target_loc in self.tilemap:
                tiles.append(self.tilemap[target_loc])
        return tiles

    def physics_rects_around(self, pos: Tuple[int, int]) -> List[Rect]:
        physics_tiles = []
        tiles = self.tiles_around(pos)

        for tile in tiles:
            tile_pos = tile.pos[0] * self.tile_size, tile.pos[1] * self.tile_size

            if Tile.is_physics_tile(tile):
                physics_tiles.append(Rect(tile_pos, (self.tile_size, self.tile_size)))

        return physics_tiles

    def render(
        self,
        surface: "Surface",
        offset: Union["Vector2", Tuple[float, float]],
    ):
        for tile in self.offgrid_tiles:
            tile_pos = (
                tile.pos[0] - offset[0],
                tile.pos[1] - offset[1],
            )
            surface.blit(self.game.assets[tile.ttype][str(tile.variant)], tile_pos)

        start_x = int(offset[0] // self.tile_size)
        end_x = start_x + (SCREEN_WIDTH // self.tile_size + 2)
        start_y = int(offset[1] // self.tile_size)
        end_y = start_y + (SCREEN_HEIGHT // self.tile_size + 2)
        count = 0
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                location = (x, y)
                if location in self.tilemap:
                    tile = self.tilemap[location]
                    tile_pos = (
                        location[0] * self.tile_size - offset[0],
                        location[1] * self.tile_size - offset[1],
                    )
                    surface.blit(
                        self.game.assets[tile.ttype][str(tile.variant)], tile_pos
                    )
                    pgdebug_rect(surface, (*tile_pos, self.tile_size, self.tile_size))
                    count += 1
