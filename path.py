import os


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_filename(path):
    return os.path.splitext(os.path.basename(path))[0]
