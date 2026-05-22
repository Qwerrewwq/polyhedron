from pytest import approx
from functools import reduce
from operator import add
from shadow.polyedr import Segment


def flatten(list):
    return [s for s in reduce(add, list, []) if not s.is_degenerate()]


def seg_approx(self, other):
    return (
        self.beg == approx(other.beg)
        and self.fin == approx(other.fin)
        or self.beg == approx(other.fin)
        and self.fin == approx(other.beg)
    )


setattr(Segment, "approx", seg_approx)


class GoodPoint:
    def __init__(self, good):
        self._good = good

    def is_good(self):
        return self._good


class TestSegment:
    def test_degenerate01(self):
        assert not Segment(0.0, 1.0).is_degenerate()

    def test_degenerate02(self):
        assert Segment(0.0, 0.0).is_degenerate()

    def test_degenerate03(self):
        assert Segment(0.0, -1.0).is_degenerate()

    def test_intersect01(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 1.0)
        a.intersect(b)
        assert a.approx(Segment(0.0, 1.0))

    def test_intersect_self_inside_other(self):
        a = Segment(0.2, 0.8)
        b = Segment(0.0, 1.0)
        a.intersect(b)
        assert a.approx(Segment(0.2, 0.8))

    def test_intersect_shift_beg(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.3, 1.2)
        a.intersect(b)
        assert a.approx(Segment(0.3, 1.0))

    def test_intersect_shift_fin(self):
        a = Segment(0.0, 1.0)
        b = Segment(-0.2, 0.7)
        a.intersect(b)
        assert a.approx(Segment(0.0, 0.7))

    def test_intersect_shift_both(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.2, 0.9)
        a.intersect(b)
        assert a.approx(Segment(0.2, 0.9))

    def test_intersect_other_wider(self):
        a = Segment(0.3, 0.7)
        b = Segment(0.0, 1.0)
        a.intersect(b)
        assert a.approx(Segment(0.3, 0.7))

    def test_intersect_no_overlap_left(self):
        a = Segment(0.5, 1.0)
        b = Segment(0.0, 0.3)
        a.intersect(b)
        assert a.is_degenerate()

    def test_intersect_no_overlap_right(self):
        a = Segment(0.0, 0.5)
        b = Segment(0.6, 1.0)
        a.intersect(b)
        assert a.is_degenerate()

    def test_intersect_commutative(self):
        a1 = Segment(0.0, 1.0)
        b1 = Segment(0.3, 1.2)
        a1.intersect(b1)
        a2 = Segment(0.3, 1.2)
        b2 = Segment(0.0, 1.0)
        a2.intersect(b2)
        assert a1.approx(a2)

        a1 = Segment(0.2, 0.8)
        b1 = Segment(0.0, 1.0)
        a1.intersect(b1)
        a2 = Segment(0.0, 1.0)
        b2 = Segment(0.2, 0.8)
        a2.intersect(b2)
        assert a1.approx(a2)

    def test_subtraction01(self):
        a, b = Segment(0.0, 1.0), Segment(0.0, 1.0)
        assert all(s.is_degenerate() for s in a.subtraction(b))

    def test_subtraction02(self):
        a, b = Segment(0.0, 2.0), Segment(0.0, 1.0)
        assert any(s.is_degenerate() for s in a.subtraction(b))
        assert any(not s.is_degenerate() for s in a.subtraction(b))

    def test_subtraction03(self):
        a, b = Segment(-1.0, 2.0), Segment(0.0, 1.0)
        assert all(not s.is_degenerate() for s in a.subtraction(b))

    def test_subtraction04(self):
        a, b = Segment(-1.0, 2.0), Segment(0.0, 1.0)
        assert all(s.is_degenerate() for s in b.subtraction(a))

    def test_subtraction05(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 0.5)
        c = Segment(0.5, 1.0)
        assert all(
            t.is_degenerate()
            for t in flatten(s.subtraction(c) for s in a.subtraction(b))
        )

    def test_subtraction06(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 0.5)
        c = Segment(0.6, 1.0)
        # Считаем количество невырожденных
        nondeg = [
            t
            for t in flatten(s.subtraction(c) for s in a.subtraction(b))
            if not t.is_degenerate()
        ]
        assert len(nondeg) == 1

    def test_subtraction07(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.1, 0.2)
        c = Segment(0.4, 0.8)
        nondeg = [
            t
            for t in flatten(s.subtraction(c) for s in a.subtraction(b))
            if not t.is_degenerate()
        ]
        assert len(nondeg) == 3

    def test_subtraction_other_right(self):
        a = Segment(2.0, 5.0)
        b = Segment(6.0, 7.0)
        left, right = a.subtraction(b)
        assert left.approx(Segment(2.0, 5.0))
        assert right.is_degenerate()

    def test_subtraction_overlap_left(self):
        a = Segment(2.0, 5.0)
        b = Segment(0.0, 3.0)
        left, right = a.subtraction(b)
        assert left.is_degenerate()
        assert right.approx(Segment(3.0, 5.0))

    def test_subtraction_overlap_right(self):
        a = Segment(2.0, 5.0)
        b = Segment(4.0, 6.0)
        left, right = a.subtraction(b)
        assert left.approx(Segment(2.0, 4.0))
        assert right.is_degenerate()

    def test_subtraction_self_inside_other(self):
        a = Segment(3.0, 4.0)
        b = Segment(1.0, 5.0)
        left, right = a.subtraction(b)
        assert left.is_degenerate()
        assert right.is_degenerate()

    def test_is_good_segment_both_good(self):
        p1 = GoodPoint(True)
        p2 = GoodPoint(True)
        s = Segment(p1, p2)
        assert s.is_good_segment() is True

    def test_is_good_segment_beg_bad(self):
        p1 = GoodPoint(False)
        p2 = GoodPoint(True)
        s = Segment(p1, p2)
        assert s.is_good_segment() is not True

    def test_is_good_segment_fin_bad(self):
        p1 = GoodPoint(True)
        p2 = GoodPoint(False)
        s = Segment(p1, p2)
        assert s.is_good_segment() is not True

    def test_is_good_segment_both_bad(self):
        p1 = GoodPoint(False)
        p2 = GoodPoint(False)
        s = Segment(p1, p2)
        assert s.is_good_segment() is not True
