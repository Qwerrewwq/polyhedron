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


# Вспомогательный класс для тестирования is_good_segment
class GoodPoint:
    def __init__(self, good):
        self._good = good

    def is_good(self):
        return self._good


class TestSegment:
    # ------ is_degenerate ------
    def test_degenerate01(self):
        assert not Segment(0.0, 1.0).is_degenerate()

    def test_degenerate02(self):
        assert Segment(0.0, 0.0).is_degenerate()

    def test_degenerate03(self):
        assert Segment(0.0, -1.0).is_degenerate()

    # ------ intersect ------
    # Пересечение с самим собой не меняет отрезок
    def test_intersect01(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 1.0)
        a.intersect(b)
        assert a.approx(Segment(0.0, 1.0))

    # Отрезок полностью внутри другого: other.beg <= self.beg и other.fin >= self.fin
    def test_intersect_self_inside_other(self):
        a = Segment(0.2, 0.8)
        b = Segment(0.0, 1.0)
        a.intersect(b)
        assert a.approx(Segment(0.2, 0.8))

    # Пересечение: other сдвигает начало (other.beg > self.beg)
    def test_intersect_shift_beg(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.3, 1.2)
        a.intersect(b)
        assert a.approx(Segment(0.3, 1.0))

    # Пересечение: other сдвигает конец (other.fin < self.fin)
    def test_intersect_shift_fin(self):
        a = Segment(0.0, 1.0)
        b = Segment(-0.2, 0.7)
        a.intersect(b)
        assert a.approx(Segment(0.0, 0.7))

    # Пересечение: other сдвигает оба конца
    def test_intersect_shift_both(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.2, 0.9)
        a.intersect(b)
        assert a.approx(Segment(0.2, 0.9))

    # Пересечение не изменяет отрезок, если other шире с обеих сторон
    def test_intersect_other_wider(self):
        a = Segment(0.3, 0.7)
        b = Segment(0.0, 1.0)
        a.intersect(b)
        assert a.approx(Segment(0.3, 0.7))

    # Пересечение, при котором other целиком левее (не перекрываются)
    # После intersect начало станет > конец? Проверим вырожденность.
    def test_intersect_no_overlap_left(self):
        a = Segment(0.5, 1.0)
        b = Segment(0.0, 0.3)
        a.intersect(
            b
        )  # other.beg=0.0 > 0.5? нет, other.fin=0.3 < 1.0? да => self.fin=0.3
        # получается отрезок [0.5, 0.3] – вырожден
        assert a.is_degenerate()

    # Пересечение, при котором other целиком правее
    def test_intersect_no_overlap_right(self):
        a = Segment(0.0, 0.5)
        b = Segment(0.6, 1.0)
        a.intersect(
            b
        )  # other.beg=0.6 > 0.0? да => self.beg=0.6, other.fin=1.0 < 0.5? нет
        # получается [0.6, 0.5] – вырожден
        assert a.is_degenerate()

    # Коммутативность intersect (проверка, что результат не зависит от порядка,
    # если применять к копиям; здесь просто демонстрация на разных примерах)
    def test_intersect_commutative(self):
        # пример 1: частичное перекрытие
        a1 = Segment(0.0, 1.0)
        b1 = Segment(0.3, 1.2)
        a1.intersect(b1)
        a2 = Segment(0.3, 1.2)
        b2 = Segment(0.0, 1.0)
        a2.intersect(b2)
        assert a1.approx(a2)

        # пример 2: вложенные отрезки
        a1 = Segment(0.2, 0.8)
        b1 = Segment(0.0, 1.0)
        a1.intersect(b1)
        a2 = Segment(0.0, 1.0)
        b2 = Segment(0.2, 0.8)
        a2.intersect(b2)
        assert a1.approx(a2)

    # ------ subtraction ------
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

    # Дополнительные тесты для subtraction: крайние случаи
    # Вычитание: other полностью справа
    def test_subtraction_other_right(self):
        a = Segment(2.0, 5.0)
        b = Segment(6.0, 7.0)
        left, right = a.subtraction(b)
        # self.fin < other.beg? 5 < 6 истинно => left конец = self.fin =5, left=[2,5] невырожден
        # self.beg > other.fin? 2 > 7 ложно => right начало = other.fin =7, right=[7,5] вырожден
        assert left.approx(Segment(2.0, 5.0))
        assert right.is_degenerate()

    # Вычитание: other перекрывает левый край
    def test_subtraction_overlap_left(self):
        a = Segment(2.0, 5.0)
        b = Segment(0.0, 3.0)
        left, right = a.subtraction(b)
        # self.fin < other.beg? 5<0 ложно => left конец = other.beg = 0 => [2,0] вырожден
        # self.beg > other.fin? 2>3 ложно => right начало = other.fin = 3 => [3,5] невырожден
        assert left.is_degenerate()
        assert right.approx(Segment(3.0, 5.0))

    # Вычитание: other перекрывает правый край
    def test_subtraction_overlap_right(self):
        a = Segment(2.0, 5.0)
        b = Segment(4.0, 6.0)
        left, right = a.subtraction(b)
        # self.fin < other.beg? 5<4 ложно => left конец = other.beg = 4 => [2,4] невырожден
        # self.beg > other.fin? 2>6 ложно => right начало = other.fin = 6 => [6,5] вырожден
        assert left.approx(Segment(2.0, 4.0))
        assert right.is_degenerate()

    # Вычитание: self полностью внутри other
    def test_subtraction_self_inside_other(self):
        a = Segment(3.0, 4.0)
        b = Segment(1.0, 5.0)
        left, right = a.subtraction(b)
        # self.fin < other.beg? 4<1 ложно => left конец = other.beg=1 -> [3,1] вырожден
        # self.beg > other.fin? 3>5 ложно => right начало = other.fin=5 -> [5,4] вырожден
        assert left.is_degenerate()
        assert right.is_degenerate()

    # ------ is_good_segment ------
    def test_is_good_segment_both_good(self):
        p1 = GoodPoint(True)
        p2 = GoodPoint(True)
        s = Segment(p1, p2)
        assert s.is_good_segment() == True

    def test_is_good_segment_beg_bad(self):
        p1 = GoodPoint(False)
        p2 = GoodPoint(True)
        s = Segment(p1, p2)
        assert s.is_good_segment() == False

    def test_is_good_segment_fin_bad(self):
        p1 = GoodPoint(True)
        p2 = GoodPoint(False)
        s = Segment(p1, p2)
        assert s.is_good_segment() == False

    def test_is_good_segment_both_bad(self):
        p1 = GoodPoint(False)
        p2 = GoodPoint(False)
        s = Segment(p1, p2)
        assert s.is_good_segment() == False

