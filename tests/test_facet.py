from pytest import approx
from math import sqrt
from common.r3 import R3
from shadow.polyedr import Facet


def is_collinear(self, other):
    t = (
        self.dot(other)
        / sqrt(self.x**2 + self.y**2 + self.z**2)
        / sqrt(other.x**2 + other.y**2 + other.z**2)
    )
    return t == approx(1.0)


setattr(R3, "is_collinear", is_collinear)


def r3approx(self, other):
    return (
        self.x == approx(other.x)
        and self.y == approx(other.y)
        and self.z == approx(other.z)
    )


setattr(R3, "approx", r3approx)


class TestFacet:
    def test_vertical01(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        assert not f.is_vertical()

    def test_vertical02(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(0.0, 0.0, 1.0), R3(1.0, 0.0, 0.0)])
        assert f.is_vertical()

    def test_h_normal01(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        assert f.h_normal().is_collinear(R3(0.0, 0.0, 1.0))

    def test_h_normal02(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(0.0, 3.0, 0.0), R3(3.0, 0.0, 0.0)])
        assert f.h_normal().is_collinear(R3(0.0, 0.0, 1.0))

    def test_h_normal03(self):
        f = Facet([R3(1.0, 0.0, 0.0), R3(0.0, 1.0, 0.0), R3(0.0, 0.0, 1.0)])
        assert f.h_normal().is_collinear(R3(1.0, 1.0, 1.0))

    def test_v_normal01(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        normals = [R3(-1.0, 0.0, 0.0), R3(0.0, -1.0, 0.0), R3(1.0, 1.0, 0.0)]
        for t in zip(f.v_normals(), normals):
            assert t[0].is_collinear(t[1])

    def test_v_normal02(self):
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(2.0, 0.0, 0.0),
                R3(2.0, 2.0, 0.0),
                R3(0.0, 2.0, 0.0),
            ]
        )
        normals = [
            R3(-1.0, 0.0, 0.0),
            R3(0.0, -1.0, 0.0),
            R3(1.0, 0.0, 0.0),
            R3(0.0, 1.0, 0.0),
        ]
        for t in zip(f.v_normals(), normals):
            assert t[0].is_collinear(t[1])

    def test_v_normal03(self):
        f = Facet([R3(1.0, 0.0, 0.0), R3(0.0, 1.0, 0.0), R3(0.0, 0.0, 1.0)])
        normals = [R3(0.0, -1.0, 0.0), R3(1.0, 1.0, 0.0), R3(-1.0, 0.0, 0.0)]
        for t in zip(f.v_normals(), normals):
            assert t[0].is_collinear(t[1])

    def test_center01(self):
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(2.0, 0.0, 0.0),
                R3(2.0, 2.0, 0.0),
                R3(0.0, 2.0, 0.0),
            ]
        )
        assert f.center().approx((R3(1.0, 1.0, 0.0)))

    def test_center02(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        assert f.center().approx((R3(1.0, 1.0, 0.0)))
