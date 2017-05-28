# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
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

from core.analyze.analysis import ANALYSIS_RESULTS_FIELDS


# All possible field names. Used for constructing file names and testing.
# The dictionary is populated like this;
#
#   DATA_FIELDS = {'datetime': 'DUMMY',
#                  'publisher': 'DUMMY',
#                  'title': 'DUMMY',
#                  'tags': 'DUMMY',
#                  'author': 'DUMMY',
#                  'extension': 'DUMMY',
#                  'description': 'DUMMY'}

DATA_FIELDS = dict.fromkeys(ANALYSIS_RESULTS_FIELDS +
                            ['edition', 'year', 'description', 'extension'], 'DUMMY')

MAGIC_TYPE_LOOKUP = {'bmp':   ['image/x-ms-bmp'],
                     'gif':   ['image/gif'],
                     'jpg':   ['image/jpeg'],
                     'mp4':   ['video/mp4'],
                     'ogg':   ['video/ogg'],
                     'pdf':   ['application/pdf'],
                     'png':   ['image/png'],
                     'txt':   ['text/plain'],
                     'empty': ['inode/x-empty']}