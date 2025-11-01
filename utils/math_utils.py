from typing import Union


def sign(n: Union[float, int]):
    return (n > 0) - (n < 0)


# introduce something that i no longer need, anyway this is great for learning piecewise function
def is_closer(
    a: Union[float, int], b: Union[float, int], threshold: Union[float, int] = 0
) -> bool:
    """
    Check if a is closer to b within a given threshold.

    Args:
        a (Union[float, int]): Target to test.
        b (Union[float, int]): Source value.
        threshold (Union[float, int]): Acceptable closeness range.

    Returns:
        bool: True if a is within the threshold of b.
    """
    return abs(a - b) <= abs(threshold)


print(is_closer(51, 51, -2))
