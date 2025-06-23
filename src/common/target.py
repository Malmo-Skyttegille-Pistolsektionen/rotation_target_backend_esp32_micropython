from common.common import program_state


def show():
    program_state.target_status_shown = True
    pass


def hide():
    program_state.target_status_shown = False
    pass
