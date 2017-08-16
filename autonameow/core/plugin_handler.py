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
from core import util


# TODO: [TD0009] Implement a proper plugin interface.
class PluginHandler(object):
    def __init__(self, file_object, add_pool_data_callback,
                 request_data_callback):
        self.file_object = file_object

        # Callbacks to the shared "data pool".
        self.request_data = request_data_callback
        self.add_pool_data = add_pool_data_callback

        # Get instantiated and validated plugins.
        self.plugin_classes = plugins.UsablePlugins
        assert(isinstance(self.plugin_classes, list))

    def collect_results(self, label, data):
        """
        Collects plugin results. Passed to plugins as a callback.

        Plugins call this to store collected data.

        If argument "data" is a dictionary, it is "flattened" here.
        Example:

          Incoming arguments:
          LABEL: 'metadata.exiftool'     DATA: {'a': 'b', 'c': 'd'}

          Would be "flattened" to:
          LABEL: 'metadata.exiftool.a'   DATA: 'b'
          LABEL: 'metadata.exiftool.c'   DATA: 'd'

        Args:
            label: Label that uniquely identifies the data.
            data: The data to add.
        """
        assert label is not None and isinstance(label, str)

        if isinstance(data, dict):
            flat_data = util.flatten_dict(data)
            for k, v in flat_data.items():
                merged_label = label + '.' + str(k)
                self.collect_data(merged_label, v)
        else:
            self.collect_data(label, data)

    def collect_data(self, label, data):
        self.add_pool_data(self.file_object, label, data)

    def _request_data(self, query_string):
        return self.request_data(self.file_object, query_string)

    def query(self, query_string):
        if query_string.startswith('plugin.'):
            plugin_name, plugin_query = query_string.lstrip('plugin.').split('.')
            result = plugins.plugin_query(plugin_name, plugin_query, None)
            return result
        else:
            return False

    def start(self):
        for klass in self.plugin_classes:
            plugin_instance = klass(add_results_callback=self.collect_results,
                                    request_data_callback=self._request_data)
            if plugin_instance.can_handle():
                plugin_instance.run()
