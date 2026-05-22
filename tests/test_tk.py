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

    def test_draw_circle(self):
        tk = TkDrawer()
        try:
            # Сохраняем количество элементов до вызова
            initial_items = tk.canvas.find_all()
            # Рисуем окружность радиуса 2.0 (в условных единицах)
            tk.draw_circle(2.0)
            new_items = tk.canvas.find_all()
            # Должен добавиться ровно один объект
            assert len(new_items) == len(initial_items) + 1

            # Проверяем координаты
            coords = tk.canvas.coords(new_items[-1])
            cx, cy = SIZE / 2, SIZE / 2
            r = SCALE * 2.0
            expected = (cx - r, cy - r, cx + r, cy + r)
            assert coords == approx(expected)

            # Проверяем, что это овал
            assert tk.canvas.type(new_items[-1]) == "oval"

            # Проверяем цвет контура
            outline = tk.canvas.itemcget(new_items[-1], "outline")
            assert outline == "pink"
        finally:
            tk.root.destroy()
