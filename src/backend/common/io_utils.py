import os


def dir_exists(directory: str) -> bool:
    try:
        return (os.stat(directory)[0] & 0o170000) == 0o040000
    except OSError:
        return False


def file_exists(filename: str):
    try:
        return (os.stat(filename)[0] & 0o170000) == 0o100000
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
        if not dir_exists(path):
            os.mkdir(path)


def path_join(*parts):
    return "/".join(part.strip("/") for part in parts if part)
