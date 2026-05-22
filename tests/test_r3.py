from pytest import approx
from common.r3 import R3


def r3approx(self, other):
    return (
        self.x == approx(other.x)
        and self.y == approx(other.y)
        and self.z == approx(other.z)
    )


# добавляем метод approx в класс R3 для удобства сравнения в тестах
setattr(R3, "approx", r3approx)


class TestR3:
    # Конструктор и атрибуты
    def test_init(self):
        p = R3(1.0, 2.0, 3.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    # Сложение векторов
    def test_add(self):
        a = R3(1.0, 2.0, 3.0)
        b = R3(4.0, 5.0, 6.0)
        c = a + b
        assert c.x == 5.0
        assert c.y == 7.0
        assert c.z == 9.0

    # Вычитание векторов
    def test_sub(self):
        a = R3(4.0, 5.0, 6.0)
        b = R3(1.0, 2.0, 3.0)
        c = a - b
        assert c.x == 3.0
        assert c.y == 3.0
        assert c.z == 3.0

    # Умножение на число
    def test_mul(self):
        a = R3(1.0, 2.0, 3.0)
        b = a * 2.0
        assert b.x == 2.0
        assert b.y == 4.0
        assert b.z == 6.0

    # Умножение на отрицательное число
    def test_mul_neg(self):
        a = R3(1.0, -2.0, 3.0)
        b = a * (-1.0)
        assert b.x == -1.0
        assert b.y == 2.0
        assert b.z == -3.0

    # Поворот вокруг Oz на 90 градусов (π/2)
    def test_rz_90(self):
        a = R3(1.0, 0.0, 5.0)
        b = a.rz(3.1415926535 / 2)
        assert b.x == approx(0.0, abs=1e-6)
        assert b.y == approx(1.0, abs=1e-6)
        assert b.z == 5.0

    # Поворот вокруг Oz на 0 градусов не меняет вектор
    def test_rz_zero(self):
        a = R3(1.0, 2.0, 3.0)
        b = a.rz(0.0)
        assert b.approx(a)  # используем approx метод

    # Поворот вокруг Oy на 90 градусов (π/2)
    def test_ry_90(self):
        a = R3(1.0, 0.0, 0.0)
        b = a.ry(3.1415926535 / 2)
        # после поворота вокруг Oy на 90°, точка (1,0,0) переходит в (0,0,-1)
        assert b.x == approx(0.0, abs=1e-6)
        assert b.y == 0.0
        assert b.z == approx(-1.0, abs=1e-6)

    # Поворот вокруг Oy на 0 градусов не меняет вектор
    def test_ry_zero(self):
        a = R3(1.0, 2.0, 3.0)
        b = a.ry(0.0)
        assert b.approx(a)

    # Скалярное произведение ортогональных векторов равно 0
    def test_dot_orthogonal(self):
        a = R3(1.0, 0.0, 0.0)
        b = R3(0.0, 1.0, 0.0)
        assert a.dot(b) == 0.0

    # Векторное произведение
    def test_cross(self):
        a = R3(1.0, 0.0, 0.0)
        b = R3(0.0, 1.0, 0.0)
        c = a.cross(b)
        assert c.x == 0.0
        assert c.y == 0.0
        assert c.z == 1.0

    # Векторное произведение антикоммутативно
    def test_cross_anticommutative(self):
        a = R3(1.0, 2.0, 3.0)
        b = R3(4.0, 5.0, 6.0)
        c1 = a.cross(b)
        c2 = b.cross(a)
        assert c1.x == -c2.x
        assert c1.y == -c2.y
        assert c1.z == -c2.z

    def test_is_good_inside(self):
        p = R3(2.0, 2.0, 100.0)  # x²+y²=8, z не важно
        assert p.is_good() is True

    def test_is_good_inner_boundary(self):
        p = R3(1.0, 0.0, 0.0)  # 1
        assert p.is_good() is False

    def test_is_good_outer_boundary(self):
        p = R3(4.0, 0.0, 0.0)  # 16
        assert p.is_good() is False

    def test_is_good_outside_inner(self):
        p = R3(0.5, 0.5, 0.0)  # 0.5
        assert p.is_good() is False

    def test_is_good_outside_outer(self):
        p = R3(4.0, 1.0, 0.0)  # 17
        assert p.is_good() is False

    def test_distance_on_xoy(self):
        a = R3(0.0, 0.0, 10.0)
        b = R3(3.0, 4.0, -10.0)
        d = a.distance_on_xoy(b)
        assert d == 5.0

    def test_distance_on_xoy_zero(self):
        a = R3(1.0, 2.0, 3.0)
        b = R3(1.0, 2.0, 5.0)
        assert a.distance_on_xoy(b) == 0.0
