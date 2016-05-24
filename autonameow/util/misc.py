# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging


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

def unpack_dict(dt_list):
    # TODO: Finish/verify this. Not sure it is finished/correct.
    if type(dt_list) is dict:
        return dt_list
    elif type(dt_list) is not list:
        logging.warning('Got unexpected type: {}'.format(type(dt_list)))

    results = {}
    for entry in dt_list:
        if type(entry) is dict:
            if entry not in results:
                results[entry] = entry
        else:
            for content in entry:
                if type(content) is dict:
                    results.append(entry)

    return results
