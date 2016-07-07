# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging

from unidecode import unidecode


def sanitize_text(text):
    """
    Sanitizes text of unknown origin, encoding and content.
    :param text: text to process
    :return: sanitized text
    """
    if text is None or text.strip() is None:
        return False

    # TODO: Make sure this below is OK.
    text = unidecode(text)

    # Collapse whitespace.
    # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160).
    text = text.replace("\xa0", " ")
    #pdf_text = " ".join(pdf_text.replace("\xa0", " ").strip().split())

    return text


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