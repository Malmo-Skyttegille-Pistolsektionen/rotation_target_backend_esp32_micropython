import os


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
        try:
            os.stat(path)
        except OSError:
            try:
                os.mkdir(path)
            except OSError as e:
                # In MicroPython, errno.EEXIST means the directory already exists
                import errno

                if hasattr(e, "errno") and e.errno == errno.EEXIST:
                    # Directory already exists, ignore the error
                    pass
                else:
                    # Directory cannot be created for another reason, re-raise
                    raise
