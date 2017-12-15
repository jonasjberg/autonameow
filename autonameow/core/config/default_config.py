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

#   TODO: Document all fields ..

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
    'RULES': {
        'test_files Gmail print-to-pdf': {
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
        'test_files smulan.jpg': {
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
        'test_files simplest_pdf.md.pdf': {
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
        'Sample Entry for Photos with strict rules': {
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
                'datetime': [
                    'extractor.metadata.exiftool.EXIF:DateTimeOriginal',
                    'extractor.metadata.exiftool.EXIF:DateTimeDigitized',
                    'extractor.metadata.exiftool.EXIF:CreateDate'
                ],
                'description': 'plugin.microsoft_vision.caption',
                'extension': 'extractor.filesystem.xplat.basename.extension',
                'tags': 'plugin.microsoft_vision.tags'
            }
        },
        # ____________________________________________________________________
        'Sample Entry for E-books': {
            'exact_match': False,
            'ranking_bias': 0.1,
            'NAME_FORMAT': 'default_book',
            'CONDITIONS': {
                'extractor.filesystem.xplat.contents.mime_type': [
                    'application/epub+zip',
                    'image/vnd.djvu',
                    'application/pdf',
                    'application/octet-stream',
                ],
                'extractor.filesystem.xplat.basename.extension': '(pdf|mobi)',
            },
            'DATA_SOURCES': {
                'author': 'analyzer.ebook.author',
                'extension': 'extractor.filesystem.xplat.contents.mime_type',
                'year': 'analyzer.ebook.date',
                'edition': [
                    'analyzer.ebook.edition',
                    'analyzer.filename.edition'
                ],
                'publisher': [
                    'analyzer.ebook.publisher',
                    'analyzer.filename.publisher'
                ],
                'title': 'analyzer.ebook.title',
            },
        },
    },

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
        'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}',
        'default_photo': '{datetime} {description} -- {tags}.{extension}'
    },

    #  Name Template Fields
    #  ====================
    #  Known good candidates for fields.
    #  For instance, the publisher field lists user-defined book publisher
    #  candidates along with a list of patterns that if matched, would be
    #  replaced with the candidate name.
    'NAME_TEMPLATE_FIELDS': {
        'publisher': {
            'candidates': {
                'ProjectGutenberg': ['Project Gutenberg', 'www.gutenberg.net'],
                'FeedBooks': ['This book is brought to you by Feedbooks',
                              'http://www.feedbooks.com']
            },
        },
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

    #  Persistence Options
    #  ===================
    #  Controls how autonameow stores persistent data to disk.
    'PERSISTENCE': {
        'cache_directory': None,
        'history_file_path': None,
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
        'sanitize_strict': False,
        'simplify_unicode': True
    },

    #  Filetags Options
    #  ================
    #  Options for functionality related to the "filetags" workflow.
    #
    'FILETAGS_OPTIONS': {
        'filename_tag_separator': ' -- ',
        'between_tag_separator': ' '
    },

    'COMPATIBILITY': {
        '{}_version'.format(C.STRING_PROGRAM_NAME): C.STRING_PROGRAM_VERSION
    }
}


if __name__ == '__main__':
    """
    Run as stand-alone to write DEFAULT_CONFIG to a YAML-file.

    NOTE: Relative imports require PYTHONPATH to be set ..
          Workaround wrapper-script at "devscripts/write-default-config.sh"
    """
    from datetime import datetime
    import os
    import sys
    from core import disk


    def default_destpath():
        basename = 'default_config_{}.yaml'.format(
            datetime.now().strftime('%Y-%m-%dT%H%M%S')
        )
        this_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.normpath(os.path.join(this_dir, basename))

    if len(sys.argv) > 1 and sys.argv[1] == '--write-default':
        if len(sys.argv) > 2:
            dest_path = sys.argv[2]
        else:
            dest_path = default_destpath()

        if os.path.exists(dest_path):
            print('[ERROR] Destination exists: "{!s}"'.format(dest_path))
            sys.exit(1)

        try:
            disk.write_yaml_file(dest_path, DEFAULT_CONFIG)
        except Exception as e:
            print('[ERROR] Unable to write DEFAULT_CONFIG to disk!')
            print('Destination path: "{!s}"'.format(dest_path))
            print(str(e))
        else:
            print('Wrote DEFAULT_CONFIG: "{}"'.format(dest_path))
            sys.exit(0)

    else:
        print('''
Writes the default configuration to a YAML-file.

USAGE:  {progname} --write-default ([PATH])

Argument [PATH] is optional and defaults to:
"{default_path}"

Returns exit code 0 if the file is written successfully.
'''.format(progname=__file__, default_path=default_destpath()))
