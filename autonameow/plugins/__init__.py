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

import os
import logging as log

from core.exceptions import AutonameowPluginError
from plugins import microsoft_vision


# 'microsoft_vision.py'
# =====================
# Queries the Microsoft Vision API with images for information about visual
# content found in the image.
#
# Requires a Microsoft Visual API key, available for free at:
#   <https://www.microsoft.com/cognitive-services/en-us/sign-up>
#
# Add your API key to the file 'microsoft_vision.key' in this directory,
# or modify the line below to point to the file containing your API key.
#
api_key_path = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                            'microsoft_vision.key')
try:
    with open(api_key_path, mode='r', encoding='utf8') as f:
        API_KEY = f.read()
        API_KEY = API_KEY.strip()
except FileNotFoundError as e:
    log.critical('Unable to find "microsoft_vision.py" API key!')
    API_KEY = False


def plugin_query(plugin_name, query, data):
    """
    Hack interface to query plugins.
    """
    # TODO: Rewrite from scratch!

    if plugin_name == 'microsoft_vision':
        # NOTE: Expecting "data" to be a valid path to an image file.
        if not API_KEY:
            raise AutonameowPluginError('Missing "microsoft_vision.py" API key!')

        if query == 'caption' or query == 'tags':
            response = microsoft_vision.query_api(data, API_KEY)
            if not response:
                log.error('[plugin.microsoft_vision] Unable to query to API')
                raise AutonameowPluginError('Did not receive a valid response')
            else:
                log.debug('Received microsoft_vision API query response')

        if query == 'caption':
            caption = microsoft_vision.get_caption_text(response)
            log.debug('Returning caption: "{!s}"'.format(caption))
            return str(caption)

        elif query == 'tags':
            tags = microsoft_vision.get_tags(response, 5)
            tags_pretty = ' '.join(map(lambda x: '"' + x + '"', tags))
            log.debug('Returning tags: {}'.format(tags_pretty))
            return tags

