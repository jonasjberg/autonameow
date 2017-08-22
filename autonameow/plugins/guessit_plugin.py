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

from core import (
    exceptions,
    types,
    util
)
from plugins import BasePlugin

try:
    import guessit as guessit
except ImportError:
    guessit = False


class GuessitPlugin(BasePlugin):
    meowuri_root = 'plugin.guessit'

    def __init__(self, add_results_callback, request_data_callback,
                 display_name=None):
        super(GuessitPlugin, self).__init__(
            add_results_callback, request_data_callback, display_name='Guessit'
        )

        self.guessit_results = {}

    @classmethod
    def test_init(cls):
        return guessit is not False

    def run(self):
        if not self.guessit_results:
            # TODO: Pass input data (basename of current file) to guessit ..
            self.guessit_results = self._perform_initial_query()

        if not self.guessit_results:
            raise exceptions.AutonameowPluginError('TODO: ..')
        else:
            self._wrap_and_add_result('date', types.AW_TIMEDATE, 'date')
            self._wrap_and_add_result('title', types.AW_STRING, 'title')
            self._wrap_and_add_result('release_group', types.AW_STRING,
                                      'publisher')
            self._wrap_and_add_result('audio_codec', types.AW_STRING, 'tags')
            self._wrap_and_add_result('video_codec', types.AW_STRING, 'tags')
            self._wrap_and_add_result('format', types.AW_STRING, 'tags')
            self._wrap_and_add_result('screen_size', types.AW_STRING, 'tags')
            self._wrap_and_add_result('type', types.AW_STRING, 'tags')
            self._wrap_and_add_result('episode', types.AW_INTEGER,
                                      'episode_number')
            self._wrap_and_add_result('season', types.AW_INTEGER,
                                      'season_number')

    def _wrap_and_add_result(self, raw_key, wrapper_type, result_key):
        if raw_key in self.guessit_results:
            wrapped = wrapper_type(self.guessit_results[raw_key])
            if wrapped is not None:
                self._add_results(result_key, wrapped)

    def _add_results(self, meowuri_leaf, data):
        if data is None:
            return

        meowuri = '{}.{}'.format(self.meowuri_root, meowuri_leaf)
        #log.debug(
        #    '{!s} passing "{}" to "add_results" callback'.format(self, meowuri)
        #)
        self.add_results(meowuri, data)

    def can_handle(self):
        _mime_type = self.request_data('filesystem.contents.mime_type')
        return util.eval_magic_glob(_mime_type, 'video/*')

    def _perform_initial_query(self):
        _file_basename = self.request_data('filesystem.basename.full')
        if not _file_basename:
            raise exceptions.AutonameowPluginError('Required data unavailable')

        results = run_guessit(_file_basename)
        return results


def run_guessit(input_data, options=None):
    if options:
        guessit_options = options
    else:
        guessit_options = {'no-embedded-config': True, 'name_only': True}

    if guessit:
        try:
            result = guessit.guessit(input_data, guessit_options)
        except guessit.api.GuessitException as e:
            raise exceptions.AutonameowPluginError(e)
        else:
            return result
