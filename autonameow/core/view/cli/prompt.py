# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
import sys

from core import constants as C
from core import event
from core import master_provider
from core.exceptions import DependencyError
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.view import cli
from util import disk
from util import encoding as enc

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import Completer
    from prompt_toolkit.completion import Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.shortcuts import confirm
    from prompt_toolkit.validation import ValidationError
    from prompt_toolkit.validation import Validator
except ImportError:
    raise DependencyError(missing_modules='prompt_toolkit')


log = logging.getLogger(__name__)


class ConfigHistoryPathStore(object):
    def __init__(self):
        self._config_history_path = None
        self.default_history_filepath = C.DEFAULT_HISTORY_FILE_ABSPATH

    def update_from_config(self, active_config):
        if not active_config:
            return

        history_filepath = active_config.get(['PERSISTENCE', 'history_file_path'])
        if not history_filepath:
            return

        if disk.isfile(history_filepath):
            self._config_history_path = history_filepath
        elif disk.isdir(history_filepath):
            log.warning('Expected history path to include a file ..')
            fixed_history_filepath = disk.joinpaths(
                history_filepath, C.DEFAULT_HISTORY_FILE_BASENAME
            )
            if fixed_history_filepath:
                log.warning('Added default filename to history path "%s"',
                            enc.displayable_path(fixed_history_filepath))
                self._config_history_path = fixed_history_filepath

    @property
    def config_history_path(self):
        if not self._config_history_path:
            log.debug('Using default history file path "%s"',
                      enc.displayable_path(self.default_history_filepath))
            return self.default_history_filepath

        log.debug('Using history file path "%s"',
                  enc.displayable_path(self._config_history_path))
        return self._config_history_path


_config_history_path_store = ConfigHistoryPathStore()


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
        # TODO: [TD0185] Rework access to 'master_provider' functionality.
        self.all_meowuris = list(master_provider.Registry.mapped_meowuris)

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

    history_filepath = _config_history_path_store.config_history_path
    if history_filepath:
        history = FileHistory(history_filepath)
        log.debug('Prompt history file: "%s"',
                  enc.displayable_path(history_filepath))
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

    try:
        response = prompt(
            'Enter MeowURI: ',
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            completer=meowuri_completer,
            enable_history_search=True,
            validator=MeowURIValidator()
        )
        return response
    except (EOFError, KeyboardInterrupt):
        return None


def field_selection_prompt(candidates):
    if not sys.__stdin__.isatty():
        # TODO: [TD0111] Separate abstract user interaction from CLI specifics.
        log.critical('Standard input is not a TTY --- would have triggered an '
                     'AssertionError in "prompt_toolkit". ABORTING!')
        return None

    _candidate_numbers = list(candidates.keys())
    try:
        response = prompt(
            'Enter #: ',
            validator=NumberSelectionValidator(candidates=_candidate_numbers)
        )
        return response
    except (EOFError, KeyboardInterrupt):
        return None


def ask_confirm(message):
    if not sys.__stdin__.isatty():
        # TODO: [TD0111] Separate abstract user interaction from CLI specifics.
        log.critical('Standard input is not a TTY --- would have triggered an '
                     'AssertionError in "prompt_toolkit". ABORTING!')
        return False

    assert isinstance(message, str)

    # TODO: Test this!
    answer = confirm(message + ' ')
    return answer


def _on_config_changed(*_, **kwargs):
    """
    Called whenever the global configuration changes.
    """
    active_config = kwargs.get('config')
    assert active_config

    _config_history_path_store.update_from_config(active_config)


event.dispatcher.on_config_changed.add(_on_config_changed)


if __name__ == '__main__':
    response = meowuri_prompt()
    print('Got: {!s}'.format(response))
