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
from core import (
    util,
    repository,
    exceptions
)


# TODO: [TD0009] Implement a proper plugin interface.
class PluginHandler(object):
    def __init__(self, file_object):
        self.file_object = file_object

        self.request_global_data = repository.SessionRepository.resolve
        self.add_to_global_data = repository.SessionRepository.store

        # Get instantiated and validated plugins.
        self.plugin_classes = plugins.UsablePlugins
        assert(isinstance(self.plugin_classes, list))

    def collect_results(self, label, data):
        """
        Collects plugin results. Passed to plugins as a callback.

        Plugins call this to pass collected data to the session repository.

        Args:
            label: Label that uniquely identifies the data.
            data: The data to add.
        """
        self.add_to_global_data(self.file_object, label, data)

    def _request_data(self, query_string):
        return self.request_global_data(self.file_object, query_string)

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
                try:
                    plugin_instance.run()
                except exceptions.AutonameowPluginError:
                    # log.critical('Plugin instance "{!s}" execution '
                    #              'FAILED'.format(plugin_instance))
                    raise
