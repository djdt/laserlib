import numpy as np

from pew.lib.calc import normalise, shuffle_blocks

from typing import Tuple


def li_icq(x: np.ndarray, y: np.ndarray) -> float:
    ux, uy = np.mean(x), np.mean(y)
    return np.sum((x - ux) * (y - uy) >= 0.0) / x.size - 0.5


def pearsonr(x: np.ndarray, y: np.ndarray) -> float:
    """Returns Pearson's colocalisation coefficient for the two arrays.
    This value for colocalisation between -1 and 1 (colocalised).
"""
    return (np.mean(x * y) - (np.mean(x) * np.mean(y))) / (np.std(x) * np.std(y))


def pearsonr_probablity(
    x: np.ndarray,
    y: np.ndarray,
    block: int = 3,
    mask: np.ndarray = None,
    mask_all: bool = True,
    n: int = 500,
) -> Tuple[float, float]:
    """Returns Pearson's colocalisation coefficient and the relevant probabilty.
    If a mask is passsed then masked shuffle_blocks is used.
"""
    if mask is None:
        mask = np.ones(x.shape, dtype=bool)

    rs = np.empty(n, dtype=float)
    for i in range(n):
        shuffled = shuffle_blocks(y, (block, block), mask, mask_all=mask_all)
        rs[i] = pearsonr(x[mask], shuffled[mask])

    r = pearsonr(x[mask], y[mask])
    return r, (rs < r).sum() / n


def manders(
    x: np.ndarray, y: np.ndarray, tx: float = None, ty: float = None
) -> Tuple[float, float]:
    """Returns Manders' correlation coefficients m1, m2.
    tx and ty are the thresholds for x and y respectively.
    If ty is None then tx is used.
"""
    if tx is None:
        tx = np.amin(x)
    if ty is None:
        ty = np.amin(y)

    return np.sum(x, where=y > ty) / x.sum(), np.sum(y, where=x > tx) / y.sum()


def costes_threshold(
    x: np.ndarray, y: np.ndarray, target_r: float = 0.0
) -> Tuple[float, float, float]:
    """Calculates the thresholds Tx and Ty for the given arrays.
    Arrays should be normalised before calling this function.

    Returns:
        T -> threshold for x
        a -> slope
        b -> interept
"""
    b, a = np.polynomial.polynomial.polyfit(x.ravel(), y.ravel(), 1)
    threshold = x.max()
    threshold_min = x.min()
    increment = (threshold - threshold_min) / 256.0

    idx = np.logical_or(x <= threshold, y <= (a * threshold + b))
    r = pearsonr(x[idx], y[idx])

    while r > target_r and threshold > threshold_min:
        threshold -= increment
        idx = np.logical_or(x <= threshold, y <= (a * threshold + b))
        if np.unique(x[idx]).size == 1 or np.unique(y[idx]).size == 1:
            threshold = threshold_min
            break
        r = pearsonr(x[idx], y[idx])  # pragma: no cover

    return threshold, a, b


def costes(
    x: np.ndarray, y: np.ndarray, n_scrambles: int = 200
) -> Tuple[float, float, float, float]:  # pragma: no cover, covered in other funcs
    x, y = normalise(x), normalise(y)
    t, a, b = costes_threshold(x, y)
    tx, ty = t, t * a + b
    pearson_r, r_prob = pearsonr_probablity(
        x, y, mask=np.logical_and(x > tx, y > ty), n=n_scrambles
    )
    m1, m2 = manders(x, y, tx, ty)

    return pearson_r, r_prob, m1, m2
