DEFAULT_NAME = '%(date)s_%(time)s %(description)s -- %(tags)s%(ext)s'

match_rules = {'ogv_record_my_desktop': {'mime': 'ogv',
                                         'name': None,
                                         'path': None,
                                         'prefer_datetime': 'Fs_Accessed'}}

match_rename_template = {'ogv_record_my_desktop': DEFAULT_NAME,
                         'photograph': DEFAULT_NAME}
