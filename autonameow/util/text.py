# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging


def _sanitize_text(text):
    return None


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