#!/usr/bin/env python
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

from core import view
from util import sanity
from util import encoding as enc


log = logging.getLogger(__name__)


class Choice(object):
    ABORT = 0


def select_field(fileobject, templatefield, candidates):
    # TODO: [TD0024][TD0025] Implement Interactive mode.

    view.msg(enc.displayable_path(fileobject), style='section')
    view.msg('Candidates for unresolved field: {!s}'.format(
        templatefield.as_placeholder()))

    try:
        prioritized_candidates = sorted(candidates,
                                        key=lambda x: (x.probability, x.value),
                                        reverse=True)
    except TypeError as e:
        # TODO: FIX THIS! Must separate "real" value from displayable value!
        log.critical('Error while sorting candidates in "select_field()"')
        log.critical(str(e))
        return Choice.ABORT

    numbered_candidates = dict()
    rows_to_display = list()
    for n, c in enumerate(prioritized_candidates):
        _candidate_number = str(n)
        numbered_candidates[_candidate_number] = c

        if isinstance(c.value, list):
            c_value = ', '.join(c.value)
        else:
            c_value = c.value

        _candidate_value = '"{!s}"'.format(c_value)
        _candidate_source = str(c.source)
        _candidate_probability = str(c.probability)
        _candidate_meowuri = str(c.meowuri)
        rows_to_display.append(
            (_candidate_number, _candidate_source, _candidate_probability,
             _candidate_value, _candidate_meowuri)
        )

    cf = view.ColumnFormatter()
    cf.addemptyrow()
    cf.addrow('#', 'SOURCE', 'PROBABILITY', 'FORMATTED VALUE', 'MEOWURI')
    cf.addrow('=', '======', '===========', '===============', '=======')
    for row_to_display in rows_to_display:
        cf.addrow(*row_to_display)
    view.msg(str(cf))

    response = view.field_selection_prompt(numbered_candidates)
    if not response:
        return Choice.ABORT

    assert response in numbered_candidates
    # Returns an instance of the 'FieldDataCandidate' class.
    return numbered_candidates.get(response)


def select_template(candidates):
    # TODO: [TD0024][TD0025] Implement Interactive mode.
    log.warning('TODO: Implement user name template selection')

    return None


def meowuri_prompt(message):
    # TODO: [TD0024][TD0025] Implement Interactive mode.
    response = view.meowuri_prompt(message)
    if not response:
        return Choice.ABORT
    return response


def ask_confirm_use_rule(fileobject, rule):
    view.msg(enc.displayable_path(fileobject), style='section')
    user_response = ask_confirm(
        'Best matched rule "{!s}"'
        '\nProceed with this rule?'.format(rule.description)
    )
    return user_response


def ask_confirm(message=None):
    if message is None:
        msg = 'Please Confirm (unspecified action)? [y/n]'
    else:
        sanity.check_internal_string(message)
        msg = '{!s}  [y/n]'.format(message)

    response = view.ask_confirm(msg)
    assert isinstance(response, bool)
    return response


def ask_confirm_rename(from_basename, dest_basename):
    sanity.check_internal_string(from_basename)
    sanity.check_internal_string(dest_basename)

    view.msg_possible_rename(from_basename, dest_basename)
    response = view.ask_confirm('Proceed with rename? [y/n]')
    assert isinstance(response, bool)
    return response
