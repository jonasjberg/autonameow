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
import os
import sys

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import (
        Completer,
        Completion
    )
    from prompt_toolkit.history import (
        FileHistory,
        InMemoryHistory
    )
    from prompt_toolkit.interface import AbortAction
    from prompt_toolkit.shortcuts import confirm
    from prompt_toolkit.validation import (
        Validator,
        ValidationError
    )
except ImportError:
    raise SystemExit(
        'Missing required module "prompt_toolkit". '
        'Make sure "prompt_toolkit" is available before running this program.'
    )

from core import constants as C
from core import (
    config,
    providers,
)
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.view import cli
from util import encoding as enc
from util import (
    disk,
    sanity
)


log = logging.getLogger(__name__)


def get_config_history_path():
    _active_config = config.ActiveConfig
    if not _active_config:
        return C.DEFAULT_HISTORY_FILE_ABSPATH

    try:
        _history_path = _active_config.get(['PERSISTENCE', 'history_file_path'])
    except AttributeError:
        _history_path = None

    if _history_path:
        if disk.isfile(_history_path):
            return _history_path
        elif disk.isdir(_history_path):
            log.warning('Expected history path to include a file ..')
            _fixed_path = os.path.join(
                enc.syspath(_history_path),
                enc.syspath(C.DEFAULT_HISTORY_FILE_BASENAME)
            )
            if _fixed_path:
                log.warning('Using fixed history path: "{!s}"'.format(
                    enc.displayable_path(_fixed_path)
                ))
                return _fixed_path

    return C.DEFAULT_HISTORY_FILE_ABSPATH


class NumberSelectionValidator(Validator):
    def __init__(self, candidates=None):
        super(NumberSelectionValidator, self).__init__()
        self.candidates = candidates

    def validate(self, document):
        _text = document.text
        if _text not in self.candidates:
            _valid = ', '.join(c for c in self.candidates)
            raise ValidationError(
                message='Enter one of; {!s}'.format(_valid),
                cursor_position=len(_text)  # Move cursor to end of input.
            )


class MeowURIValidator(Validator):
    def validate(self, document):
        _text = document.text
        try:
            MeowURI(_text)
        except InvalidMeowURIError as e:
            raise ValidationError(
                message=str(e),
                cursor_position=len(_text)  # Move cursor to end of input.
            )


class MeowURICompleter(Completer):
    def __init__(self):
        self.all_meowuris = list(providers.Registry.mapped_meowuris)

    # TODO: [TD0099] Split by MeowURI separators.
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text:
            for suggestion in C.MEOWURI_ROOTS:
                yield Completion(suggestion, start_position=0)

        if text:
            for match in self._match_start(text):
                yield Completion(match, start_position=-len(text))

    def _match_start(self, string):
        for uri in self.all_meowuris:
            if uri.startswith(string):
                yield uri


def meowuri_prompt(message=None):
    if not sys.__stdin__.isatty():
        # TODO: [TD0111] Separate abstract user interaction from CLI specifics.
        log.critical('Standard input is not a TTY --- would have triggered an '
                     'AssertionError in "prompt_toolkit". ABORTING!')
        return None

    _history_file_path = get_config_history_path()
    if _history_file_path:
        history = FileHistory(_history_file_path)
        log.debug('Prompt history file: "{!s}"'.format(
            enc.displayable_path(_history_file_path)
        ))
    else:
        log.debug('Prompt history file: in-memory (volatile)')
        history = InMemoryHistory()

    meowuri_completer = MeowURICompleter()

    cli.msg('\n', ignore_quiet=True)
    if message is not None:
        cli.msg(message, style='info', ignore_quiet=True)

    cli.msg(
        'Use <TAB> to autocomplete and <RIGHT ARROW> for history completion.',
        style='info', ignore_quiet=True
    )
    cli.msg('\n', ignore_quiet=True)

    text = prompt(
        'Enter MeowURI: ',
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        completer=meowuri_completer,
        enable_history_search=True,
        on_abort=AbortAction.RETURN_NONE,
        validator=MeowURIValidator()
    )
    return text


def field_selection_prompt(candidates):
    if not sys.__stdin__.isatty():
        # TODO: [TD0111] Separate abstract user interaction from CLI specifics.
        log.critical('Standard input is not a TTY --- would have triggered an '
                     'AssertionError in "prompt_toolkit". ABORTING!')
        return None

    _candidate_numbers = list(candidates.keys())
    text = prompt(
        'Enter #: ',
        on_abort=AbortAction.RETURN_NONE,
        validator=NumberSelectionValidator(candidates=_candidate_numbers)
    )
    return text


def ask_confirm(message):
    if not sys.__stdin__.isatty():
        # TODO: [TD0111] Separate abstract user interaction from CLI specifics.
        log.critical('Standard input is not a TTY --- would have triggered an '
                     'AssertionError in "prompt_toolkit". ABORTING!')
        return False

    sanity.check_internal_string(message)

    # TODO: Test this!
    answer = confirm(message + ' ')
    return answer


if __name__ == '__main__':
    response = meowuri_prompt()
    print('Got: {!s}'.format(response))
