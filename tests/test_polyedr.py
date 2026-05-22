import pytest
from pytest import approx
from math import pi
from shadow.polyedr import Polyedr, Edge, Facet, Segment
from common.r3 import R3

# Вспомогательная функция для создания временного .geom файла
def write_geom_file(path, lines):
    with open(path, 'w') as f:
        f.write('\n'.join(lines))

class TestPolyedr:

    # ------------------------------------------------------------
    # Тесты конструктора
    # ------------------------------------------------------------
    def test_init_cube(self, tmp_path):
        """Проверка загрузки куба: количество вершин, рёбер, граней, координаты"""
        geom = [
            "1.0 0.0 0.0 0.0",   # гомотетия=1, углы 0
            "8 6 24",            # 8 вершин, 6 граней, 24 ребра (удвоено)
            "-0.5 -0.5 0.5",
            "-0.5 0.5 0.5",
            "0.5 0.5 0.5",
            "0.5 -0.5 0.5",
            "-0.5 -0.5 -0.5",
            "-0.5 0.5 -0.5",
            "0.5 0.5 -0.5",
            "0.5 -0.5 -0.5",
            "4 1 2 3 4",
            "4 5 6 2 1",
            "4 3 2 6 7",
            "4 3 7 8 4",
            "4 1 4 8 5",
            "4 8 7 6 5"
        ]
        filepath = tmp_path / "cube.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        # Проверка количества
        assert len(poly.vertexes) == 8
        assert len(poly.vertexes_roated) == 8
        assert len(poly.facets) == 6
        # Рёбер в edges должно быть 24 (по 4 на грань * 6 граней)
        assert len(poly.edges) == 24
        assert len(poly.edges_roated) == 24
        # Проверка, что вершины после поворота (0 градусов) и гомотетии 1 совпадают с исходными
        # Возьмём первую вершину из vertexes и vertexes_roated
        v0 = poly.vertexes[0]          # (-0.5, -0.5, 0.5) *1
        v0r = poly.vertexes_roated[0]  # (-0.5, -0.5, 0.5)
        assert v0.x == approx(-0.5) and v0.y == approx(-0.5) and v0.z == approx(0.5)
        assert v0r.x == approx(-0.5) and v0r.y == approx(-0.5) and v0r.z == approx(0.5)
        # Проверка, что координаты рёбер тоже совпадают (начало первого ребра первой грани)
        # Первая грань: 1 2 3 4 -> рёбра: 4-1, 1-2, 2-3, 3-4
        first_edge = poly.edges[0]  # 4-1
        assert first_edge.beg.x == approx(0.5) and first_edge.beg.y == approx(-0.5)
        assert first_edge.fin.x == approx(-0.5) and first_edge.fin.y == approx(-0.5)

    def test_init_with_rotation_and_scale(self, tmp_path):
        """Проверка, что гомотетия и поворот применяются"""
        # Квадрат из одной грани в плоскости z=0, повёрнутый на 90° вокруг Oz
        geom = [
            "2.0 0.0 0.0 90.0",   # c=2, alpha=0, beta=0, gamma=90
            "4 1 4",
            "1.0 0.0 0.0",
            "1.0 1.0 0.0",
            "0.0 1.0 0.0",
            "0.0 0.0 0.0",
            "4 1 2 3 4"
        ]
        filepath = tmp_path / "square.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        # После поворота на 90° вокруг Oz: точка (1,0,0) -> (0,1,0), затем умножается на 2 -> (0,2,0)
        v0 = poly.vertexes[0]  # исходный индекс 0: (1,0,0)
        assert v0.x == approx(0.0) and v0.y == approx(2.0) and v0.z == approx(0.0)
        # vertexes_roated без гомотетии: (0,1,0)
        v0r = poly.vertexes_roated[0]
        assert v0r.x == approx(0.0) and v0r.y == approx(1.0) and v0r.z == approx(0.0)

    # ------------------------------------------------------------
    # Тесты метода good_edges_length
    # ------------------------------------------------------------
    def test_good_edges_length_no_good_edges(self, tmp_path):
        """Все вершины внутри внутренней окружности — сумма 0"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "4 1 4",
            "0.5 0.0 0.0",   # x^2+y^2=0.25 <1
            "0.0 0.5 0.0",
            "-0.5 0.0 0.0",
            "0.0 -0.5 0.0",
            "4 1 2 3 4"
        ]
        filepath = tmp_path / "no_good.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        assert poly.good_edges_length() == approx(0.0)

    def test_good_edges_length_single_good_edge(self, tmp_path):
        """Одно ребро с двумя хорошими концами — сумма равна длине"""
        # Точки (2,0,0) и (2,1,0): x^2+y^2=4 и 5 — обе в интервале (1,16)
        geom = [
            "1.0 0.0 0.0 0.0",
            "2 1 2",
            "2.0 0.0 0.0",
            "2.0 1.0 0.0",
            "2 1 2"   # грань-отрезок? Нужна хотя бы одна грань из двух вершин (но Facet ожидает минимум 3? В коде конструктор Facet просто сохраняет список вершин, так что можно и 2. Но тень может сломаться, если вызывать draw. Для теста good_edges_length draw не используется, так что можно)
        ]
        # Осторожно: Facet из 2 вершин вызовет проблемы в h_normal (нужно не менее 3). Но good_edges_length не использует facet. Однако в конструкторе Polyedr создаются facets, что может вызвать ошибку при вычислении центра или нормалей, если они не понадобятся. Но facets.append(Facet(vertexes)) просто создаст объект, а при инициализации Facet никакие методы не вызываются. Ошибка возникнет только при вызове методов Facet, но мы этого не делаем. Поэтому можно.
        # Лучше сделать треугольник, содержащий это ребро дважды, но чтобы проверить уникальность. Создадим два треугольника с общим ребром, тогда edges_roated будет содержать это ребро дважды.
        filepath = tmp_path / "single_good.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        length = poly.good_edges_length()
        # Длина ребра = 1.0
        assert length == approx(1.0)

    def test_good_edges_length_with_duplicate_edges(self, tmp_path):
        """Два треугольника с общим ребром — длина учтена один раз"""
        # Вершины:
        # 0: (2,0,0)  (хорошая)
        # 1: (2,1,0)  (хорошая)
        # 2: (3,0,0)  (хорошая? x^2+y^2=9)
        # Общее ребро: 0-1
        geom = [
            "1.0 0.0 0.0 0.0",
            "3 2 6",       # 3 вершины, 2 грани, 6 рёбер (удвоено)
            "2.0 0.0 0.0",
            "2.0 1.0 0.0",
            "3.0 0.0 0.0",
            "3 0 1 2",     # треугольник 0-1-2
            "3 1 0 2"      # второй треугольник 1-0-2 (то же ребро 0-1)
        ]
        filepath = tmp_path / "dup.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        # Длины: 0-1 = 1, 1-2 = sqrt((1)^2+(-1)^2)=√2, 0-2 = 1
        # Хорошие рёбра: оба конца должны быть хорошими. Вершина 2: (3,0,0) -> 9, хорошо. Значит все три ребра хорошие.
        # Но ребро 0-1 появляется дважды, должно быть учтено один раз.
        total = poly.good_edges_length()
        expected = 1.0 + (2.0**0.5) + 1.0
        assert total == approx(expected)

    def test_good_edges_length_boundary(self, tmp_path):
        """Точки на границах кольца не считаются хорошими (строгое неравенство)"""
        # Точка (1,0,0) – x^2+y^2=1 (не good), точка (4,0,0) – x^2+y^2=16 (не good)
        geom = [
            "1.0 0.0 0.0 0.0",
            "3 1 3",
            "1.0 0.0 0.0",
            "4.0 0.0 0.0",
            "2.0 2.0 0.0",  # хорошая (4+4=8)
            "3 0 1 2"
        ]
        filepath = tmp_path / "boundary.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        # Ребро 0-1: оба нехорошие -> не учитывается
        # Ребро 1-2: 1 нехорошая, 2 хорошая -> не учитывается
        # Ребро 2-0: 2 хорошая, 0 нехорошая -> не учитывается
        assert poly.good_edges_length() == 0.0

    def test_good_edges_length_mixed(self, tmp_path):
        """Ребро с одним хорошим концом не учитывается"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "2 1 2",
            "2.0 0.0 0.0",  # хорошая
            "0.5 0.0 0.0",  # нехорошая (0.25)
            "2 0 1"
        ]
        filepath = tmp_path / "mixed.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        assert poly.good_edges_length() == 0.0

    # ------------------------------------------------------------
    # Тест статического метода search
    # ------------------------------------------------------------
    def test_search(self):
        assert Polyedr.search([1,2,3], 2) == 1
        assert Polyedr.search([1,2,3], 4) is None
        assert Polyedr.search([], 1) is None