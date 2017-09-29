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

from core import constants as C


# ALL_CONDITIONS_FIELDS
# =====================
# 'extractor.filesystem.xplat.basename.full'        Regular expression
# 'extractor.filesystem.xplat.basename.extension'   Regular expression
# 'extractor.filesystem.xplat.pathname.full'        Regular expression
# 'extractor.filesystem.xplat.date_accessed'        Python "datetime" format
# 'extractor.filesystem.xplat.date_created'         Python "datetime" format
# 'extractor.filesystem.xplat.date_modified'        Python "datetime" format
# 'extractor.filesystem.xplat.contents.mime_type'   Supports simple "globbing" ('*/jpeg')
# 'extractor.metadata.exiftool'     See note below.

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
             'extractor.filesystem.xplat.basename.full': 'gmail.pdf',
             'extractor.filesystem.xplat.basename.extension': 'pdf',
             'extractor.filesystem.xplat.contents.mime_type': 'application/pdf',
         },
         'DATA_SOURCES': {
             'datetime': 'extractor.metadata.exiftool.PDF:CreateDate',
             'title': 'extractor.filesystem.xplat.basename.prefix',
             'extension': 'extractor.filesystem.xplat.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'test_files smulan.jpg',
         'exact_match': True,
         'ranking_bias': 1,
         'NAME_FORMAT': '{datetime} {description}.{extension}',
         'CONDITIONS': {
             'extractor.filesystem.xplat.basename.full': 'smulan.jpg',
             'extractor.filesystem.xplat.contents.mime_type': 'image/jpeg',
         },
         'DATA_SOURCES': {
             'datetime': 'extractor.metadata.exiftool.EXIF:DateTimeOriginal',
             'description': 'plugin.microsoft_vision.caption',
             'extension': 'extractor.filesystem.xplat.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'test_files simplest_pdf.md.pdf',
         'exact_match': True,
         'ranking_bias': 1,
         'NAME_FORMAT': 'simplest_pdf.md.{extension}',
         'CONDITIONS': {
             'extractor.filesystem.xplat.basename.full': 'simplest_pdf.md.pdf',
         },
         'DATA_SOURCES': {
             'extension': 'extractor.filesystem.xplat.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'Sample Entry for Photos with strict rules',
         'exact_match': True,
         'ranking_bias': 1,
         'NAME_FORMAT': '{datetime} {description} -- {tags}.{extension}',
         'CONDITIONS': {
             'extractor.filesystem.xplat.pathname.full': '~/Pictures/incoming',
             'extractor.filesystem.xplat.basename.full': 'DCIM*',
             'extractor.filesystem.xplat.basename.extension': 'jpg',
             'extractor.filesystem.xplat.contents.mime_type': 'image/jpeg',
             # TODO: [TD0015] Ensure proper validation of entry below.
             'extractor.metadata.exiftool.EXIF:DateTimeOriginal': 'Defined',
         },
         'DATA_SOURCES': {
             'datetime': ['extractor.metadata.exiftool.EXIF:DateTimeOriginal',
                          'extractor.metadata.exiftool.EXIF:DateTimeDigitized',
                          'extractor.metadata.exiftool.EXIF:CreateDate'],
             'description': 'plugin.microsoft_vision.caption',
             'extension': 'extractor.filesystem.xplat.basename.extension',
             'tags': 'plugin.microsoft_vision.tags'
         }
         },
        # ____________________________________________________________________
        {'description': 'Sample Entry for E-books',
         'exact_match': True,
         'ranking_bias': 0.1,
         'NAME_FORMAT': 'default_book',
         'CONDITIONS': {
             'extractor.filesystem.xplat.contents.mime_type': [
                 'application/pdf',
                 'application/epub+zip',
                 'image/vnd.djvu',
             ],
             'extractor.filesystem.xplat.pathname.full': '.*book.*'
         },
         'DATA_SOURCES': {
             'author': 'analysis.ebook.author',
             'extension': 'extractor.filesystem.xplat.contents.mime_type',
             'date': 'analysis.ebook.date',
             'edition': 'analysis.ebook.edition',
             'publisher': 'analysis.ebook.publisher',
             'title': 'analysis.ebook.title',
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

    #  Filesystem Options
    #  ==================
    #  Specify patterns for files to be ignored.
    #  These are added on to the defaults specified in 'constants.py'.
    'FILESYSTEM_OPTIONS': {
        'ignore': ['*.swp', '*/.*'],
    },

    #  Custom Post-Processing Options
    #  ==============================
    #  Pairs of substrings to match and replace during the last post-processing
    #  just before the file is renamed. The syntax is 'MATCH: REPLACE'
    #  For instance, using "'foo': 'bar'" would result in every occurrence of
    #  "foo" in a file name to be replaced by "bar".
    'CUSTOM_POST_PROCESSING': {
        'replacements': {
            '_{2,}': '_',
            '-{2,}': '-',
            '\.{2,}': '.'
        },
        'lowercase_filename': False,
        'uppercase_filename': False,
        'sanitize_filename': True,
        'sanitize_strict': False
    },

    #  Filetags Options
    #  ================
    #  Options for functionality related to the "filetags" workflow.
    #
    'FILETAGS_OPTIONS': {
        'filename_tag_separator': ' -- ',
        'between_tag_separator': ' '
    },

    'autonameow_version': C.STRING_PROGRAM_VERSION
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

