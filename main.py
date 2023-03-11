import argparse
import os

from graphic import GifGenerator, MAX_DEPTH


def check_arguments(args):
    if os.path.exists(args.img):
        if args.img.endswith('.png') or args.img.endswith('.jpg'):
            if 0 < args.level <= MAX_DEPTH:
                return True
            else:
                print("The compression ratio should be between 1 and 8")
        else:
            print("Wrong file type!")
    else:
        print("Wrong image path!")
    return False


def parse():
    # Осуществляем разбор аргументов командной строки
    parser = argparse.ArgumentParser(description="Сжатие изображений на основе"
                                                 " квадродеревьев")
    parser.add_argument("-i", "--img", dest="img", type=str,
                        help="Исходный файл изображения", required=True)
    parser.add_argument("-l", "--level", dest="level", type=int,
                        help="Уровень сжатия", required=True)
    parser.add_argument("-b", "--borders", dest="borders", action="store_true",
                        help="Отображение границ")
    parser.add_argument("-g", "--gif", dest="gif", action="store_true",
                        help="Создание gif-изображения")
    args = parser.parse_args()
    if check_arguments(args):
        gif = GifGenerator()
        gif.compression_start(args.img, args.level, args.borders, args.gif)


if __name__ == "__main__":
    parse()
