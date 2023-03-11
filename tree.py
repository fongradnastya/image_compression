import threading
from typing import Optional
from PIL import Image

MAX_DEPTH = 8  # Максимальная глубина узла
MAX_VALUE = 13  # Порог значения


class Point:
    """Класс точки."""

    def __init__(self, x_pos: int, y_pos: int) -> None:
        """
        Конструктор класса точки.
        :param x_pos: Координата x
        :param y_pos: Координата y
        :return: None
        """
        self._x_pos = x_pos
        self._y_pos = y_pos

    @property
    def x_pos(self):
        return self._x_pos

    @property
    def y_pos(self):
        return self._y_pos

    def __eq__(self, another: "Point") -> bool:
        """
        Сравнение двух точек.
        :param another: Точка для сравнения
        :return: Результат сравнения
        """
        return self._x_pos == another._y_pos and self._y_pos == another._y_pos

    def __repr__(self) -> str:
        """
        Строковое представление точки.
        :return: Cтроковое представление точки
        """
        return f"Point: ({self._x_pos}, {self._y_pos})"


def average_color(hist: list[int]):
    """
    Возвращает взвешенное среднее значение цвета и
    ошибку из гистограммы пикселей.
    :param hist: список количества пикселей для каждого диапазона.
    :return: взвешенное среднее значение цвета и ошибка
    """
    c_sum = sum(hist)
    if c_sum > 0:
        value = sum(i * x for i, x in enumerate(hist))
        value /= c_sum
        error = sum(x * (value - i) ** 2 for i, x in enumerate(hist))
        error = (error / c_sum) ** 0.5
        return value, error
    return 0, 0


def color_from_histogram(hist: list[int]):
    """
    Возвращает средний цвет RGB из заданной гистограммы
    количества цветов пикселей.
    :param hist: список количества пикселей для каждого диапазона.
    :return: Cредний цвет и ошибка.
    """
    red, red_error = average_color(hist[:256])
    green, green_error = average_color(hist[256:512])
    blue, blue_error = average_color(hist[512:768])
    error = red_error * 0.2989 + green_error * 0.5870 + blue_error * 0.1140
    return (int(red), int(green), int(blue)), error


class TreeNode:
    """
    Класс, отвечающий за узел квадродерева,
    который содержит секцию изображения и информацию о ней.
    """
    def __init__(self, image: Image, border_box: tuple[int], deep: int) -> \
            None:
        """
        Конструктор класса.
        :param image: изображение
        :param border_box: координатная область
        :param deep: глубина
        :return: None
        """
        self._border_box = border_box  # регион копирования
        self._deep = deep
        self._children = None  # top left,top right,bottom left,bottom right
        self._is_leaf = False
        self.node_points = []
        print(self._border_box)
        left_right = self._border_box[0] + (self._border_box[2] -
                                            self._border_box[0]) / 2
        top_bottom = self._border_box[1] + (self._border_box[3] -
                                            self._border_box[1]) / 2

        self._node_center_point = Point(left_right, top_bottom)
        # Обрезка части изображения по координатам
        image = image.crop(border_box)
        # 256 типа красного, 256 типов зеленого и 256 синего.
        hist = image.histogram()
        self._average_color, self._error = color_from_histogram(hist)

    @property
    def depth(self) -> int:
        """
        Возвращает значение глубины.
        :return: Значение глубины.
        """
        return self._deep

    @property
    def node_center_point(self) -> Point:
        """
        Возвращает координаты центральной точки узла.
        :return: Координаты центральной точки.
        """
        return self._node_center_point

    @property
    def error(self) -> float:
        """
        Возвращает значения ошибки.
        :return: Значение ошибки.
        """
        return self._error

    @property
    def average_color(self) -> tuple[int, int, int]:
        """
        Возвращает значения цвета
        :return: Значение цвета.
        """
        return self._average_color

    @property
    def children(self) -> Optional[list]:
        """
        Возвращение дочерних узлов.
        :return: Список с дочерними узлами.
        """
        return self._children

    @property
    def border_box(self) -> tuple[int]:
        """
        Возвращает координаты граничных точек.
        :return: Координаты точек.
        """
        return self._border_box

    @property
    def is_leaf(self) -> bool:
        """
        Является ли узел листом или нет.
        :return: Логическое значение
        """
        return self._is_leaf

    @is_leaf.setter
    def is_leaf(self, value: bool) -> None:
        """
        Квадрант становится листом.
        :param value: Булевое значение
        :return: None
        """
        self._is_leaf = value

    def __repr__(self) -> str:
        """
        Строковое представление узла
        :return: строковое представление узла.
        """
        return f"Узел дерева: {self._border_box}"

    def split(self, image: Image) -> None:
        """
        Разбивает данную секцию изображения на четыре равных блока.
        :param image: Изображение
        :return: None
        """
        left, top, right, bottom = self._border_box
        box = (left, top, self._node_center_point.x_pos,
            self._node_center_point.y_pos)
        top_left = TreeNode(image, box, self._deep + 1)
        box = (self._node_center_point.x_pos, top, right,
               self._node_center_point.y_pos)
        top_right = TreeNode(image, box, self._deep + 1)
        box = (left, self._node_center_point.y_pos,
               self._node_center_point.x_pos, bottom)
        bottom_left = TreeNode(image, box, self._deep + 1)
        box = (self._node_center_point.x_pos, self._node_center_point.y_pos,
               right, bottom),
        bottom_right = TreeNode(image, box, self._deep + 1)
        self._children = [top_left, top_right, bottom_left, bottom_right]

    def insert_point(self, point: Point) -> "function":
        """
        Вставка точки в подходящий узел
        :param point: Точка, которая должна быть вставлена
        :return: None или рекурсивный вызов функции.
        """
        if self.children is not None:
            if point.x_pos < self._node_center_point.x_pos and point.y_pos < \
                    self._node_center_point.y_pos:
                return self.children[0].insert_point(point)
            if point.x_pos >= self._node_center_point.x_pos and \
                    point.y_pos < self._node_center_point.y_pos:
                return self.children[1].insert_point(point)
            if point.x_pos < self._node_center_point.x_pos and \
                    point.y_pos >= self._node_center_point.y_pos:
                self.children[2].insert_point(point)
            if point.x_pos >= self._node_center_point.x_pos and \
                    point.y_pos >= self._node_center_point.y_pos:
                self.children[3].insert_point(point)
        self.node_points.append(point)

    def find_node_contain_point(self, point, search_list: list = None):
        """
        Возвращает узел, содержащий точку и путь до узла.
        :param point: искомая точка
        :param search_list: список узлов
        :return: узел и список узлов
        """
        if not search_list:
            search_list = []
        search_list.append(self)
        if self.children is not None:
            if point.x_pos < self._node_center_point.x_pos and \
                    point.y_pos < self._node_center_point.y_pos:
                if self.children[0] is not None:
                    return self.children[0].find_node(point, search_list)
            elif point.x_pos >= self._node_center_point.x_pos and \
                    point.y_pos < self._node_center_point.y_pos:
                if self.children[1] is not None:
                    return self.children[1].find_node(point, search_list)
            elif point.x_pos < self._node_center_point.x_pos and \
                    point.y_pos >= self._node_center_point.y_pos:
                if self.children[2] is not None:
                    return self.children[2].find_node(point, search_list)
            elif point.x_pos >= self._node_center_point.x_pos and \
                    point.y_pos >= self._node_center_point.y_pos:
                if self.children[3] is not None:
                    return self.children[3].find_node(point, search_list)
        return self

    def remove_point(self, delete_point: Point) -> None:
        """
        Удаление точки.
        :param delete_point: Удаляемая точка.
        :return: None
        """
        current_node = self.find_node_contain_point(delete_point)
        if current_node is not None:
            for point in current_node.node_points:
                if point == delete_point:
                    current_node.node_points.remove(point)


