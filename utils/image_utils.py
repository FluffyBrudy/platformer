import sys
import re
import pygame
from pathlib import Path
from typing import Sequence, Tuple, Union
from constants import Color
from PIL import Image
import numpy as np


def load_image(
    path: Path,
    scale_ratio_or_size: Union[Tuple[float, float], float] = 1.0,
    colorkey: Tuple[int, int, int, int] = Color.BLACK,
    trim_space=False,
):
    if not path.exists():
        print(f"[WARNING]: {path} not found")
        sys.exit(1)

    image = load_pil_img_to_pygame_surf_np(path, colorkey[:3], trim_space)

    if type(scale_ratio_or_size) == float or type(scale_ratio_or_size) == int:
        scaled_image = pygame.transform.scale_by(image, scale_ratio_or_size)
        return scaled_image
    elif len(scale_ratio_or_size) > 1:  # type:ignore
        scaled_image = pygame.transform.scale(image, scale_ratio_or_size)  # type: ignore
        return scaled_image
    else:
        print(f"[WARNING]: invalid scale-ratio or size")
        sys.exit(1)


def load_images(
    dir_path: Path,
    scale: Union[Tuple[float, float], float] = 1,
    colorkey=Color.BLACK,
    trim_space=False,
):
    if not dir_path.exists():
        print(f"[WARNING]: directory {dir_path} not found")
        sys.exit(1)
    sorted_path = sorted(
        [path for path in dir_path.iterdir() if path.suffix == ".png"],
        key=get_numeric_sort_key,
    )
    return [load_image(img, scale, colorkey, trim_space) for img in sorted_path]


def load_key_images(
    dir_path: Path,
    scale: Union[Tuple[float, float], float] = 1,
    key_index: Union[Sequence[int], Tuple[int]] = (0,),
    /,
    trim_space=False,
    colorkey=Color.BLACK,
):
    """
    Loads images from dictionary with key as first character of file.

    Args:
        dir_path (Path): The directory to extract images
        key_index (Optional[Iterable[int]]): character at index to use as key

    Returns:
        Dict[str, pygame.Surface]
    """
    if not dir_path.exists():
        print(f"[WARNING]: directory {dir_path} not found")
        sys.exit(1)
    sorted_path = sorted(
        [path for path in dir_path.iterdir() if path.suffix == ".png"],
        key=get_numeric_sort_key,
    )
    st_index = key_index[0]
    end_index = max(st_index + 1, len(key_index) - 1)
    return {
        img.stem[st_index:end_index]: load_image(img, scale, colorkey, trim_space)
        for img in sorted_path
    }


"""
This is from my own package but i lost this github account
Link:https://github.com/FluffyRudy/pygame_utility/blob/main/src/pygame_utility/sortkeys.py
"""


def get_numeric_sort_key(filepath: Union[Path, str]) -> Tuple[float, str]:
    """
    Extract the numeric part from a file path for sorting. If no numeric part is found, return infinity.

    Args:
        filepath (Union[Path, str]): The file path to extract the numeric part from. Can be a Path object or a string.

    Returns:
        Tuple[float, str]: A tuple containing the numeric part as a float (or infinity if no number is found)
                            and the original file path. The tuple is used for sorting files primarily by
                            the numeric part and secondarily by the file path if needed.

    Example without callback:
        >>> files = ['file10.txt', 'file2.txt', 'file1.txt']
        >>> sorted(files)
        ['file1.txt', 'file10.txt', 'file2.txt']

    Example with `get_numeric_sort_key` callback:
        >>> files = ['file10.txt', 'file2.txt', 'file1.txt']
        >>> sorted(files, key=get_numeric_sort_key)
        ['file1.txt', 'file2.txt', 'file10.txt']
    """
    if isinstance(filepath, Path):
        filepath = str(filepath)

    match = re.search(r"\d+", filepath)
    number = int(match.group()) if match else float("inf")

    return (number, filepath)


def load_pil_img_to_pygame_surf_np(
    path: Path,
    colorkey: Tuple[int, int, int],
    trim_space=False,
):
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)

    mask = (arr[..., :3] == colorkey).all(axis=-1) | (arr[..., 3] == 0)
    arr[mask, 3] = 0

    if trim_space:
        alpha = arr[..., 3]
        ys, xs = np.nonzero(alpha)
        if ys.size > 0 and xs.size > 0:
            arr = arr[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]

    surf = pygame.image.frombuffer(arr.tobytes(), arr.shape[1::-1], "RGBA")
    return surf
