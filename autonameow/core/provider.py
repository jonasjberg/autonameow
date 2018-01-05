# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
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

from collections import defaultdict

from core import (
    providers,
    repository
)


class MasterDataProvider(object):
    """
    Handles top-level data retrieval and data extraction delegation.

    Part of restructuring the overall architecture to fetch data lazily while
    evaluating rule conditions, etc.
    """
    def __init__(self):
        self.seen_fileobject_meowuris = defaultdict(dict)

    def query(self, fileobject, meowuri):
        _data_maybe = repository.SessionRepository.query(fileobject, meowuri)
        if _data_maybe:
            self.seen_fileobject_meowuris[fileobject][meowuri] = _data_maybe
            return _data_maybe

        _possible_providers = providers.get_providers_for_meowuri(meowuri)
        # TODO: [TD0142] Rework overall architecture to fetch data when needed.
        print(_possible_providers)


_master_data_provider = MasterDataProvider()


def query(fileobject, meowuri):
    return _master_data_provider.query(fileobject, meowuri)
