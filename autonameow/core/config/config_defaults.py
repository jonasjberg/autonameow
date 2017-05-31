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

# TODO: Integrate filetags options with new configuration format.
FILENAME_TAG_SEPARATOR = ' -- '
BETWEEN_TAG_SEPARATOR = ' '


DEFAULT_CONFIG = {

    #   File Rules
    #   ----------
    #   File rules determine which files are handled and how they are handled.
    #
    #   Each rule specifies conditions that should be met for the rule to apply
    #   to a given file.
    #
    #   TODO: Document all fields ..
    #
    #   * If '_exact_match' is True, __all__ conditions must be met,
    #     otherwise the rule is considered to not apply to the given file.
    #
    #   * If '_exact_match' is False, the rule with the highest number of
    #     satisfied conditions is used.
    #     When multiple rules end up tied for the "best fit", I.E. they all
    #     have an equal amount of satisfied conditions; '_weight' is used
    #     to prioritize the candidates.
    #
    #   TODO: Document all fields ..
    #
    'file_rules': [
        {'_description': 'First Entry in the Default Configuration',
         '_exact_match': False,
         '_weight': None,
         'name_template': 'default_template_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': None
             },
             'contents': {
                 'mime_type': None
             }
         },
         'data_sources': {
             'datetime': None,
             'description': None,
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filename.extension'
         }
         },
        {'_description': 'Sample Entry for Photos with strict rules',
         '_exact_match': True,
         '_weight': 1,
         'name_format': '{datetime} {description} -- {tags}.{extension}',
         'conditions': {
             'filename': {
                 'pathname': '~/Pictures/incoming',
                 'basename': 'DCIM*',
                 'extension': 'jpg'
             },
             'contents': {
                 'mime_type': 'image/jpeg',
                 'metadata': 'exif.datetimeoriginal'
             }
         },
         'data_sources': {
             'datetime': ['metadata.exif.datetimeoriginal',
                          'metadata.exif.datetimedigitized',
                          'metadata.exif.createdate'],
             'description': 'plugin.microsoftvision.caption',
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filename.extension',
             'tags': 'plugin.microsoftvision.tags'
         }
         },
        {'_description': 'Sample Entry for EPUB e-books',
         '_exact_match': True,
         '_weight': 1,
         'name_format': '',
         'name_template': 'default_ebook_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': 'epub'
             },
             'contents': {
                 'mime_type': 'application/epub+zip',
                 'metadata': 'metadata.XMP-dc.***'
             }
         },
         'data_sources': {
             'datetime': ['metadata.XMP-dc.PublicationDate',
                          'metadata.XMP-dc.Date'],
             'description': None,
             'title': 'metadata.XMP-dc.Title',
             'author': ['metadata.XMP-dc.Creator',
                        'metadata.XMP-dc.CreatorFile-as'],
             'publisher': 'metadata.XMP-dc.Publisher',
             'edition': None,
             'extension': 'filename.extension',
             'tags': None
         }
         },
        {'_description': 'Sample Entry for MOBI e-books',
         '_exact_match': True,
         '_weight': 1,
         'name_format': None,
         'name_template': 'default_ebook_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': ['mobi']
             },
             'contents': {
                 'mime_type': 'application/x-mobipocket-ebook',
                 'metadata': 'metadata.MOBI.***'
             }
         },
         'data_sources': {
             'datetime': ['metadata.MOBI.PublishDate'],
             'description': ['metadata.MOBI.Description',
                             'metadata.MOBI.Subject'],
             'title': ['metadata.MOBI.BookName',
                       'metadata.MOBI.UpdatedTitle'],
             'author': 'metadata.MOBI.Author',
             'publisher': 'metadata.MOBI.Publisher',
             'extension': 'filename.extension',
             'tags': None
         }
         }
    ],

    #  File Name Templates
    #  -------------------
    #  These file name templates can be reused by multiple file rules.
    #  Simply add the template name to the file rule 'name_template' field.
    #
    #  NOTE: If a rule specifies both 'name_format' and 'name_template',
    #        'name_format' will be prioritized.
    #
    'name_templates': [
        {'_description': 'First name template in the Default Configuration',
         '_name': 'default_template_name',
         'name_format': '{title} - {author} {datetime}.{extension}'},
        {'_description': 'Ebook name template in the Default Configuration',
         '_name': 'default_ebook_name',
         'name_format': '{publisher} {title} {edition} - {author} {year}.{extension}'}
    ],

    #  File Name Date and Time Format
    #  ------------------------------
    #  Specifies the format of date and time in constructed file names.
    #  Fields are parsed with "datetime" from the Python standard library.
    #  Refer to the "datetime" library documentation for more information;
    #
    #      docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    #
    'name_datetime_format': {
        'date': '%Y-%m-%d',
        'time': '%H-%M-%S',
        'datetime': '%Y-%m-%dT%H%M%S'
    },
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

