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

import plugins
from core.container import DataContainerBase


class PluginResults(DataContainerBase):
    def __init__(self):
        super(PluginResults, self).__init__()

    def get(self, query_string=None):
        if not query_string:
            return self._data

        if query_string.startswith('plugin.'):
            plugin_name, plugin_query = query_string.lstrip('plugin.').split('.')
            result = plugins.plugin_query(plugin_name, plugin_query, None)
            return result
        else:
            return False

    def add(self, destination, data):
        if not destination:
            raise KeyError('Expected non-empty "destination"')

        self._data.update({destination: data})


class PluginHandler(object):
    def __init__(self, extracted_data, active_config):
        self.extracted_data = extracted_data
        self.config = active_config

        self.plugins = plugins.Plugins
        assert(isinstance(self.plugins, dict))

        self.results = PluginResults()

    def query(self, query_string):
        if query_string.startswith('plugin.'):
            plugin_name, plugin_query = query_string.lstrip('plugin.').split('.')
            result = plugins.plugin_query(plugin_name, plugin_query, None)
            return result
        else:
            return False
