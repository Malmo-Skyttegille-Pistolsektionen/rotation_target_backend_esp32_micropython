import os

import stat


def is_dir(path):
    try:
        mode = os.stat(path)[0]
        return stat.S_ISDIR(mode)
    except OSError:
        return False


def make_dirs(directory: str) -> None:
    """
    Create a directory and all its parent directories if they do not exist.

    Args:
        directory (str): The path of the directory to create.
    """

    parts = directory.split("/")
    path = ""
    for part in parts:
        if not part:
            continue
        path = path + "/" + part if path else part
        if not is_dir(path):
            os.mkdir(path)
