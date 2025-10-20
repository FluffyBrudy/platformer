from typing import Tuple


def sorted_pos_tuple(*coor: Tuple[int, int]):
    return tuple(sorted(coor))
