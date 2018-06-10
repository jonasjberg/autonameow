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

from extractors import ExtractorError
from extractors.metadata.base import BaseMetadataExtractor


class GuessitExtractor(BaseMetadataExtractor):
    HANDLES_MIME_TYPES = ['video/*']

    def __init__(self):
        super().__init__()

        self._guessit_module = None
        self._initialize_guessit_module()

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.filename)

    def shutdown(self):
        self._guessit_module = None
        reset_lazily_imported_guessit_module()

    def _initialize_guessit_module(self):
        self._guessit_module = get_lazily_imported_guessit_module()

    def _get_metadata(self, file_basename):
        if not file_basename:
            self.log.debug(
                '{!s} aborting --- file basename is not available'.format(self)
            )
            return None

        guessit_output = run_guessit(file_basename, self._guessit_module)
        if not guessit_output:
            self.log.debug(
                '{!s} aborting --- got not data from guessit'.format(self)
            )
            return None

        metadata = self._to_internal_format(guessit_output)
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        return metadata

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for field, value in raw_metadata.items():
            coerced = self.coerce_field_value(field, value)
            if coerced is not None:
                coerced_metadata[field] = coerced

        return coerced_metadata

    @classmethod
    def dependencies_satisfied(cls):
        _guessit = get_lazily_imported_guessit_module()
        return _guessit is not None


_GUESSIT_MODULE = None


def get_lazily_imported_guessit_module():
    global _GUESSIT_MODULE
    if _GUESSIT_MODULE is None:
        try:
            import guessit as _guessit
        except ImportError:
            _guessit = None

        _GUESSIT_MODULE = _guessit
    return _GUESSIT_MODULE


def reset_lazily_imported_guessit_module():
    global _GUESSIT_MODULE
    _GUESSIT_MODULE = None


def run_guessit(input_data, guessit_module, options=None):
    assert guessit_module
    assert hasattr(guessit_module, 'guessit')
    assert hasattr(guessit_module, 'api')
    assert callable(getattr(guessit_module, 'guessit'))

    if options:
        guessit_options = dict(options)
    else:
        guessit_options = {
            'no-embedded-config': True,
            'name_only': True
        }

    import logging
    logging.disable(logging.DEBUG)
    try:
        result = guessit_module.guessit(input_data, guessit_options)
    except (guessit_module.api.GuessitException, Exception) as e:
        logging.disable(logging.NOTSET)
        raise ExtractorError(e)
    else:
        return result
    finally:
        # TODO: Reset logging to state before disabling DEBUG!
        logging.disable(logging.NOTSET)
