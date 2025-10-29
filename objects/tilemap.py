from pygame import Rect, Vector2
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    List,
    Sequence,
    Tuple,
    Union,
    cast,
)
from typing import TYPE_CHECKING
import json
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE


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


@dataclass
class Tile:
    ttype: "TTileTypes"
    pos: tuple[int, int]
    variant: int
    rotation: int = 0

    @staticmethod
    def is_physics_tile(tile: "Tile"):
        return tile.ttype == "grass" or tile.ttype == "stone"

    def copy(self):
        return Tile(self.ttype, self.pos, self.variant)


class Tilemap:
    def __init__(self, game: "Game", tile_size: Union[Tuple[int, int], int] = 16):
        self.game = game
        self.tile_size = cast(
            Tuple[int, int],
            (tile_size if type(tile_size) == tuple else (tile_size, tile_size)),
        )
        self.tilemap: Dict[Tuple[int, int], Tile] = {}
        self.offgrid_tiles: List[Tile] = []
        self.offgrid_cull_min_pos = Vector2(-2 * TILE_SIZE[0], -2 * TILE_SIZE[1])
        self.offgrid_cull_max_pos = Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)

    def solid_tile_check(self, pos: Tuple[int, int]):
        tile_loc_x = int(pos[0] // self.tile_size[0])
        tile_loc_y = int(pos[1] // self.tile_size[1])
        tile_loc = (tile_loc_x, tile_loc_y)
        if tile_loc in self.tilemap and Tile.is_physics_tile(self.tilemap[tile_loc]):
            return self.tilemap[tile_loc]
        return None

    def tiles_around(self, pos: Tuple[int, int]) -> List[Tile]:
        tiles = []
        tile_loc_x, tile_loc_y = (
            int(pos[0] // self.tile_size[0]),
            int(pos[1] // self.tile_size[1]),
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
            tile_pos = tile.pos[0] * self.tile_size[0], tile.pos[1] * self.tile_size[1]

            if Tile.is_physics_tile(tile):
                physics_tiles.append(Rect(tile_pos, (self.tile_size)))  # type: ignore

        return physics_tiles

    def extract(self, id_pairs: Sequence[Tuple[str, int]], keep=False):
        """
        Args:
            id_pairs: Sequence of (tile_type, variant)
            keep: boolean value indicating wether to keep or remove tiles
        """
        matches: List[Tile] = []

        for tile in self.offgrid_tiles.copy():
            if (tile.ttype, tile.variant) in id_pairs:
                matches.append(tile)
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile.ttype, tile.variant) in id_pairs:
                matches.append(tile)
                matches[-1].pos = (
                    self.tile_size[0] * matches[-1].pos[0],
                    self.tile_size[1] * matches[-1].pos[1],
                )
                if not keep:
                    del self.tilemap[loc]
        return matches

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

            if (
                self.offgrid_cull_min_pos.x
                <= tile_pos[0]
                <= self.offgrid_cull_max_pos.x
                and self.offgrid_cull_min_pos.y
                <= tile_pos[1]
                <= self.offgrid_cull_max_pos.y
            ):
                surface.blit(self.game.assets[tile.ttype][str(tile.variant)], tile_pos)

        start_x = int(offset[0] // self.tile_size[0])
        end_x = start_x + (SCREEN_WIDTH // self.tile_size[0] + 2)
        start_y = int(offset[1] // self.tile_size[1])
        end_y = start_y + (SCREEN_HEIGHT // self.tile_size[1] + 2)
        count = 0
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                location = (x, y)
                if location in self.tilemap:
                    tile = self.tilemap[location]
                    tile_pos = (
                        location[0] * self.tile_size[0] - offset[0],
                        location[1] * self.tile_size[1] - offset[1],
                    )
                    surface.blit(
                        self.game.assets[tile.ttype][str(tile.variant)], tile_pos
                    )
                    # pgdebug_rect(surface, (*tile_pos, self.tile_size, self.tile_size))
                    count += 1

    def dump_mapdata(self, path: Path = Path("mapdata.json")):
        serialized_tilemap_data = {
            ",".join(map(str, k)): {
                "ttype": v.ttype,
                "pos": list(v.pos),
                "variant": v.variant,
                "rotation": v.rotation,
            }
            for k, v in self.tilemap.items()
        }

        serialized_offgrid_tiles = [
            [t.ttype, list(t.pos), t.variant, t.rotation] for t in self.offgrid_tiles
        ]

        with open(path, "w") as fp:
            json.dump(
                {
                    "tilemap": serialized_tilemap_data,
                    "offgrid": serialized_offgrid_tiles,
                    "tile_size": self.tile_size,
                },
                fp,
            )
        print(f"Tilemap saved to {path}")

    def load_tilemap_data(self, path: Path):
        if path.suffix != ".json":
            print("Not a map data file")
            return

        try:
            with open(path, "r") as file:
                data = json.load(file)

            self.tilemap = {}
            for key, tile_data in data.get("tilemap", {}).items():
                pos = cast(Tuple[int, int], tuple(int(n) for n in key.split(",")))
                self.tilemap[pos] = Tile(
                    ttype=tile_data["ttype"],
                    pos=pos,
                    variant=tile_data.get("variant", 0),
                    rotation=tile_data.get("rotation", 0),
                )

            self.offgrid_tiles = [
                Tile(ttype=t[0], pos=tuple(t[1]), variant=t[2], rotation=t[3])
                for t in data.get("offgrid", [])
            ]

            self.tile_size = data.get("tile_size", self.tile_size)

            print(f"Tilemap loaded from {path}")

        except FileNotFoundError:
            print("File not found")
        except json.JSONDecodeError:
            print("Error parsing JSON file")
        except Exception as e:
            print(f"Unexpected error: {e}")
