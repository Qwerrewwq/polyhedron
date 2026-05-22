from pytest import approx
from common.tk_drawer import TkDrawer, x, y, SIZE, SCALE
from common.r3 import R3


class TestTkDrawer:

    # Проверка создания экземпляра и заголовка окна
    def test_init(self):
        tk = TkDrawer()
        assert tk.root.title() == "Изображение проекции полиэдра"
        assert tk.canvas is not None
        tk.root.destroy()

    # Проверка преобразования x
    def test_x(self):
        p = R3(0.0, 0.0, 0.0)
        assert x(p) == SIZE / 2
        p = R3(1.0, 0.0, 0.0)
        assert x(p) == SIZE / 2 + SCALE * 1.0

    # Проверка преобразования y
    def test_y(self):
        p = R3(0.0, 0.0, 0.0)
        assert y(p) == SIZE / 2
        p = R3(0.0, 1.0, 0.0)
        assert y(p) == SIZE / 2 - SCALE * 1.0

    # Метод clean не должен вызывать ошибок
    def test_clean(self):
        tk = TkDrawer()
        try:
            tk.clean()
        except Exception as e:
            assert False, f"clean() raised exception: {e}"
        finally:
            tk.root.destroy()

    # Метод draw_line не должен вызывать ошибок
    def test_draw_line(self):
        tk = TkDrawer()
        p = R3(0.0, 0.0, 0.0)
        q = R3(1.0, 1.0, 0.0)
        try:
            tk.draw_line(p, q)
        except Exception as e:
            assert False, f"draw_line() raised exception: {e}"
        finally:
            tk.root.destroy()