from pygame import Rect, Surface
from typing import Dict, List, Literal, NamedTuple, Sequence, Tuple
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from game import Game


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
    ttype: Literal["grass", "water", "stone"]
    pos: tuple[int, int]
    variant: int

    @staticmethod
    def is_physics_tile(tile: "Tile"):
        return tile.ttype == "grass" or tile.ttype == "stone"


class Tilemap:
    def __init__(self, game: "Game", tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap: Dict[Tuple[int, int], Tile] = {}
        self.offgrid_tiles: List[Tile] = []

        for i in range(10):
            grass_loc = (3 + i, 10)
            stone_loc = (10, 5 + i)
            self.tilemap[grass_loc] = Tile("grass", grass_loc, 1)
            self.tilemap[stone_loc] = Tile("stone", stone_loc, 1)

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

    def physics_rect_around(self, pos: Tuple[int, int]) -> List[Rect]:
        physics_tiles = []
        tiles = self.tiles_around(pos)

        for tile in tiles:
            tile_pos = tile.pos[0] * self.tile_size, tile.pos[1] * self.tile_size
            if Tile.is_physics_tile(tile):
                physics_tiles.append(Rect(tile_pos, (self.tile_size, self.tile_size)))

        return physics_tiles

    def render(self, surface: Surface):
        for tile in self.offgrid_tiles:
            surface.blit(self.game.assets[tile.ttype][str(tile.variant)], tile.pos)

        for location in self.tilemap:
            tile = self.tilemap[location]
            tile_pos = location[0] * self.tile_size, location[1] * self.tile_size
            surface.blit(self.game.assets[tile.ttype][str(tile.variant)], tile_pos)
