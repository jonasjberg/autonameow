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

from plugins import BasePlugin

try:
    import guessit as guessit
except ImportError:
    guessit = False


class GuessitPlugin(BasePlugin):
    def __init__(self):
        super(GuessitPlugin, self).__init__(display_name='Guessit')

        self.guessit_results = {}

    def test_init(self):
        return guessit is not False

    def query(self, field=None):
        if not self.guessit_results:
            # TODO: Pass input data (basename of current file) to guessit ..
            # self.guessit_results = run_guessit(file_object.filenamepart_base)
            pass

    # def _get_datetime(self):
    #     result = []
    #     if self.guessit_results:
    #         guessit_timestamps = self._get_datetime_from_guessit_results()
    #         if guessit_timestamps:
    #             result += guessit_timestamps
    #
    # def _run(self):
    #     if guessit and self.file_object.mime_type == 'mp4':
    #         self.guessit_results = self._get_metadata_from_guessit()
    #
    #         if self.guessit_results:
    #             self.add_results('plugins.guessit', self.guessit_results)
    #
    # def _get_datetime_from_guessit_results(self):
    #     """
    #     Get date/time-information from the results returned by "guessit".
    #     :return: a list of dictionaries (actually just one) on the form:
    #              [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
    #                  'source' : "Create date",
    #                  'weight'  : 1
    #                }, .. ]
    #     """
    #     if self.guessit_results:
    #         if 'date' in self.guessit_results:
    #             return [{'value': self.guessit_results['date'],
    #                      'source': 'guessit',
    #                      'weight': 0.75}]
    #
    # def _get_title_from_guessit_results(self):
    #     """
    #     Get the title from the results returned by "guessit".
    #     :return: a list of dictionaries (actually just one) on the form:
    #              [ { 'title': "The Cats Meouw,
    #                  'source' : "guessit",
    #                  'weight'  : 0.75
    #                }, .. ]
    #     """
    #     if self.guessit_results:
    #         if 'title' in self.guessit_results:
    #             return [{'value': self.guessit_results['title'],
    #                      'source': 'guessit',
    #                      'weight': 0.75}]


def run_guessit(input_data, options=None):
    if options:
        guessit_options = options
    else:
        guessit_options = ['no-embedded-config', 'name_only']

    if guessit:
        result = guessit.guessit(input_data, guessit_options)
        return result
    return None

