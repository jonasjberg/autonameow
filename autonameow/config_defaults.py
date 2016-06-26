# Default match rename template:
DEFAULT_NAME = '%(date)s_%(time)s %(description)s -- %(tags)s%(ext)s'

# Matching rules:
rules = {'record_my_desktop': {'type': 'ogv',
                               'name': None,
                               'path': None,
                               'prefer_datetime': 'accessed',
                               'use_rename_template': DEFAULT_NAME},
         'photo_default': {'type': 'jpg',
                           'name': None,
                           'path': None,
                           'prefer_datetime': 'datetimeoriginal',
                           'new_name_template': DEFAULT_NAME},
         'photo_oneplusx': {'type': 'jpg',
                            'name': '^IMG_\d{8}_\d{6}\.jpg$',
                            'path': None,
                            'prefer_datetime': 'very_special_case',
                            'new_name_template': DEFAULT_NAME}}
