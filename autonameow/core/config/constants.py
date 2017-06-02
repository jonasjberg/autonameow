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


# Each analyzer can be queried for these fields by calling either;
#   the_analyzer.get_FIELD()   or   the_analyzer.get('FIELD')
ANALYSIS_RESULTS_FIELDS = ['datetime', 'publisher', 'title', 'tags', 'author']


# All possible field names. Used for constructing file names and testing.
# The dictionary is populated like this;
#
#   DATA_FIELDS = {'author': 'DUMMY',
#                  'datetime': 'DUMMY',
#                  'description': 'DUMMY',
#                  'edition': 'DUMMY',
#                  'extension': 'DUMMY',
#                  'publisher': 'DUMMY',
#                  'tags': 'DUMMY',
#                  'title': 'DUMMY',
#                  'year': 'DUMMY'}
DATA_FIELDS = dict.fromkeys(ANALYSIS_RESULTS_FIELDS +
                            ['edition', 'date', 'description', 'extension'],
                            'DUMMY')


# File "magic" MIME type lookup table keyed by shorthand. Each value is a
# list of file MIME types that is classified for that particular shorthand.
MAGIC_TYPE_LOOKUP = {'bmp':   ['image/x-ms-bmp'],
                     'gif':   ['image/gif'],
                     'jpg':   ['image/jpeg'],
                     'mp4':   ['video/mp4'],
                     'ogg':   ['video/ogg'],
                     'pdf':   ['application/pdf'],
                     'png':   ['image/png'],
                     'txt':   ['text/plain'],
                     'empty': ['inode/x-empty']}


# Default values for required configuration fields.
FILERULE_DEFAULT_WEIGHT = 0.5