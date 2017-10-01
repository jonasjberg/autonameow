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

from prompt_toolkit import prompt
from prompt_toolkit.completion import (
    Completer,
    Completion
)
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.interface import AbortAction
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from core import constants as C
from core import repository


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
    history = InMemoryHistory()
    history.append('extractor.filesystem.xplat.basename.full')
    history.append('analyzer.filetags.tags')
    history.append('extractor.metadata.exiftool.EXIF:DateTimeOriginal')
    history.append('generic.metadata.author')
    history.append('generic.contents.author')

    meowuri_completer = MeowURICompleter()

    print('')
    if message is not None:
        print(message)

    print('Use <TAB> to autocomplete and <RIGHT ARROW> for history completion.')
    text = prompt('Enter MeowURI: ', history=history,
                  auto_suggest=AutoSuggestFromHistory(),
                  completer=meowuri_completer,
                  enable_history_search=True,
                  on_abort=AbortAction.RETRY)
    return text


if __name__ == '__main__':
    response = meowuri_prompt()
    print('Got: {!s}'.format(response))
