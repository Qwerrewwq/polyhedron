import pytest
from pytest import approx
from math import pi
from shadow.polyedr import Polyedr, Edge, Facet, Segment
from common.r3 import R3


# Вспомогательная функция для создания временного .geom файла
def write_geom_file(path, lines):
    with open(path, "w") as f:
        f.write("\n".join(lines))


class TestPolyedr:
    def test_init_cube(self, tmp_path):
        """Проверка загрузки куба: количество вершин, рёбер, граней, координаты"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "8 6 24",
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
            "4 8 7 6 5",
        ]
        filepath = tmp_path / "cube.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        assert len(poly.vertexes) == 8
        assert len(poly.vertexes_roated) == 8
        assert len(poly.facets) == 6
        assert len(poly.edges) == 24
        assert len(poly.edges_roated) == 24
        v0 = poly.vertexes[0]
        v0r = poly.vertexes_roated[0]
        assert v0.x == approx(-0.5) and v0.y == approx(-0.5) and v0.z == approx(0.5)
        assert v0r.x == approx(-0.5) and v0r.y == approx(-0.5) and v0r.z == approx(0.5)
        first_edge = poly.edges[0]  # 4-1
        assert first_edge.beg.x == approx(0.5) and first_edge.beg.y == approx(-0.5)
        assert first_edge.fin.x == approx(-0.5) and first_edge.fin.y == approx(-0.5)

    def test_init_with_rotation_and_scale(self, tmp_path):
        """Проверка, что гомотетия и поворот применяются"""
        geom = [
            "2.0 0.0 0.0 90.0",
            "4 1 4",
            "1.0 0.0 0.0",
            "1.0 1.0 0.0",
            "0.0 1.0 0.0",
            "0.0 0.0 0.0",
            "4 1 2 3 4",
        ]
        filepath = tmp_path / "square.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        v0 = poly.vertexes[0]
        assert v0.x == approx(0.0) and v0.y == approx(2.0) and v0.z == approx(0.0)
        v0r = poly.vertexes_roated[0]
        assert v0r.x == approx(0.0) and v0r.y == approx(1.0) and v0r.z == approx(0.0)

    def test_good_edges_length_no_good_edges(self, tmp_path):
        """Все вершины внутри внутренней окружности — сумма 0"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "4 1 4",
            "0.5 0.0 0.0",
            "0.0 0.5 0.0",
            "-0.5 0.0 0.0",
            "0.0 -0.5 0.0",
            "4 1 2 3 4",
        ]
        filepath = tmp_path / "no_good.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        assert poly.good_edges_length() == approx(0.0)

    def test_good_edges_length_single_good_edge(self, tmp_path):
        """Одно ребро с двумя хорошими концами — сумма равна длине"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "2 1 2",
            "2.0 0.0 0.0",
            "2.0 1.0 0.0",
            "2 1 2",
        ]
        filepath = tmp_path / "single_good.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        length = poly.good_edges_length()
        assert length == approx(1.0)

    def test_good_edges_length_with_duplicate_edges(self, tmp_path):
        """Два треугольника с общим ребром — длина учтена один раз"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "3 2 6",
            "2.0 0.0 0.0",
            "2.0 1.0 0.0",
            "3.0 0.0 0.0",
            "3 0 1 2",
            "3 1 0 2",
        ]
        filepath = tmp_path / "dup.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        total = poly.good_edges_length()
        expected = 1.0 + (2.0**0.5) + 1.0
        assert total == approx(expected)

    def test_good_edges_length_boundary(self, tmp_path):
        """Точки на границах кольца не считаются хорошими (строгое неравенство)"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "3 1 3",
            "1.0 0.0 0.0",
            "4.0 0.0 0.0",
            "2.0 2.0 0.0",
            "3 0 1 2",
        ]
        filepath = tmp_path / "boundary.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        assert poly.good_edges_length() == 0.0

    def test_good_edges_length_mixed(self, tmp_path):
        """Ребро с одним хорошим концом не учитывается"""
        geom = [
            "1.0 0.0 0.0 0.0",
            "2 1 2",
            "2.0 0.0 0.0",
            "0.5 0.0 0.0",
            "2 0 1",
        ]
        filepath = tmp_path / "mixed.geom"
        write_geom_file(filepath, geom)
        poly = Polyedr(str(filepath))
        assert poly.good_edges_length() == 0.0

    def test_search(self):
        assert Polyedr.search([1, 2, 3], 2) == 1
        assert Polyedr.search([1, 2, 3], 4) is None
        assert Polyedr.search([], 1) is None
