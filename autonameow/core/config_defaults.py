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

# Default match rename template:
DEFAULT_NAME = '%(date)s_%(time)s %(description)s -- %(tags)s%(ext)s'

# Rename templates:
DOCUMENT_NAME = '%(date)s %(title)s %(author)s -- %(tags)s%(ext)s'
EBOOK_NAME = '%(author)s %(date)s %(publisher)s - %(title)s%(ext)s'

# Rule fields:
# 'type'              --  mime file type
#                         can be either a single item or a list of items,
#                         where one match in the list counts as a positive.
# 'name'              --  Regular expression matching the basename.
#                         (any leading directories removed)
# 'path'              --  TODO: Decide on behaviour/format.
# 'prefer_datetime'   --  TODO: Decide on behaviour/format.
# 'prefer_title'      --  TODO: Decide on behaviour/format.
# 'new_name_template' --  Template used to construct a new filename.
#
# **Rule ordering matters** -- the first matching rule is used.
rules = {'record_my_desktop': {'type': ['ogv', 'ogg'],
                               'name': None,
                               'path': None,
                               'prefer_datetime': 'accessed',
                               'prefer_title': None,
                               'new_name_template': DEFAULT_NAME,
                               'tags': []},
         'photo_oneplusx': {'type': 'jpg',
                            'name': r'^IMG_\d{8}_\d{6}\.jpg$',
                            'path': None,
                            'prefer_datetime': 'very_special_case',
                            'prefer_title': None,
                            'new_name_template': DEFAULT_NAME,
                            'tags': []},
         'photo_android_msg': {'type': 'jpg',
                               'name': r'^received_\d{15,17}\.jpeg$',
                               'path': None,
                               'prefer_datetime': 'android_messenger',
                               'prefer_title': None,
                               'new_name_template': DEFAULT_NAME,
                               'tags': []},
         'screencapture': {'type': 'png',
                           'name': r'^screencapture.*.png$',
                           'path': None,
                           'prefer_datetime': 'screencapture_unixtime',
                           'prefer_title': None,
                           'new_name_template': DEFAULT_NAME,
                           'tags': ['screenshot']},
         'filetagsscreenshot': {'type': 'png',
                                'name': None,
                                'path': None,
                                'prefer_datetime': 'very_special_case',
                                'prefer_title': None,
                                'new_name_template': DEFAULT_NAME,
                                'tags': ['screenshot']},
         'filetagsphoto': {'type': 'jpg',
                           'name': None,
                           'path': None,
                           'prefer_datetime': 'very_special_case',
                           'prefer_title': None,
                           'new_name_template': DEFAULT_NAME,
                           'tags': ['screenshot']},

         # 'photo_default': {'type': 'jpg',
         #                   'name': None,
         #                   'path': None,
         #                   'prefer_datetime': 'datetimeoriginal',
         #                   'new_name_template': DEFAULT_NAME}}
         'document_default': {'type': 'pdf',
                              'name': None,
                              'path': None,
                              'prefer_author': 'PDF:Author',
                              'prefer_datetime': 'CreationDate',
                              'prefer_title': None,
                              'prefer_publisher': 'PDF:EBX_PUBLISHER',
                              'new_name_template': DOCUMENT_NAME,
                              'tags': []},
         'ebook_pdf': {'type': 'pdf',
                       'name': None,
                       'path': None,
                       'prefer_author': 'PDF:Author',
                       'prefer_datetime': 'CreationDate',
                       'prefer_title': 'PDF:Title',
                       'prefer_publisher': 'PDF:EBX_PUBLISHER',
                       'new_name_template': EBOOK_NAME,
                       'tags': []},
         }

# NOTE: New default configuration

NEW_DEFAULT_CONFIG = [
    {
        '_description': 'First Entry in the Default Configuration',
        '_exact_match': False,
        '_weight': None,
        'conditions': {
            'filename': {
                'pathname': None,
                'basename': None,
                'extension': None
            },
            'contents': {
                'mime_type': None
            }
        }
    },
    {
        '_description': 'Second Entry in the Default Configuration',
        '_exact_match': True,
        '_weight': None,
        'conditions': {
            'filename': {
                'pathname': 'whatever_pattern_to_match',
                'basename': None,
                'extension': None
            },
            'contents': {
                'mime_type': 'image/jpeg'
            }
        }
    }
]

NEW_DEFAULT_CONFIG_2 = {
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
         'name_template': '[datetime(%Y-%m-%dT%H%M%S)] [description] -- [tags].[ext]',
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
        {'_description': 'Sample Entry for Photos with strict rules',
         '_exact_match': True,
         '_weight': 1,
         'name_template': '[datetime(%Y-%m-%dT%H%M%S)] [description] -- [tags].[ext]',
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
         }
    ],
    'name_templates': [
        {'_description': 'First name template in the Default Configuration',
         '_name': 'default_template_name',
         'name_format': '%(title)s - %(author)s %(datetime)s.%(extension)s'}
    ]
}

# %(show)s - S%(series_num)02dE%(episode_num)02d - %(title)s.%(extension)s


if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 2 and '--write-default' in sys.argv:
        import os
        from datetime import datetime
        from config import write_yaml_file

        _this_dir = os.path.dirname(os.path.realpath(__file__))
        _basename = 'default_config_{}.yaml'.format(datetime.now().strftime('%Y-%m-%dT%H%M%S'))
        _dest = os.path.join(_this_dir, _basename)

        try:
            write_yaml_file(_dest, NEW_DEFAULT_CONFIG_2)
        except Exception:
            print('Unable to write NEW_DEFAULT_CONFIG_2 to disk')
        else:
            print('Wrote NEW_DEFAULT_CONFIG_2 to file: "{}"'.format(_dest))

