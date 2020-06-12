import numpy as np

from pew.lib import colocal


a = np.tile([[0.0, 1.0], [0.0, 1.0]], (5, 5))
b = np.tile([[0.0, 1.0], [1.0, 0.0]], (5, 5))
c = np.tile([[1.0, 0.0], [1.0, 0.0]], (5, 5))
d = np.tile([[1., 2.], [3., 4.]], (5, 5))
e = np.tile([[1., 2.], [4., 3.]], (5, 5))


def test_li_icq():
    assert colocal.li_icq(a, a) == 0.5
    assert colocal.li_icq(a, b) == 0.0
    assert colocal.li_icq(a, c) == -0.5


def test_pearson_r():
    assert colocal.pearsonr(a, a) == 1.0
    assert colocal.pearsonr(a, b) == 0.0
    assert colocal.pearsonr(a, c) == -1.0


def test_pearson_r_probability():
    r, p = colocal.pearsonr_probablity(a, b, block=4, n=100)
    assert r == 0
    assert p > 0.95


def test_manders():
    assert colocal.manders(a, a, 0) == (1.0, 1.0)
    assert colocal.manders(a, b, 0, 0) == (0.5, 0.5)
    assert colocal.manders(a, c, 0, 0) == (0.0, 0.0)


def test_costes_threshold():
    assert np.allclose(colocal.costes_threshold(a, a), (0.0, 1.0, 0.0))
