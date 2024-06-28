import os


def clear_console():
    command = "clear"
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)