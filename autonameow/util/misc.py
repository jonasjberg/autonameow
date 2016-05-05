def extract_digits(string):
    """
    Extracts digits from text string.
    :param string: string to extract digits from
    :return: digits in string or None if string contains no digits
    """
    digits = ''
    for char in string:
        if char.isdigit():
            digits += char

    return digits if digits.strip() else None

