import magic

def determine_file_type(file):
    file_type=magic.from_file(file)
    return file_type


def check_arg(a):
    return True