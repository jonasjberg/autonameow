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

try:
    import guessit as guessit
except ImportError:
    guessit = None

from extractors import (
    BaseExtractor,
    ExtractorError
)


class GuessitExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['video/*']
    FIELD_LOOKUP = {
        'audio_codec': {
            'coercer': 'aw_string',
            'mapped_fields': [],
            'generic_field': None
        },
        'date': {
            'coercer': 'aw_timedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': '1'}},
                {'WeightedMapping': {'field': 'Date', 'probability': '1'}},
            ],
            'generic_field': 'date_created'
        },
        'episode': {
            'coercer': 'aw_integer',
            'mapped_fields': [],
            'generic_field': None
        },
        'format': {
            'coercer': 'aw_string',
            'mapped_fields': [],
            'generic_field': None
        },
        'release_group': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'probability': '0.1'}},
                {'WeightedMapping': {'field': 'Description', 'probability': '0.001'}},
            ]
        },
        'screen_size': {
            'coercer': 'aw_string',
            'mapped_fields': [],
            'generic_field': None
        },
        'season': {
            'coercer': 'aw_integer',
            'mapped_fields': [],
            'generic_field': None
        },
        'title': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Title', 'probability': '1'}},
            ]
        },
        'type': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Tags', 'probability': '0.5'}},
            ]
        },
        'video_codec': {
            'coercer': 'aw_string',
            'mapped_fields': [],
            'generic_field': None
        },
        'year': {
            'coercer': 'aw_date',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': '1'}},
                {'WeightedMapping': {'field': 'Date', 'probability': '1'}},
            ]
        },
    }

    def __init__(self):
        super().__init__()

    def extract(self, fileobject, **kwargs):
        file_basename = fileobject.filename
        if not file_basename:
            self.log.debug(
                '{!s} aborting --- file basename is not available'.format(self)
            )
            return

        data = run_guessit(file_basename)
        if not data:
            self.log.debug(
                '{!s} aborting --- got not data from guessit'.format(self)
            )
            return

        _results = dict()
        for field, value in data.items():
            _coerced = self.coerce_field_value(field, value)
            if _coerced is not None:
                _results[field] = _coerced

        return _results

    @classmethod
    def check_dependencies(cls):
        return guessit is not None


def run_guessit(input_data, options=None):
    assert guessit, 'Missing required module "guessit"'

    if options:
        guessit_options = dict(options)
    else:
        guessit_options = {
            'no-embedded-config': True,
            'name_only': True
        }

    logging.disable(logging.DEBUG)
    try:
        result = guessit.guessit(input_data, guessit_options)
    except (guessit.api.GuessitException, Exception) as e:
        logging.disable(logging.NOTSET)
        raise ExtractorError(e)
    else:
        return result
    finally:
        # TODO: Reset logging to state before disabling DEBUG!
        logging.disable(logging.NOTSET)
        return result
