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
    logs,
    repository
)
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI


log = logging.getLogger(__name__)


# TODO: [TD0009] Implement a proper plugin interface.
class PluginHandler(object):
    def __init__(self):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )
        self._plugins_to_use = []
        self.available_plugins = []

    def start(self, fileobject, require_plugins=None, run_all_plugins=False):
        self.log.debug(' Plugin Handler Started '.center(120, '='))

        # Get instantiated and validated plugins.
        self.available_plugins = plugins.UsablePlugins
        assert isinstance(self.available_plugins, list)

        if self.available_plugins:
            _p = ' '.join(
                map(lambda x: '"' + str(x) + '"', self.available_plugins)
            )
            self.log.debug('Available plugins: {!s}'.format(_p))
        else:
            self.log.debug('No plugins are available')

        if run_all_plugins:
            self.use_all_plugins()
        elif require_plugins:
            assert isinstance(require_plugins, list), (
                'Expected "require_plugins" to be a list. Got {!s}'.format(
                    type(require_plugins))
            )
            self.use_plugins(list(require_plugins))

        with logs.log_runtime(log, 'Plugins'):
            self.execute_plugins(fileobject)

    def use_plugins(self, plugin_list):
        self.log.debug(
            'Required {} plugins: {!s}'.format(len(plugin_list), plugin_list)
        )

        for plugin in plugin_list:
            if plugin in self.available_plugins:
                self._plugins_to_use.append(plugin)
                self.log.debug('Using plugin: "{!s}"'.format(plugin))
            else:
                self.log.debug(
                    'Requested unavailable plugin: "{!s}"'.format(plugin)
                )

    def use_all_plugins(self):
        self.log.debug(
            'Using all {} plugins'.format(len(self.available_plugins))
        )
        self._plugins_to_use = [p for p in self.available_plugins]

    def execute_plugins(self, fileobject):
        self.log.debug('Running {} plugins'.format(len(self._plugins_to_use)))
        for plugin_klass in self._plugins_to_use:
            plugin = plugin_klass()

            if not plugin.can_handle(fileobject):
                self.log.debug(
                    '"{!s}" plugin can not handle file "{!s}"'.format(
                        plugin, fileobject)
                )
                continue

            self.log.debug(
                '"{!s}" plugin CAN handle file "{!s}"'.format(
                    plugin, fileobject)
            )
            self.log.debug('Executing plugin: "{!s}" ..'.format(plugin))

            try:
                _metainfo = plugin.metainfo()
            except (AttributeError, NotImplementedError) as e:
                log.error('Failed to get meta info! Halted plugin "{!s}":'
                          ' {!s}'.format(plugin, e))
                continue
            try:
                data = plugin(fileobject)
            except exceptions.AutonameowPluginError:
                log.critical('Plugin instance "{!s}" execution '
                             'FAILED'.format(plugin))
                continue

            # TODO: [TD0108] Fix inconsistencies in results passed back by plugins.
            if not data:
                continue

            _results = _wrap_extracted_data(data, _metainfo, plugin)
            _meowuri_prefix = plugin.meowuri_prefix()
            collect_results(fileobject, _meowuri_prefix, _results)


def request_data(fileobject, meowuri):
    response = repository.SessionRepository.query(fileobject, meowuri)
    return response.get('value')


def collect_results(fileobject, meowuri_prefix, data):
    """
    Collects plugin results. Passed to plugins as a callback.

    Plugins call this to pass collected data to the session repository.

    Args:
        fileobject: File that produced the data to add.
        meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
        data: The data to add.
    """
    # TODO: [TD0108] Fix inconsistencies in results passed back by plugins.
    for _uri_leaf, _data in data.items():
        try:
            _meowuri = MeowURI(meowuri_prefix, _uri_leaf)
        except InvalidMeowURIError as e:
            log.critical(
                'Got invalid MeowURI from plugin -- !{!s}"'.format(e)
            )
            continue
        repository.SessionRepository.store(fileobject, _meowuri, _data)


def _wrap_extracted_data(extracteddata, metainfo, source_klass):
    out = {}

    for field, value in extracteddata.items():
        field_metainfo = dict(metainfo.get(field, {}))
        if not field_metainfo:
            log.warning('Missing metainfo for field "{!s}"'.format(field))

        field_metainfo['value'] = value
        # Do not store a reference to the class itself before actually needed..
        field_metainfo['source'] = str(source_klass)
        out[field] = field_metainfo

    return out
