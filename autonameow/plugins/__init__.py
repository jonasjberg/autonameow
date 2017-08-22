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
import logging
import os
import sys


# Plugins are assumed to be located in the same directory as this file.
AUTONAMEOW_PLUGIN_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_PLUGIN_PATH)

log = logging.getLogger(__name__)


# TODO: [TD0009] Implement a proper plugin interface.
class BasePlugin(object):
    # Resource identifier "MeowURI" for the data returned by this extractor.
    # Example:  'plugin.guessit'
    data_meowuri = None

    def __init__(self, add_results_callback, request_data_callback,
                 display_name=None):
        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.__class__.__name__

        self.add_results = add_results_callback
        self.request_data = request_data_callback

    @classmethod
    def test_init(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def run(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def can_handle(self, file_object):
        """
        Tests if this plugin class can handle the given file object.

        Args:
            file_object: The file to test as an instance of 'FileObject'.

        Returns:
            True if the plugin class can handle the given file, else False.
        """
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


def get_usable_plugin_classes():
    return [k for k in get_plugin_classes() if k.test_init()]


def suitable_plugins_for(file_object):
    """
    Returns plugin classes that can handle the given file object.

    Args:
        file_object: File to get plugins for as an instance of 'FileObject'.

    Returns:
        A list of plugin classes that can handle the given file.
    """
    return [p for p in UsablePlugins if p.can_handle(file_object)]


def map_meowuri_to_plugins():
    """
    Returns a mapping of the plugin classes "meowURIs" and actual classes.

    Each plugin class defines 'data_meowuri' which is used as the
    first part of all data returned by the plugin.

    Returns: A dictionary where the keys are "meowURIs" and the values
        are lists of analyzer classes.
    """
    out = {}

    for klass in UsablePlugins:
        data_meowuri = klass.data_meowuri
        if not data_meowuri:
            continue

        if data_meowuri in out:
            out[data_meowuri].append(klass)
        else:
            out[data_meowuri] = [klass]

    return out


UsablePlugins = get_usable_plugin_classes()
MeowURIClassMap = map_meowuri_to_plugins()
