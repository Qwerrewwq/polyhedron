from math import pi
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Edge:
    """Ребро полиэдра"""

    # Параметры конструктора: начало и конец ребра (точки в R3)

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin


class Facet:
    """Грань полиэдра"""

    # Параметры конструктора: список вершин

    def __init__(self, vertexes):
        self.vertexes = vertexes


class Polyedr:
    """Полиэдр"""

    # Параметры конструктора: файл, задающий полиэдр

    def __init__(self, file):

        # списки вершин, рёбер и граней полиэдра
        (
            self.vertexes,
            self.vertexes_roated,
            self.edges,
            self.edges_roated,
            self.facets,
        ) = (
            [],
            [],
            [],
            [],
            [],
        )

        # список строк файла
        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    # обрабатываем первую строку; buf - вспомогательный массив
                    buf = line.split()
                    # коэффициент гомотетии
                    self.c = float(buf.pop(0))
                    # углы Эйлера, определяющие вращение
                    alpha, beta, gamma = (float(x) * pi / 180.0 for x in buf)
                elif i == 1:
                    # во второй строке число вершин, граней и рёбер полиэдра
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    # задание всех вершин полиэдра
                    x, y, z = (float(x) for x in line.split())
                    self.vertexes.append(
                        R3(x, y, z).rz(alpha).ry(beta).rz(gamma) * self.c
                    )
                    self.vertexes_roated.append(
                        R3(x, y, z).rz(alpha).ry(beta).rz(gamma)
                    )
                else:
                    # вспомогательный массив
                    buf = line.split()
                    # количество вершин очередной грани
                    size = int(buf.pop(0))
                    # массив вершин этой грани
                    vertexes = [self.vertexes[int(n) - 1] for n in buf]
                    vertexes_roated = list(
                        self.vertexes_roated[int(n) - 1] for n in buf
                    )
                    # задание рёбер грани
                    for n in range(size):
                        self.edges.append(Edge(vertexes[n - 1], vertexes[n]))
                        self.edges_roated.append(
                            Edge(vertexes_roated[n - 1], vertexes_roated[n])
                        )
                    # задание самой грани
                    self.facets.append(Facet(vertexes))

    @staticmethod
    def search(lst, val):
        for k in range(len(lst)):
            if lst[k] == val:
                return k
        return None

    def good_edges_length(self):
        seen = []
        for j in self.edges_roated:
            a = (j.beg.x, j.beg.y, j.beg.z)
            b = (j.fin.x, j.fin.y, j.fin.z)
            if j.beg.is_good() and j.fin.is_good():
                key = sorted([a, b])
                if self.search(seen, key) is None:
                    seen.append(key)
        distance = 0
        for k in seen:
            d = (
                (k[0][0] - k[1][0]) ** 2
                + (k[0][1] - k[1][1]) ** 2
                + (k[0][2] - k[1][2]) ** 2
            ) ** 0.5
            distance += d
        return distance

    # Метод изображения полиэдра
    def draw(self, tk):
        tk.clean()
        tk.draw_circle(1 * self.c)
        tk.draw_circle(4 * self.c)

        for e in self.edges:
            tk.draw_line(e.beg, e.fin)
