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
import sys
# import logging as log


# Plugins are assumed to be located in the same directory as this file.
AUTONAMEOW_PLUGIN_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_PLUGIN_PATH)


def plugin_query(plugin_name, query, data):
    """
    Hack interface to query plugins.
    """
    # TODO: [TD0009] Rewrite from scratch!
    if plugin_name == 'microsoft_vision':
        # NOTE: Expecting "data" to be a valid path to an image file.

        # TODO: [TD0061] Fetch an instance of the requested plugin.

        # TODO: [TD0061] Query the plugin instance.

        # TODO: [TD0061] Return any query response data.
        pass

        # if query == 'caption':
        #     caption = 'a cat lying on a rug'
        #     # log.debug('Returning caption: "{!s}"'.format(caption))
        #     return str(caption)
        # elif query == 'tags':
        #     tags = ['cat', 'black', 'indoor', 'laying', 'white']
        #     tags_pretty = ' '.join(map(lambda x: '"' + x + '"', tags))
        #     # log.debug('Returning tags: {}'.format(tags_pretty))
        #     return tags


class BasePlugin(object):
    def __init__(self, display_name=None):
        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.__class__.__name__

    def test_init(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def query(self, field=None):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return self.display_name


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

        # log.debug('Imported plugin source file "{!s}" but no plugins were'
        #           ' loaded ..'.format(plugin_file))

    return _plugin_classes


def _plugin_class_instance_dict():
    out = {}

    klasses = get_plugin_classes()
    for klass in klasses:
        plugin_class_instance = klass()
        if plugin_class_instance.test_init():
            # Make sure that plugin-specific prerequisites/dependencies are met.
            key = str(plugin_class_instance)
            out[key] = plugin_class_instance

    return out


Plugins = _plugin_class_instance_dict()
