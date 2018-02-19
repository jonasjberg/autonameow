# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

from core import (
    logs,
    provider,
    repository
)
from core.exceptions import (
    AutonameowException,
    AutonameowPluginError,
)
from core.model import force_meowuri
from core.model.genericfields import get_field_class
from util import sanity


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
        import plugins
        self.available_plugins = plugins.ProviderClasses
        sanity.check_isinstance(self.available_plugins, list)

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
            sanity.check_isinstance(require_plugins, list)
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
                with logs.log_runtime(log, str(plugin)):
                    data = plugin(fileobject)
            except AutonameowPluginError:
                log.critical('Plugin instance "{!s}" execution '
                             'FAILED'.format(plugin))
                continue

            # TODO: [TD0108] Fix inconsistencies in results passed back by plugins.
            if not data:
                continue

            _results = _wrap_extracted_data(data, _metainfo, plugin)
            _meowuri_prefix = plugin.meowuri_prefix()
            store_results(fileobject, _meowuri_prefix, _results)


def request_global_data(fileobject, uri_string):
    # NOTE(jonas): String to MeowURI conversion boundary.
    sanity.check_internal_string(uri_string)

    uri = force_meowuri(uri_string)
    if not uri:
        log.error('Bad MeowURI in plugin request: "{!s}"'.format(uri_string))
        return None

    # Pass a "tie-breaker" to resolve cases where we only want one item?
    # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
    response = provider.query(fileobject, uri)
    if response:
        return response.value
    return None


def store_results(fileobject, meowuri_prefix, data):
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
        uri = force_meowuri(meowuri_prefix, _uri_leaf)
        if not uri:
            log.error('Unable to construct full plugin result MeowURI'
                      'from prefix "{!s}" and leaf "{!s}"'.format(
                          meowuri_prefix, _uri_leaf))
            continue

        repository.SessionRepository.store(fileobject, uri, _data)


def _wrap_extracted_data(extracteddata, metainfo, source_klass):
    out = dict()

    for field, value in extracteddata.items():
        field_metainfo = dict(metainfo.get(field, {}))
        if not field_metainfo:
            log.warning('Missing metainfo for field "{!s}"'.format(field))

        field_metainfo['value'] = value
        # Do not store a reference to the class itself before actually needed..
        field_metainfo['source'] = str(source_klass)

        # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
        # Map strings to generic field classes.
        _generic_field_string = field_metainfo.get('generic_field')
        if _generic_field_string:
            _generic_field_klass = get_field_class(_generic_field_string)
            if _generic_field_klass:
                field_metainfo['generic_field'] = _generic_field_klass
            else:
                field_metainfo.pop('generic_field')

        out[field] = field_metainfo

    return out


def run_plugins(fileobject, require_plugins=None, run_all_plugins=False):
    """
    Instantiates, executes and returns a 'PluginHandler' instance.

    Args:
        fileobject: The current file object to pass to plugins.
        require_plugins: List of plugin classes that should be included.
        run_all_plugins: Whether all plugins should be included.

    Returns:
        An instance of the 'PluginHandler' class that has executed successfully.

    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    plugin_handler = PluginHandler()
    try:
        plugin_handler.start(fileobject,
                             require_plugins=require_plugins,
                             run_all_plugins=run_all_plugins is True)
    except AutonameowPluginError as e:
        # TODO: [TD0164] Tidy up throwing/catching of exceptions.
        log.critical('Plugins FAILED: {!s}'.format(e))
        raise AutonameowException(e)
