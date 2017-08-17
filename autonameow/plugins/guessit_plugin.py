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
    data_query_string = 'plugin.guessit'

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

        if 'date' in self.guessit_results:
            wrapped_date = types.AW_TIMEDATE(self.guessit_results['date'])
            if wrapped_date:
                print('Wrapped guessit_results[date]: {}'.format(wrapped_date))
                self.add_results('plugin.guessit.datetime', wrapped_date)

        if 'title' in self.guessit_results:
            wrapped_title = types.AW_STRING(self.guessit_results['title'])
            if wrapped_title:
                print('Wrapped guessit_results[title]: {}'.format(wrapped_title))
                self.add_results('plugin.guessit.title', wrapped_title)

    def can_handle(self):
        _mime_type = self.request_data('contents.mime_type')
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
        result = guessit.guessit(input_data, guessit_options)
        return result
    return None

