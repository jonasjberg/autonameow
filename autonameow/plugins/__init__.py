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

import inspect
import os
import logging as log

import sys

from core.exceptions import AutonameowPluginError
from plugins import microsoft_vision


# Plugins are assumed to be located in the same directory as this file.
AUTONAMEOW_PLUGIN_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_PLUGIN_PATH)


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
    # log.critical('Unable to find "microsoft_vision.py" API key!')
    API_KEY = False


def plugin_query(plugin_name, query, data):
    """
    Hack interface to query plugins.
    """
    # TODO: [TD0009] Rewrite from scratch!

    # ** NOTE: This is a "mock" for testing! Returns constants! **
    if plugin_name == 'microsoft_vision':
        if query == 'caption':
            caption = 'a cat lying on a rug'
            log.debug('Returning caption: "{!s}"'.format(caption))
            return str(caption)

        elif query == 'tags':
            tags = ['cat', 'black', 'indoor', 'laying', 'white']
            tags_pretty = ' '.join(map(lambda x: '"' + x + '"', tags))
            log.debug('Returning tags: {}'.format(tags_pretty))
            return tags

    # ** NOTE: Actual query code below! Comment the mock and uncomment this **
    # if plugin_name == 'microsoft_vision':
    #     # NOTE: Expecting "data" to be a valid path to an image file.
    #     if not API_KEY:
    #         raise AutonameowPluginError('Missing "microsoft_vision.py" API key!')
    #
    #     if query == 'caption' or query == 'tags':
    #         response = microsoft_vision.query_api(data, API_KEY)
    #         if not response:
    #             log.error('[plugin.microsoft_vision] Unable to query to API')
    #             raise AutonameowPluginError('Did not receive a valid response')
    #         else:
    #             log.debug('Received microsoft_vision API query response')
    #
    #     if query == 'caption':
    #         caption = microsoft_vision.get_caption_text(response)
    #         log.debug('Returning caption: "{!s}"'.format(caption))
    #         return str(caption)
    #
    #     elif query == 'tags':
    #         tags = microsoft_vision.get_tags(response, 5)
    #         tags_pretty = ' '.join(map(lambda x: '"' + x + '"', tags))
    #         log.debug('Returning tags: {}'.format(tags_pretty))
    #         return tags


class BasePlugin(object):
    def query(self, field=None):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return self.__class__.__name__


def find_plugin_files():
    """
    Finds Python source files assumed to be autonameow plugins.

    Returns: List of the basenames of any found plugin source files.
    """
    found_files = [x for x in os.listdir(AUTONAMEOW_PLUGIN_PATH)
                   if x.endswith('.py') and x != '__init__.py']
    return found_files


plugin_source_files = find_plugin_files()


def get_plugin_classes():
    # Strip extensions.
    _to_import = [f[:-3] for f in plugin_source_files]

    _plugin_classes = []
    for plugin_file in _to_import:
        __import__(plugin_file, None, None)
        namespace = inspect.getmembers(sys.modules[plugin_file],
                                       inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if not issubclass(_obj_type, BasePlugin):
                continue
            elif _obj_type == BasePlugin:
                continue
            else:
                _plugin_classes.append(_obj_type)
                break

        log.debug('Imported plugin source file "{!s}" but no plugins were'
                  ' loaded ..'.format(plugin_file))

    return _plugin_classes


if __name__ == '__main__':
    TEST_IMAGE = '~/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files/smulan.jpg'
    image_path = os.path.realpath(os.path.expanduser(TEST_IMAGE))

    if not os.path.isfile(image_path):
        sys.exit('Not a file: "{}"'.format(image_path))

    response_caption = plugin_query('microsoft_vision', 'caption', image_path)
    response_tags = plugin_query('microsoft_vision', 'tags', image_path)

    print('Microsoft vision API test')
    print('-------------------------')
    print('Using image: "{}"'.format(str(image_path)))
    print('')
    print('Caption: {}'.format(response_caption))
    print('   Tags: {}'.format(response_tags))


# Expected output:
# ================
# (Current working directory is "$SRCROOT/autonameow")
#
#   $ PYTHONPATH=. python3 plugins/__init__.py
#   Microsoft vision API test
#   -------------------------
#   Using image: "/Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files/smulan.jpg"
#
#   Caption: a cat lying on a rug
#      Tags: ['cat', 'black', 'indoor', 'laying', 'white']
