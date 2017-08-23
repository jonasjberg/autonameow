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

from core import constants


# ALL_CONDITIONS_FIELDS
# =====================
# 'filesystem.basename.full'        Regular expression
# 'filesystem.basename.extension'   Regular expression
# 'filesystem.pathname.full'        Regular expression
# 'filesystem.date_accessed'        Python "datetime" format
# 'filesystem.date_created'         Python "datetime" format
# 'filesystem.date_modified'        Python "datetime" format
# 'filesystem.contents.mime_type'   Supports simple "globbing" ('*/jpeg')
# 'metadata.exiftool'               See note below.

#   NOTE:  See this link for all available exiftool fields.
#   http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html


DEFAULT_CONFIG = {

    #   Rules
    #   =====
    #   Rules determine which files are handled and how they are handled.
    #
    #   Each rule specifies conditions that should be met for the rule to apply
    #   to a given file.
    #
    #   TODO: Document all fields ..
    #
    #   * If 'exact_match' is True, __all__ conditions must be met,
    #     otherwise the rule is considered to not apply to the given file.
    #
    #   * If 'exact_match' is False, the rule is kept even if a condition fails.
    #
    #   TODO: Document all fields ..
    #
    'RULES': [
        {'description': 'test_files Gmail print-to-pdf',
         'exact_match': True,
         'ranking_bias': None,
         'NAME_FORMAT': '{datetime} {title}.{extension}',
         'CONDITIONS': {
             'filesystem.basename.full': 'gmail.pdf',
             'filesystem.basename.extension': 'pdf',
             'filesystem.contents.mime_type': 'application/pdf',
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
         'ranking_bias': 1,
         'NAME_FORMAT': '{datetime} {description}.{extension}',
         'CONDITIONS': {
             'filesystem.basename.full': 'smulan.jpg',
             'filesystem.contents.mime_type': 'image/jpeg',
         },
         'DATA_SOURCES': {
             'datetime': 'metadata.exiftool.EXIF:DateTimeOriginal',
             'description': 'plugin.microsoft_vision.caption',
             'extension': 'filesystem.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'test_files simplest_pdf.md.pdf',
         'exact_match': True,
         'ranking_bias': 1,
         'NAME_FORMAT': 'simplest_pdf.md.{extension}',
         'CONDITIONS': {
             'filesystem.basename.full': 'simplest_pdf.md.pdf',
         },
         'DATA_SOURCES': {
             'extension': 'filesystem.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'Sample Entry for Photos with strict rules',
         'exact_match': True,
         'ranking_bias': 1,
         'NAME_FORMAT': '{datetime} {description} -- {tags}.{extension}',
         'CONDITIONS': {
             'filesystem.pathname.full': '~/Pictures/incoming',
             'filesystem.basename.full': 'DCIM*',
             'filesystem.basename.extension': 'jpg',
             'filesystem.contents.mime_type': 'image/jpeg',
             # TODO: [TD0015] Ensure proper validation of entry below.
             'metadata.exiftool.EXIF:DateTimeOriginal': 'Defined',
         },
         'DATA_SOURCES': {
             'datetime': ['metadata.exiftool.EXIF:DateTimeOriginal',
                          'metadata.exiftool.EXIF:DateTimeDigitized',
                          'metadata.exiftool.EXIF:CreateDate'],
             'description': 'plugin.microsoft_vision.caption',
             'extension': 'filesystem.basename.extension',
             'tags': 'plugin.microsoft_vision.tags'
         }
         },
        # ____________________________________________________________________
        {'description': 'Sample Entry for EPUB e-books',
         'exact_match': True,
         'ranking_bias': 1,
         'NAME_FORMAT': 'default_book',
         'CONDITIONS': {
             'filesystem.pathname.full': '.*',
             'filesystem.basename.full': '.*',
             'filesystem.basename.extension': 'epub',
             'filesystem.contents.mime_type': 'application/epub+zip',
             # TODO: [TD0015] Ensure proper validation of entry below.
             'metadata.exiftool.XMP-dc:Creator': 'Defined',
         },
         'DATA_SOURCES': {
             'datetime': ['metadata.exiftool.XMP-dc:PublicationDate',
                          'metadata.exiftool.XMP-dc:Date'],
             'title': 'metadata.exiftool.XMP-dc:Title',
             'author': ['metadata.exiftool.XMP-dc:Creator',
                        'metadata.exiftool.XMP-dc:CreatorFile-as'],
             'publisher': 'metadata.exiftool.XMP-dc:Publisher',
             'edition': None,
             'extension': 'filesystem.basename.extension',
         }
         },
    ],

    #  File Name Templates
    #  ===================
    #  These file name templates can be reused by multiple rules.
    #  Simply add the template name to the rule 'NAME_FORMAT' field.
    #
    #  NOTE: If a rule specifies both 'NAME_FORMAT' and 'NAME_TEMPLATE',
    #        'NAME_FORMAT' will be prioritized.
    #
    'NAME_TEMPLATES': {
        'default_document': '{title} - {author} {datetime}.{extension}',
        'default_book': '{publisher} {title} {edition} - {author} {datetime}.{extension}',
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

    #  Filesystem Options
    #  ==================
    #  Options for how filenames are written do disk. Allowed/blacklisted
    #  characters and potentially custom replacements, etc.
    'FILESYSTEM_OPTIONS': {
        'sanitize_filename': True,
        'sanitize_strict': False,
        'ignore': ['*/.DS_Store', '*/Thumbs.db', '*~', '*.swp']
    },

    #  Filetags Options
    #  ================
    #  Options for functionality related to the "filetags" workflow.
    #
    'FILETAGS_OPTIONS': {
        'filename_tag_separator': ' -- ',
        'between_tag_separator': ' '
    },

    'autonameow_version': constants.PROGRAM_VERSION
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

