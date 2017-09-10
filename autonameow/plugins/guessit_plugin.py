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

from core import (
    exceptions,
    types,
    util,
    fields
)
from extractors import ExtractedData
from plugins import BasePlugin

try:
    import guessit as guessit
except ImportError:
    guessit = None


log = logging.getLogger(__name__)


class GuessitPlugin(BasePlugin):
    meowuri_root = 'plugin.guessit'
    DISPLAY_NAME = 'Guessit'

    tagname_type_lookup = {
        'date': ExtractedData(
            wrapper=types.AW_TIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'title': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.title, probability=1),
            ]
        ),
        'release_group': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.publisher, probability=0.1),
                fields.WeightedMapping(fields.description, probability=0.001),
            ]
        ),
    }

    def __init__(self):
        super(GuessitPlugin, self).__init__(self.DISPLAY_NAME)

    def can_handle(self, file_object):
        _mime_type = self.request_data(file_object,
                                       'filesystem.contents.mime_type')
        return util.eval_magic_glob(_mime_type, 'video/*')

    def execute(self, file_object):
        _file_basename = self.request_data(file_object, 'filesystem.basename.full')
        if _file_basename is None:
            raise exceptions.AutonameowPluginError('Required data unavailable')

        data = run_guessit(_file_basename)
        if not data:
            raise exceptions.AutonameowPluginError('TODO: ..')

        def _to_internal_format(raw_data):
            for tag_name, value in raw_data.items():
                if tag_name in self.tagname_type_lookup:
                    # Found a "template" 'Item' class.
                    wrapper = self.tagname_type_lookup[tag_name]
                else:
                    # Use a default 'Item' class.
                    wrapper = ExtractedData(wrapper=None, mapped_fields=None)

                item = wrapper(value)
                if item:
                    self._add_results(file_object, tag_name, item)

        def _wrap_and_add_result(raw_data, raw_key, wrapper_type, result_key):
            raw_value = raw_data.get(raw_key)
            if not raw_value:
                return

            try:
                wrapped = wrapper_type(raw_value)
            except types.AWTypeError as e:
                pass
            else:
                if wrapped is not None:
                    self._add_results(file_object, result_key, wrapped)

        # self._wrap_and_add_result('date', types.AW_TIMEDATE, 'date')
        # self._wrap_and_add_result('title', types.AW_STRING, 'title')
        # self._wrap_and_add_result('release_group', types.AW_STRING, 'publisher')
        _to_internal_format(data)

        _wrap_and_add_result(data, 'audio_codec', types.AW_STRING, 'tags')
        _wrap_and_add_result(data, 'video_codec', types.AW_STRING, 'tags')
        _wrap_and_add_result(data, 'format', types.AW_STRING, 'tags')
        _wrap_and_add_result(data, 'screen_size', types.AW_STRING, 'tags')
        _wrap_and_add_result(data, 'type', types.AW_STRING, 'tags')
        _wrap_and_add_result(data, 'episode', types.AW_INTEGER, 'episode_number')
        _wrap_and_add_result(data, 'season', types.AW_INTEGER, 'season_number')
        _wrap_and_add_result(
            data,
            'year',
            ExtractedData(
                wrapper=types.AW_DATE,
                mapped_fields=[
                    fields.WeightedMapping(fields.datetime, probability=1),
                    fields.WeightedMapping(fields.date, probability=1)
                ]),
            'date'
        )

    def _add_results(self, file_object, meowuri_leaf, data):
        if data is None:
            return

        meowuri = '{}.{}'.format(self.meowuri_root, meowuri_leaf)
        #log.debug(
        #    '{!s} passing "{}" to "add_results" callback'.format(self, meowuri)
        #)
        self.add_results(file_object, meowuri, data)

    @classmethod
    def test_init(cls):
        return guessit is not None


def run_guessit(input_data, options=None):
    if not guessit:
        return

    if options:
        guessit_options = options
    else:
        guessit_options = {'no-embedded-config': True, 'name_only': True}

    try:
        result = guessit.guessit(input_data, guessit_options)
    except (guessit.api.GuessitException, Exception) as e:
        raise exceptions.AutonameowPluginError(e)
    else:
        return result
