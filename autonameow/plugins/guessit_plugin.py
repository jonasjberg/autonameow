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

try:
    import guessit as guessit
except ImportError:
    guessit = None

from core import (
    exceptions,
    types,
    util,
)
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.model import genericfields as gf
from core.namebuilder import fields
from plugins import BasePlugin


class GuessitPlugin(BasePlugin):
    DISPLAY_NAME = 'Guessit'
    MEOWURI_LEAF = DISPLAY_NAME.lower()

    EXTRACTEDDATA_WRAPPER_LOOKUP = {
        'audio_codec': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[],
            generic_field=None
        ),
        'date': ExtractedData(
            coercer=types.AW_TIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'episode': ExtractedData(
            coercer=types.AW_INTEGER,
            mapped_fields=[],
            generic_field=None
        ),
        'format': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[],
            generic_field=None
        ),
        'release_group': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=0.1),
                WeightedMapping(fields.Description, probability=0.001),
            ]
        ),
        'screen_size': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[],
            generic_field=None
        ),
        'season': ExtractedData(
            coercer=types.AW_INTEGER,
            mapped_fields=[],
            generic_field=None
        ),
        'title': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1),
            ]
        ),
        'type': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[],
            generic_field=None
        ),
        'video_codec': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[],
            generic_field=None
        ),
        'year': ExtractedData(
            coercer=types.AW_DATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ]
        ),
    }

    def __init__(self):
        super(GuessitPlugin, self).__init__(self.DISPLAY_NAME)

    def can_handle(self, fileobject):
        _mime_type = self.request_data(
            fileobject, 'extractor.filesystem.xplat.contents.mime_type'
        )
        return util.magic.eval_glob(_mime_type, 'video/*')

    def execute(self, fileobject):
        _file_basename = self.request_data(
            fileobject, 'extractor.filesystem.xplat.basename.full'
        )
        if _file_basename is None:
            raise exceptions.AutonameowPluginError('Required data unavailable')

        data = run_guessit(_file_basename)
        if not data:
            raise exceptions.AutonameowPluginError('Got no data from "guessit"')

        for field, value in data.items():
            _wrapped = self._add_context(field, value)
            if _wrapped:
                self.add_results(fileobject, field, _wrapped)

    def _add_context(self, field, value):
        context = self.EXTRACTEDDATA_WRAPPER_LOOKUP.get(field)
        if not context:
            context = ExtractedData(coercer=None, mapped_fields=None)

        return ExtractedData.from_raw(context, value)

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

    logging.disable(logging.DEBUG)
    try:
        result = guessit.guessit(input_data, guessit_options)
    except (guessit.api.GuessitException, Exception) as e:
        logging.disable(logging.NOTSET)
        raise exceptions.AutonameowPluginError(e)
    else:
        logging.disable(logging.NOTSET)
        return result
