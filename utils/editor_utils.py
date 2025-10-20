from typing import Sequence, Tuple


def sorted_pos_tuple(*coor: Tuple[int, int]):
    return tuple(sorted(coor))
