# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

from core.truths import known_data_loader


def canonical_values(fieldname):
    return known_data_loader.lookup_values(fieldname) or set()


# TODO: Get valid fieldnames dynamically from the known data loader.
VALID_FIELDNAMES = frozenset(['creatortool', 'language', 'publisher'])


def incorrect_values(fieldname):
    """
    Returns values known to be incorrect for the given fieldname.

    Args:
        fieldname (str): Field value corresponding to the basenames of files
                         stored in the 'data' directory, as a Unicode string.

    Returns:
        A set of all values known to be incorrect for the given field name.
    """
    if fieldname not in VALID_FIELDNAMES:
        return set()

    other_fieldnames = [n for n in VALID_FIELDNAMES if n != fieldname]

    values = set()
    for other_fieldname in other_fieldnames:
        values.update(known_data_loader.lookup_values(other_fieldname))
        lookup = known_data_loader.literal_lookup_dict(other_fieldname)
        values.update(*lookup.values())

    return values