class Tree:
    """Класс квадродерева."""

    def __init__(self, image: Image) -> None:
        """
        Конструктор класса
        :param image: исходное изображение.
        :return: None
        """
        self._width, self._height = image.size
        self._root = TreeNode(image, image.getbbox(), 0)
        # отслеживает максимальную глубину, достигнутую рекурсией
        self._max_deep = 0
        self._build_tree(image, self._root)

    @property
    def width(self) -> int:
        """
        Возвращает ширину исходного изображения
        :return: ширина исходного изображения
        """
        return self._width

    @property
    def height(self) -> int:
        """
        Возвращает высоту исходного изображения
        :return: высота изображения
        """
        return self._height

    @property
    def max_depth(self) -> int:
        """
        Возвращает максимальную глубину, достигнутую рекурсией.
        :return: Значение максимальной глубины.
        """
        return self._max_deep

    @property
    def root(self) -> TreeNode:
        """
        Возвращает корневой узел
        :return: высота изображения
        """
        return self._root

    def _build_tree(self, image: Image, node: TreeNode) -> None:
        """
        Рекурсивно добавляет узлы, пока не будет достигнута макс. глубина
        :param image: исходное изображение
        :param node: узел
        :return: None
        """
        if (node.depth >= MAX_DEPTH) or (node.error <= MAX_VALUE):
            if node.depth > self._max_deep:
                self._max_deep = node.depth
            node.is_leaf = True
            return None
        node.split(image)
        threads = []
        for child in node.children:
            thread = threading.Thread(target=self._build_tree,
                                      args=(image, child))
            thread.start()
            threads.append(thread)
        for process in threads:
            process.join()
        return None

    def get_leaf_nodes(self, deep: int) -> list:
        """
        Получаем листья дерева.
        :param deep: Значение глубины рекурсии.
        :return: Список листьев
        """
        if deep > self._max_deep:
            raise ValueError('Дана глубина больше, чем высота деревьев')
        leaf_nodes = []
        # рекурсивный поиск по квадродереву
        self.get_leaf_nodes_recursion(self._root, deep, leaf_nodes)
        return leaf_nodes

    def get_leaf_nodes_recursion(self, node: TreeNode, depth: int,
                                 leaf_nodes: list) -> None:
        """
        Рекурсивно получает листовые узлы в зависимости от того,
        является ли узел листом или достигнута заданная глубина.
        :param node: Узел
        :param depth: значение глубины
        :param leaf_nodes: Список листьев
        :return:
        """
        if node.is_leaf is True or node.depth == depth:
            leaf_nodes.append(node)
        elif node.children is not None:
            for child in node.children:
                self.get_leaf_nodes_recursion(child, depth, leaf_nodes)
