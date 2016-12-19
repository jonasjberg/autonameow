# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.
# -*- coding: utf-8 -*-

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
                               'filename_in_filetags_format': False,
                               'tags': []},
         'photo_oneplusx': {'type': 'jpg',
                            'name': r'^IMG_\d{8}_\d{6}\.jpg$',
                            'path': None,
                            'prefer_datetime': 'very_special_case',
                            'prefer_title': None,
                            'new_name_template': DEFAULT_NAME,
                            'filename_in_filetags_format': False,
                            'tags': []},
         'photo_android_msg': {'type': 'jpg',
                               'name': r'^received_\d{15,17}\.jpeg$',
                               'path': None,
                               'prefer_datetime': 'android_messenger',
                               'prefer_title': None,
                               'new_name_template': DEFAULT_NAME,
                               'filename_in_filetags_format': False,
                               'tags': []},
         'screencapture': {'type': 'png',
                           'name': r'^screencapture.*.png$',
                           'path': None,
                           'prefer_datetime': 'screencapture_unixtime',
                           'prefer_title': None,
                           'new_name_template': DEFAULT_NAME,
                           'filename_in_filetags_format': False,
                           'tags': ['screenshot']},
         'filetagsscreenshot': {'type': 'png',
                                'name': None,
                                'path': None,
                                'prefer_datetime': 'very_special_case',
                                'prefer_title': None,
                                'new_name_template': DEFAULT_NAME,
                                'filename_in_filetags_format': True,
                                'tags': ['screenshot']},
         'filetagsphoto': {'type': 'jpg',
                           'name': None,
                           'path': None,
                           'prefer_datetime': 'very_special_case',
                           'prefer_title': None,
                           'new_name_template': DEFAULT_NAME,
                           'filename_in_filetags_format': True,
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
