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

# Filetags options
FILENAME_TAG_SEPARATOR = ' -- '
BETWEEN_TAG_SEPARATOR = ' '


DEFAULT_CONFIG = {
    # File rules specify conditions that should be true for the rule to apply
    # for a given file.
    #
    # If '_exact_match' is True, *all* conditions must apply for the rule to be
    # considered a match for a given file.
    # Otherwise, when '_exact_match' is False, the rule with the most amount of
    # satisfied conditions is chosen.
    # If multiple rules end up tied (same amount of satisified conditions for a
    # given file) the '_weight' is used as a last resort to pick out a single
    # rule to use.
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
         'name_format': '%(datetime)s %(description)s -- %(tags)s.%(extension)s',
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
    # Templates used when constructing new file names.
    # Can be reused by multiple file rules. Reference the template name
    # in the file rule 'name_template' field.
    'name_templates': [
        {'_description': 'First name template in the Default Configuration',
         '_name': 'default_template_name',
         'name_format': '%(title)s - %(author)s %(datetime)s.%(extension)s'},
        {'_description': 'Ebook name template in the Default Configuration',
         '_name': 'default_ebook_name',
         'name_format': '%(publisher)s %(title)s %(edition)s - %(author)s %(year)s.%(extension)s'}
    ]
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

