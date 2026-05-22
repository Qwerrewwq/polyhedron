from pytest import approx
from common.r3 import R3
from shadow.polyedr import Segment, Edge, Facet, Polyedr


def r3approx(self, other):
    return (
        self.x == approx(other.x)
        and self.y == approx(other.y)
        and self.z == approx(other.z)
    )


setattr(R3, "approx", r3approx)


def seg_approx(self, other):
    return (
        self.beg == approx(other.beg)
        and self.fin == approx(other.fin)
        or self.beg == approx(other.fin)
        and self.fin == approx(other.beg)
    )


setattr(Segment, "approx", seg_approx)


class TestEdge:
    def test_r301(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        assert s.beg.approx(s.r3(0.0))

    def test_r302(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        assert s.fin.approx(s.r3(1.0))

    def test_r303(self):
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        assert R3(0.5, 0.0, -1.0).approx(s.r3(0.5))

    def test_intersect_01(self):
        """Ребро полностью внутри полупространства"""
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, -1.0))
        a = R3(0.0, 0.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        assert s.intersect_edge_with_normal(a, n).approx(Segment(0.0, 1.0))

    def test_intersect_02(self):
        """Ребро полностью снаружи полупространства"""
        s = Edge(R3(0.0, 0.0, 1.0), R3(1.0, 0.0, 1.0))
        a = R3(0.0, 0.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        assert s.intersect_edge_with_normal(a, n).is_degenerate()

    def test_intersect_03(self):
        """Ребро лежит в ограничивающей плоскости — пересечение пусто"""
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 0.0))
        a = R3(0.0, 0.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        assert s.intersect_edge_with_normal(a, n).is_degenerate()

    def test_intersect_04(self):
        """Начало внутри, конец снаружи — только первая половина"""
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, 1.0))
        a = R3(1.0, 1.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        assert s.intersect_edge_with_normal(a, n).approx(Segment(0.0, 0.5))

    def test_intersect_05(self):
        """Начало снаружи, конец внутри — только вторая половина"""
        s = Edge(R3(0.0, 0.0, 1.0), R3(1.0, 0.0, -1.0))
        a = R3(1.0, 1.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        assert s.intersect_edge_with_normal(a, n).approx(Segment(0.5, 1.0))

    def test_intersect_06(self):
        """Начало на плоскости, конец внутри — весь отрезок считается внутри?
        (в алгоритме граница не включается, поэтому пересечение от 0 до 1)"""
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, -1.0))
        a = R3(0.0, 0.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        assert s.intersect_edge_with_normal(a, n).approx(Segment(0.0, 1.0))

    def test_intersect_07(self):
        """Конец на плоскости, начало внутри — отрезок от 0 до точки пересечения (0.5)?"""
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 0.0, 0.0))
        a = R3(1.0, 1.0, 0.0)
        n = R3(0.0, 0.0, 1.0)
        assert s.intersect_edge_with_normal(a, n).approx(Segment(0.0, 1.0))

    def test_shadow_01(self):
        """Грань не затеняет ребро, лежащее в её плоскости"""
        s = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 1.0, 0.0))
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(2.0, 0.0, 0.0),
                R3(2.0, 2.0, 0.0),
                R3(0.0, 2.0, 0.0),
            ]
        )
        s.shadow(f)
        assert s.gaps[0].approx(Segment(0.0, 1.0))

    def test_shadow_02(self):
        """Грань не затеняет ребро, расположенное выше грани"""
        s = Edge(R3(0.0, 0.0, 1.0), R3(1.0, 1.0, 1.0))
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(2.0, 0.0, 0.0),
                R3(2.0, 2.0, 0.0),
                R3(0.0, 2.0, 0.0),
            ]
        )
        s.shadow(f)
        assert s.gaps[0].approx(Segment(0.0, 1.0))

    def test_shadow_03(self):
        """Грань полностью затеняет ребро под ней"""
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 1.0, -1.0))
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(2.0, 0.0, 0.0),
                R3(2.0, 2.0, 0.0),
                R3(0.0, 2.0, 0.0),
            ]
        )
        s.shadow(f)
        assert len(s.gaps) == 0

    def test_shadow_04(self):
        """Длинное ребро под гранью даёт ровно два просвета"""
        s = Edge(R3(-5.0, -5.0, -1.0), R3(3.0, 3.0, -1.0))
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(2.0, 0.0, 0.0),
                R3(2.0, 2.0, 0.0),
                R3(0.0, 2.0, 0.0),
            ]
        )
        s.shadow(f)
        assert len(s.gaps) == 2

    def test_shadow_vertical_facet(self):
        """Вертикальная грань не затеняет ничего"""
        s = Edge(R3(0.0, 0.0, -1.0), R3(1.0, 1.0, -1.0))
        # Вертикальная грань в плоскости x=0
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(0.0, 2.0, 0.0),
                R3(0.0, 2.0, 2.0),
                R3(0.0, 0.0, 2.0),
            ]
        )
        s.shadow(f)
        assert len(s.gaps) == 1
        assert s.gaps[0].approx(Segment(0.0, 1.0))

    def test_shadow_vertical_outside(self):
        """Ребро вне призмы вертикальных полупространств — тень пуста"""
        s = Edge(R3(3.0, 3.0, -1.0), R3(4.0, 4.0, -1.0))
        f = Facet(
            [
                R3(0.0, 0.0, 0.0),
                R3(2.0, 0.0, 0.0),
                R3(2.0, 2.0, 0.0),
                R3(0.0, 2.0, 0.0),
            ]
        )
        s.shadow(f)
        assert len(s.gaps) == 1
        assert s.gaps[0].approx(Segment(0.0, 1.0))
