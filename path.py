import os


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def check_file(path):
    check_path(os.path.dirname(path))


def get_filename(path):
    return os.path.splitext(os.path.basename(path))[0]
