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

from core import version

ALL_CONDITIONS_FIELDS = {
    'filesystem': {
        'basename': None,                       # Regular expression
        'extension': None,                      # Regular expression
        'pathname': None,                       # Regular expression
        'date_accessed': None,                  # Python "datetime" format
        'date_created': None,                   # Python "datetime" format
        'date_modified': None,                  # Python "datetime" format
    },
    'contents': {
        'mime_type': None,                      # As per *NIX "file" command
    },
    'metadata': {
        'exiftool': {
            # NOTE:  See below for available exiftool fields.
            # http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
            None,
        },
    }
}


DEFAULT_CONFIG = {

    #   File Rules
    #   ==========
    #   File rules determine which files are handled and how they are handled.
    #
    #   Each rule specifies conditions that should be met for the rule to apply
    #   to a given file.
    #
    #   TODO: Document all fields ..
    #
    #   * If 'exact_match' is True, __all__ conditions must be met,
    #     otherwise the rule is considered to not apply to the given file.
    #
    #   * If 'exact_match' is False, the rule with the highest number of
    #     satisfied conditions is used.
    #     When multiple rules end up tied for the "best fit", I.E. they all
    #     have an equal amount of satisfied conditions; 'weight' is used
    #     to prioritize the candidates.
    #
    #   TODO: Document all fields ..
    #
    'FILE_RULES': [
        {'description': 'test_files Gmail print-to-pdf',
         'exact_match': True,
         'weight': None,
         'NAME_FORMAT': '{datetime} {title}.{extension}',
         'CONDITIONS': {
             'filesystem': {
                 'basename': 'gmail.pdf',
                 'extension': 'pdf',
             },
             'contents': {
                 'mime_type': 'application/pdf',
             },
         },
         'DATA_SOURCES': {
             'datetime': 'metadata.exiftool.PDF:CreateDate',
             'title': 'filesystem.basename.prefix',
             'extension': 'filesystem.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'test_files smulan.jpg',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': '{datetime} {description}.{extension}',
         'CONDITIONS': {
             'filesystem': {
                 'basename': 'smulan.jpg',
             },
             'contents': {
                 'mime_type': 'image/jpeg',
             },
         },
         'DATA_SOURCES': {
             'datetime': 'metadata.exiftool.EXIF:DateTimeOriginal',
             'description': 'plugin.microsoft_vision.caption',
             'extension': 'filesystem.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'Sample Entry for Photos with strict rules',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': '{datetime} {description} -- {tags}.{extension}',
         'CONDITIONS': {
             'filesystem': {
                 'pathname': '~/Pictures/incoming',
                 'basename': 'DCIM*',
                 'extension': 'jpg',
             },
             'contents': {
                 'mime_type': 'image/jpeg',
             },
             'metadata': {
                 'exiftool': {
                     # TODO: Ensure proper validation of entry below.
                     'EXIF:DateTimeOriginal': None,
                 },
             }
         },
         'DATA_SOURCES': {
             'datetime': ['metadata.exiftool.EXIF:DateTimeOriginal',
                          'metadata.exiftool.EXIF:DateTimeDigitized',
                          'metadata.exiftool.EXIF:CreateDate'],
             'description': 'plugin.microsoft_vision.caption',
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filesystem.basename.extension',
             'tags': 'plugin.microsoft_vision.tags'
         }
         },
        # ____________________________________________________________________
        {'description': 'Sample Entry for EPUB e-books',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': 'default_book',
         'CONDITIONS': {
             'filesystem': {
                 'pathname': None,
                 'basename': None,
                 'extension': 'epub'
             },
             'contents': {
                 'mime_type': 'application/epub+zip',
                 'metadata': 'metadata.XMP-dc.***'
             }
         },
         'DATA_SOURCES': {
             'datetime': ['metadata.exiftool.XMP-dc:PublicationDate',
                          'metadata.exiftool.XMP-dc:Date'],
             'description': None,
             'title': 'metadata.exiftool.XMP-dc:Title',
             'author': ['metadata.exiftool.XMP-dc:Creator',
                        'metadata.exiftool.XMP-dc:CreatorFile-as'],
             'publisher': 'metadata.exiftool.XMP-dc:Publisher',
             'edition': None,
             'extension': 'filesystem.basename.extension',
             'tags': None
         }
         },
    ],

    #  File Name Templates
    #  ===================
    #  These file name templates can be reused by multiple file rules.
    #  Simply add the template name to the file rule 'NAME_FORMAT' field.
    #
    #  NOTE: If a rule specifies both 'NAME_FORMAT' and 'NAME_TEMPLATE',
    #        'NAME_FORMAT' will be prioritized.
    #
    'NAME_TEMPLATES': {
        'default_document': '{title} - {author} {datetime}.{extension}',
        'default_book': '{publisher} {title} {edition} - {author} {date}.{extension}',
        'default_photo': '{datetime} {description} -- {tags}.{extension}'
    },

    #  File Name Date and Time Format
    #  ==============================
    #  Specifies the format of date and time in constructed file names.
    #  Fields are parsed with "datetime" from the Python standard library.
    #  Refer to the "datetime" library documentation for more information;
    #
    #      docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    #
    'DATETIME_FORMAT': {
        'date': '%Y-%m-%d',
        'time': '%H-%M-%S',
        'datetime': '%Y-%m-%dT%H%M%S'
    },

    #  Filetags Options
    #  ================
    #  Options for functionality related to the "filetags" workflow.
    #
    'FILETAGS_OPTIONS': {
        'filename_tag_separator': ' -- ',
        'between_tag_separator': ' '
    },

    'autonameow_version': version.__version__
}


if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 2 and '--write-default' in sys.argv:
        import os
        from datetime import datetime
        from core.config import write_yaml_file

        _this_dir = os.path.dirname(os.path.realpath(__file__))
        _basename = 'default_config_{}.yaml'.format(datetime.now().strftime('%Y-%m-%dT%H%M%S'))
        _dest = os.path.join(_this_dir, _basename)

        try:
            write_yaml_file(_dest, DEFAULT_CONFIG)
        except Exception:
            print('Unable to write DEFAULT_CONFIG to disk')
        else:
            print('Wrote DEFAULT_CONFIG to file: "{}"'.format(_dest))

