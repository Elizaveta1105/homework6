from pathlib import Path
from sys import argv
from collections import defaultdict
import shutil

known_extensions = set()
unknown_extensions = set()


def mapping():
    latin_alphabet = list('abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA')
    cyrilic_alphabet = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')

    MAP = {}

    for key, value in zip(cyrilic_alphabet, latin_alphabet):
        MAP[ord(key)] = value
    return MAP


def normalize(name: str):
    is_latin = name.isascii()
    is_alphabetic = name.isalnum()

    if not is_latin:
        name = name.translate(mapping())

    if not is_alphabetic:
        for i in name:
            if not i.isalnum():
                name = name.replace(i, "_")

    return name


def is_archive(file_path):
    suffix = file_path.suffix.lower()
    return suffix in {".zip", ".gz", ".tar"}


def process_files(root_path, file_path):
    category = define_category(file_path.suffix.lower())
    if is_archive(file_path):
        try:
            extract_dir = root_path / category / file_path.stem
            shutil.unpack_archive(file_path, extract_dir)
            file_path.unlink()
        except Exception:
            file_path.unlink()
    else:
        move(root_path, file_path, category)


def create_categories():
    categories = {
        "images": ['.jpeg', '.png', '.jpg', '.svg'],
        "video": ['.avi', '.mp4', '.mov', '.mkv'],
        "documents": ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'],
        "audio": ['.mp3', '.ogg', '.wav', '.amr'],
        "archives": ['.zip', '.gz', '.tar']
    }

    reversed_categories = defaultdict(str)

    for k, value in categories.items():
        for v in value:
            reversed_categories[v] = k

    return reversed_categories


def define_category(suffix):
    categories_dict = create_categories()
    category = "others"

    if suffix in categories_dict:
        category = categories_dict[suffix]
        known_extensions.add(suffix)
    else:
        unknown_extensions.add(suffix)

    return category


def move(root_path, file_path, category):
    suffix = file_path.suffix
    name = file_path.stem
    new_name = normalize(name)+suffix
    new_folder = root_path/category
    new_path = new_folder/new_name

    new_folder.mkdir(exist_ok=True)
    file_path.rename(new_path)


def sort_folder(root_path, folder_path):
    for el in folder_path.iterdir():
        if el.is_dir():
            sort_folder(root_path, el)
            if not any(el.iterdir()):
                el.rmdir()
        elif el.is_file():
            process_files(root_path, el)


def write_to_file(known_ext, unknown_ext):
    all_known_extensions = ", ".join(list(known_ext))
    all_unknown_extensions = ", ".join(list(unknown_ext))
    with open('result.txt', "w") as f:
        f.write(f"Known extensions {all_known_extensions}\n")
        f.write(f"Unknown extensions {all_unknown_extensions}")


def main():
    path = Path(argv[1])
    sort_folder(path, path)
    write_to_file(known_extensions, unknown_extensions)


if __name__ == '__main__':
    main()
