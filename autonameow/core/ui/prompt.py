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

import os

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import (
        Completer,
        Completion
    )
    from prompt_toolkit.history import InMemoryHistory, FileHistory
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
from core import config
from core import (
    cache,
    repository,
    util
)
from core.exceptions import InvalidMeowURIError
from core.meowuri import MeowURI
from core.ui import cli


def get_config_history_path():
    _active_config = config.ActiveConfig
    if not _active_config:
        return DEFAULT_HISTORY_FILE_ABSPATH

    try:
        _history_path = _active_config.get(['PERSISTENCE', 'history_directory'])
    except AttributeError:
        _history_path = None

    if _history_path:
        return _history_path
    else:
        return DEFAULT_HISTORY_FILE_ABSPATH


PERSISTANT_HISTORY_BASENAME = util.encode_('prompt_history')
DEFAULT_HISTORY_FILE_ABSPATH = util.normpath(
    os.path.join(
        util.syspath(cache.DEFAULT_CACHE_DIRECTORY_ROOT),
        util.syspath(PERSISTANT_HISTORY_BASENAME)
    )
)
assert DEFAULT_HISTORY_FILE_ABSPATH not in (b'', b'/', None)
assert DEFAULT_HISTORY_FILE_ABSPATH not in (b'', None)


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
        self.all_meowuris = repository.all_meowuris()

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
        for meowuri in self.all_meowuris:
            if meowuri.startswith(string):
                yield meowuri


def meowuri_prompt(message=None):
    history = FileHistory(PERSISTANT_HISTORY_FILE)
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


def ask_confirm(message):
    # TODO: Test this!
    answer = confirm(message + ' ')
    return answer


if __name__ == '__main__':
    response = meowuri_prompt()
    print('Got: {!s}'.format(response))