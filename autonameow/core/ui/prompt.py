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
except ImportError:
    raise SystemExit(
        'Missing required module "prompt_toolkit". '
        'Make sure "prompt_toolkit" is available before running this program.'
    )


from core import constants as C
from core import (
    cache,
    repository,
    util
)
from core.ui import cli


PERSISTANT_HISTORY_BASENAME = b'prompt_history'
PERSISTANT_HISTORY_FILE = os.path.join(
    util.syspath(cache.CACHE_DIR_ABSPATH),
    util.syspath(PERSISTANT_HISTORY_BASENAME)
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
    # TODO: [TD0099] Use actual data for autosuggest/autocomplete ..
    # history = InMemoryHistory()
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

    text = prompt('Enter MeowURI: ', history=history,
                  auto_suggest=AutoSuggestFromHistory(),
                  completer=meowuri_completer,
                  enable_history_search=True,
                  on_abort=AbortAction.RETRY)
    return text


def ask_confirm(message=None):
    # TODO: Test this!
    if message is None:
        msg = 'Please Confirm (unspecified action)? [y/n]'
    else:
        msg = message

    answer = confirm(msg + ' ')
    return answer


if __name__ == '__main__':
    response = meowuri_prompt()
    print('Got: {!s}'.format(response))
