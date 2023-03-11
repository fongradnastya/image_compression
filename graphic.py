import os
from PIL import Image, ImageDraw
from tree import Tree, MAX_DEPTH


class GifGenerator:
    """
    Класс, отвечающий за сохранение Gif-изображений
    """

    def __init__(self) -> None:
        """
        Конструктор класса, который будет сохранять гифки
        @:return: None
        """
        self.frames = []
        self.frames_count = 0
        self.gif_number = 1
        self._path = self.create_path()

    @property
    def path(self):
        """
        Получение пути к gif изображению.
        @:return: путь к изображению
        """
        return self._path

    def create_path(self) -> str:
        """
        Метод создания пути к гифке
        @:return: путь к гифке
        """
        directory = "gif"
        # Если папки .gif нет, то создаём её
        if not os.path.exists(directory):
            os.mkdir(directory)
        path = f"{directory}\\gif{self.gif_number}.gif"
        while os.path.exists(path):
            self.gif_number += 1
            path = f"{directory}\\gif{self.gif_number}.gif"
        return path

    def add_img_to_gif(self, image: Image) -> None:
        """
        Добавляет один кадр к гифке
        @:param image: Добавляемый кадр к гифке
        @:return: None
        """
        self.frames_count += 1
        self.frames.append(image)

    def save_gif(self) -> None:
        """
        Метод сохранения гифки в директорию
        @:return: None
        """
        print("Started gif creation")
        self.frames[0].save(self.path, save_all=True,
                            append_images=self.frames[1:],
                            optimize=True,
                            duration=800,
                            loop=1)
        print("Gif creation successfully completed")
        self.frames[0].close()
        self.frames.clear()
        self.frames_count = 0
        self.gif_number += 1

    @staticmethod
    def generate_image(quadtree: Tree, level: int,
                       borders: bool) -> Image:
        """
        Создание изображения на основе квадродерева
        @:param quadtree: Квадродерево
        @:param level: Уровень глубины
        @:param borders: Нужны ли границы
        @:return: Готовое изображение
        """
        # Создаём пустой холст изображения
        image = Image.new('RGB', (quadtree.width, quadtree.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, quadtree.width, quadtree.height), (0, 0, 0))
        leaf_nodes = quadtree.get_leaf_nodes(level)
        for node in leaf_nodes:
            if borders:
                draw.rectangle(node.border_box, node.average_color,
                               outline=(0, 0, 0))
            else:
                draw.rectangle(node.border_box, node.average_color)
        return image

    def compression_start(self, file: str, level: int, borders: bool,
                          gif: bool) -> None:
        """
        Начало сжатия
        @:param file: Путь к файлу
        @:param level: Уровень глубины
        @:param borders: Отображение границ
        @:param gif: Нужно ли создавать gif изображение
        @:return: None
        """
        original_image = Image.open(file)
        quadtree = Tree(original_image)
        file_name = file[:-4]
        file_extension = file[len(file) - 3::]
        result_image = self.generate_image(quadtree, level, borders)
        result_image.save(f"{file_name}_quadtree.{file_extension}")
        print("The image was compressed")
        if gif:
            for value in range(MAX_DEPTH + 1):
                new_img = self.generate_image(quadtree, value, borders)
                self.add_img_to_gif(new_img)
            self.save_gif()
