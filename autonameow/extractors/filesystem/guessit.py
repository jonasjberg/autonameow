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

    def __init__(self):
        super().__init__()

    def extract(self, fileobject, **kwargs):
        file_basename = fileobject.filename
        if not file_basename:
            self.log.debug(
                '{!s} aborting --- file basename is not available'.format(self)
            )
            return None

        guessit_output = run_guessit(file_basename)
        if not guessit_output:
            self.log.debug(
                '{!s} aborting --- got not data from guessit'.format(self)
            )
            return None

        metadata = dict()
        for field, value in guessit_output.items():
            coerced_value = self.coerce_field_value(field, value)
            if coerced_value is not None:
                metadata[field] = coerced_value

        return metadata

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

    import logging
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
