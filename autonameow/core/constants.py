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

import sys

from core.util import misc

PYTHON_VERSION = sys.version.replace('\n', '')


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


# Reference analysis results data structure with all valid fields/sources.
RESULTS_DATA_STRUCTURE = {
    'filesystem': {
        'basename': {
            'full': None,
            'prefix': None,
            'suffix': None,
            'extension': None,
            'derived_data': {
                'datetime': None,
            }
        },
        'pathname': {
            'full': None,
            'parent': None
        },
        'date_accessed': None,
        'date_created': None,
        'date_modified': None,
    },
    'contents': {
        'mime_type': None,
        'textual': {
            'raw_text': None,
            'paginated': False,
            'number_pages': None,
        },
        'visual': {
            'ocr_text': None,
            'ocr_description': None,
            'ocr_tags': None
        },
        'binary': {
            'placeholder_field': None,
        }
    },
    'metadata': {
        'exiftool': None,
        'pypdf': None,
    },
    'plugin': {
        'microsoft_vision': None,
        'guessit': None,
    }
}

# Used to validate sources defined in the configuration file.
__flat_results_data_structure = misc.flatten_dict(RESULTS_DATA_STRUCTURE)
VALID_DATA_SOURCES = list(__flat_results_data_structure.keys())


# File "magic" MIME type lookup table keyed by shorthand. Each value is a
# list of file MIME types that is classified for that particular shorthand.
MAGIC_TYPE_LOOKUP = {'bmp':   ['image/x-ms-bmp'],
                     'gif':   ['image/gif'],
                     'jpg':   ['image/jpeg'],
                     'mov':   ['video/quicktime'],
                     'mp4':   ['video/mp4'],
                     'ogg':   ['video/ogg'],
                     'pdf':   ['application/pdf'],
                     'png':   ['image/png'],
                     'txt':   ['text/plain'],
                     'empty': ['inode/x-empty']}


# Default values for required configuration fields.
FILERULE_DEFAULT_WEIGHT = 0.5
FILETAGS_DEFAULT_FILENAME_TAG_SEPARATOR = ' -- '
FILETAGS_DEFAULT_BETWEEN_TAG_SEPARATOR = ' '

# Exit code values returned to the executing shell or parent process.
# Normal, successful termination should return "0" (EXIT_SUCCESS)
# Any non-zero value is interpreted as an error. Higher values should
# correspond to increasingly critical error conditions.
EXIT_SUCCESS = 0    # Program finished successfully.
EXIT_WARNING = 1    # Program execution completed but there were errors.
EXIT_ERROR = 2      # Program execution halted due to irrecoverable errors.
