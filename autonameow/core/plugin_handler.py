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

import logging

import plugins
from core import (
    exceptions,
    repository
)
from core.util import sanity
from core.model import ExtractedData


# TODO: [TD0009] Implement a proper plugin interface.


class PluginHandler(object):
    def __init__(self):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        # Get instantiated and validated plugins.
        self.available_plugins = plugins.UsablePlugins
        sanity.check_isinstance(self.available_plugins, list)

        _p = ' '.join(map(lambda x: '"' + str(x) + '"', self.available_plugins))
        self.log.debug('Available plugins: {!s}'.format(_p))

        self._plugins_to_use = []

    def use_plugins(self, plugin_list):
        for plugin in plugin_list:
            if plugin in self.available_plugins:
                self._plugins_to_use.append(plugin)
                self.log.debug('Using plugin: "{!s}"'.format(plugin))
            else:
                self.log.debug(
                    'Requested unavailable plugin: "{!s}"'.format(plugin)
                )

    def execute_plugins(self, fileobject):
        self.log.debug('Executing plugins ..')

        for plugin_klass in self._plugins_to_use:
            plugin = plugin_klass()

            if plugin.can_handle(fileobject):
                self.log.debug(
                    '"{!s}" plugin CAN handle file "{!s}"'.format(
                        plugin, fileobject)
                )
                self.log.debug('Executing plugin: "{!s}" ..'.format(plugin))
                try:
                    plugin(fileobject)
                except exceptions.AutonameowPluginError:
                    # log.critical('Plugin instance "{!s}" execution '
                    #              'FAILED'.format(plugin_instance))
                    raise
            else:
                self.log.debug(
                    '"{!s}" plugin can not handle file "{!s}"'.format(
                        plugin, fileobject)
                )


def request_data(fileobject, meowuri):
    response = repository.SessionRepository.query(fileobject, meowuri)
    if response is None:
        return None
    else:
        if isinstance(response, ExtractedData):
            return response.value
        else:
            return response


def collect_results(fileobject, label, data):
    """
    Collects plugin results. Passed to plugins as a callback.

    Plugins call this to pass collected data to the session repository.

    Args:
        fileobject: File that produced the data to add.
        label: Label that uniquely identifies the data.
        data: The data to add.
    """
    repository.SessionRepository.store(fileobject, label, data)
