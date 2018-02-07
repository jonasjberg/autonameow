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


from core import constants as C
from core import (
    interactive,
    logs,
    namebuilder,
)
from core.evaluate import TemplateFieldDataResolver
from core.exceptions import (
    AutonameowException,
    NameBuilderError
)
from util import encoding as enc


log = logging.getLogger(__name__)


class FilesContext(object):
    def __init__(self, autonameow_instance, options, active_config,
                 rule_matcher):
        self.ameow = autonameow_instance
        self.opts = options
        self.active_config = active_config
        self.matcher = rule_matcher

    def handle_file(self, current_file):
        # TODO: [TD0142] Fetch all possible data when using '--list-all'.
        should_list_any_results = self.opts.get('list_all')

        #  Things to find:
        #
        #    * NAME TEMPLATE
        #      Sources:   * User selection (interactive mode)
        #                 * Matched rule   (rule-matching, automagic)
        #
        #    * DATA SOURCES for name template fields
        #      Sources:   * User selection (interactive mode)
        #                 * Matched rule   (rule-matching, automagic)
        #                 * Yet unknown    (automagic)
        #
        #  Keeping in mind that:
        #
        #    * Matched Rule ---+--> Template
        #                      '--> Data Sources

        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        active_rule = None
        data_sources = None
        name_template = None
        if self.opts.get('mode_rulematch'):
            # TODO: Cleanup ..
            with logs.log_runtime(log, 'Rule-Matching'):
                candidates = self.matcher.match(current_file)
            log.debug('Matcher returned {} candidate rules'.format(len(candidates)))
            if candidates:
                active_rule = self._try_get_rule(current_file, candidates)

        if active_rule:
            log.info(
                'Using rule: "{!s}"'.format(active_rule.description)
            )
            data_sources = active_rule.data_sources
            name_template = active_rule.name_template

        if not name_template:
            if self.opts.get('mode_batch'):
                log.warning('Name template unknown! Aborting ..')
                self.ameow.exit_code = C.EXIT_WARNING
                return

            # Have the user select a name template.
            # TODO: [TD0024][TD0025] Implement Interactive mode.
            # candidates = None
            # choice = interactive.select_template(candidates)
            # if choice != ui.action.ABORT:
            #     name_template = choice
            # if not name_template:
            #     log.warning('No valid name template chosen. Aborting ..')

        if not name_template:
            # User name template selection did not happen or failed.
            log.warning('Name template unknown! Aborting ..')
            self.ameow.exit_code = C.EXIT_WARNING
            return

        if not data_sources:
            if self.opts.get('mode_automagic'):
                # Try real hard to figure it out (?)
                pass

            if self.opts.get('mode_batch'):
                log.warning('Data sources unknown! Aborting ..')
                self.ameow.exit_code = C.EXIT_WARNING
                return

            # Have the user select data sources.
            # TODO: [TD0024][TD0025] Implement Interactive mode.

        field_data_dict = self._try_resolve(current_file, name_template,
                                            data_sources)
        if not field_data_dict:
            if not self.opts.get('mode_automagic'):
                log.warning('Not in automagic mode. Unable to populate name.')
                self.ameow.exit_code = C.EXIT_WARNING
                return

            while not field_data_dict and candidates:
                # Try real hard to figure it out (?)
                log.debug('Start of try-hard rule matching loop ..')
                if not candidates:
                    log.debug('No candidates! Exiting try-hard matching loop')
                    break

                log.debug('Remaining candidates: {}'.format(len(candidates)))
                active_rule = self._try_get_rule(current_file, candidates)
                if active_rule:
                    log.info(
                        'Using rule: "{!s}"'.format(active_rule.description)
                    )
                    data_sources = active_rule.data_sources
                    name_template = active_rule.name_template
                    field_data_dict = self._try_resolve(current_file,
                                                        name_template,
                                                        data_sources)

        if not field_data_dict:
            log.warning('Unable to populate name.')
            self.ameow.exit_code = C.EXIT_WARNING
            return

        try:
            new_name = namebuilder.build(
                config=self.active_config,
                name_template=name_template,
                field_data_map=field_data_dict
            )
        except NameBuilderError as e:
            log.critical('Name assembly FAILED: {!s}'.format(e))
            raise AutonameowException

        log.info('New name: "{}"'.format(enc.displayable_path(new_name)))
        return new_name

    def _try_get_rule(self, current_file, candidates):
        active_rule = None

        if self.opts.get('mode_interactive'):
            log.warning('[UNIMPLEMENTED FEATURE] interactive mode')

            # Have the user select a rule from any candidate matches.
            # candidates = matcher.candidates()
            if candidates:
                log.warning('TODO: Implement interactive rule selection.')
                # TODO: [TD0024][TD0025] Implement Interactive mode.
                # choice = interactive.select_rule(candidates)
                # if choice != ui.action.ABORT:
                #     active_rule = choice
            else:
                log.debug('There are no rules available for the user to '
                          'choose from..')

        RULE_SCORE_CONFIRM_THRESHOLD = 0
        if candidates and not active_rule:
            # User rule selection did not happen or failed.
            best_match = candidates.pop(0)
            if best_match:
                # Is the score of the best matched rule high enough?
                rule, score, _ = best_match
                description = rule.description
                if score > RULE_SCORE_CONFIRM_THRESHOLD:
                    active_rule = rule
                else:
                    # Best matched rule might be a bad fit.
                    log.debug('Score {} is below threshold {} for rule "{!s}"'.format(score, RULE_SCORE_CONFIRM_THRESHOLD, description))
                    log.debug('Need confirmation before using this rule..')
                    ok_to_use_rule = self._confirm_apply_rule(current_file, rule)
                    if ok_to_use_rule:
                        log.debug('Positive response. Using rule "{!s}"'.format(description))
                        active_rule = rule
                    else:
                        log.debug('Negative response. Will not use rule "{!s}"'.format(description))
            else:
                log.debug('Rule-matcher did not find a "best match" rule')

        return active_rule

    def _try_resolve(self, current_file, name_template, data_sources):
        resolver = TemplateFieldDataResolver(current_file, name_template)
        resolver.add_known_sources(data_sources)

        # TODO: Rework the rule matcher and this logic to try another candidate.
        # if not resolver.mapped_all_template_fields():
        #     if self.opts.get('mode_automagic'):
        #         data_sources = matcher.candidates()[1]

        if not resolver.mapped_all_template_fields():
            if self.opts.get('mode_batch'):
                log.error('Unable to resolve all name template fields. '
                          'Running in batch mode -- Aborting..')
                self.ameow.exit_code = C.EXIT_WARNING
                return

        resolver.collect()

        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        if not resolver.collected_all():
            log.info('Resolver has not collected all fields ..')
            if self.opts.get('mode_batch'):
                log.warning('Unable to populate name.')
                # self.ameow.exit_code = C.EXIT_WARNING
                return

            # TODO: [TD0024][TD0025] Implement Interactive mode.
            for field in resolver.unresolved:
                candidates = resolver.lookup_candidates(field)
                log.info('Found {} candidates for field {!s}'.format(len(candidates), field.as_placeholder()))
                choice = None
                if candidates:
                    # Returns instance of 'FieldDataCandidate' or 'Choice.ABORT'
                    choice = interactive.select_field(current_file, field, candidates)

                # TODO: [TD0024] Use MeowURI prompt in interactive mode?
                # if choice is interactive.Choice.ABORT:
                #     _m = 'Specify source for field {!s}'.format(field)
                #     choice = interactive.meowuri_prompt(_m)

                if choice is interactive.Choice.ABORT:
                    log.info('Aborting ..')
                    return

                if choice:
                    log.debug('User selected {!r}'.format(choice))
                    # TODO: Translate generic 'choice.meowuri' to not generic..
                    resolver.add_known_source(field, choice.meowuri)

            resolver.collect()

        # TODO: [TD0024] Should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.
        if not resolver.collected_all():
            # TODO: Abort if running in "batch mode". Otherwise, ask the user.
            log.warning('Unable to populate name. Missing field data.')
            self.ameow.exit_code = C.EXIT_WARNING
            return None

        return resolver.fields_data

    def _confirm_apply_rule(self, current_file, rule):
        if self.opts.get('mode_batch'):
            log.info('Rule required confirmation but in batch mode -- '
                     'Skipping file ..')
            return False

        user_response = interactive.ask_confirm_use_rule(current_file, rule)
        log.debug('User response: "{!s}"'.format(user_response))
        return user_response
