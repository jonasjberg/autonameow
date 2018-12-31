# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core import constants as C
from core import interactive
from core import logs
from core import namebuilder
from core.evaluate import RuleMatcher
from core.evaluate import TemplateFieldDataResolver
from core.exceptions import AutonameowException
from core.exceptions import NameBuilderError
from util import encoding as enc


log = logging.getLogger(__name__)


class FileContext(object):
    def __init__(self, fileobject, ui, autonameow_exit_code, options, active_config,
                 masterprovider):
        self.fileobject = fileobject
        self.ui = ui
        self.autonameow_exit_code = autonameow_exit_code
        self.opts = options
        self.active_config = active_config
        self._masterprovider = masterprovider

        self._active_rule = None

    def find_new_name(self):
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
        #
        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        # TODO: [hack][cleanup] This is such a mess ..
        data_sources = None
        name_template = None

        matched_rules = self._get_matched_rules()
        log.debug('Matcher returned %s matched rules', len(matched_rules))
        if matched_rules:
            active_rule = self._pop_from_matched_rules(matched_rules)
            if active_rule:
                log.info('Using rule: "%s"', active_rule)
                self._active_rule = active_rule
                data_sources = active_rule.data_sources
                name_template = active_rule.name_template

        if not name_template:
            if self.opts.get('batch'):
                self._log_fail('Name template unknown. Running in batch mode -- Aborting')
                self._log_unable_to_find_new_name()
                return None

            # Have the user select a name template.
            # TODO: [TD0024][TD0025] Implement Interactive mode.
            self._log_fail('Name template unknown')
            self._log_unable_to_find_new_name()
            return None

        if not data_sources:
            # TODO: [hack][cleanup] This is such a mess ..
            if not name_template.placeholders:
                # No placeholders means we don't need any sources. Return as-is.
                return str(name_template)

            if self.opts.get('batch'):
                self._log_fail('Data sources unknown. Running in batch mode -- Aborting')
                self._log_unable_to_find_new_name()
                self.autonameow_exit_code = C.EXIT_WARNING
                return None

            if self.opts.get('automagic'):
                # Try real hard to figure it out (?)
                pass

            # Have the user select data sources.
            # TODO: [TD0024][TD0025] Implement Interactive mode.
            self._log_fail('Data sources unknown')
            self._log_unable_to_find_new_name()
            return None

        field_databundle_dict = self._get_resolved_databundle_dict(name_template.placeholders, data_sources)
        if not field_databundle_dict:
            if not self.opts.get('automagic'):
                self._log_fail('Missing field data bundles. Not in automagic mode -- Aborting')
                self._log_unable_to_find_new_name()
                self.autonameow_exit_code = C.EXIT_WARNING
                return None

            while not field_databundle_dict:
                # Try real hard to figure it out (?)
                log.debug('Entering try-hard rule matching loop ..')
                if not matched_rules:
                    log.debug('No matched_rules! Exiting try-hard matching loop')
                    break

                log.debug('Remaining matched_rules: %s', len(matched_rules))
                active_rule = self._pop_from_matched_rules(matched_rules)
                if active_rule:
                    log.info('Using rule: "%s"', active_rule)
                    self._active_rule = active_rule
                    data_sources = active_rule.data_sources
                    name_template = active_rule.name_template

                    if not data_sources:
                        # TODO: [hack][cleanup] This is such a mess ..
                        if not name_template.placeholders:
                            # No placeholders means we don't need any sources. Return as-is.
                            return str(name_template)

                    # Uses new resolver instance with state derived from the currently active rule.
                    field_databundle_dict = self._get_resolved_databundle_dict(name_template.placeholders, data_sources)

        if not field_databundle_dict:
            self._log_fail('Missing data bundles for all fields')
            self._log_unable_to_find_new_name()
            self.autonameow_exit_code = C.EXIT_WARNING
            return None

        try:
            new_name = namebuilder.build(
                config=self.active_config,
                name_template=name_template,
                field_databundle_dict=field_databundle_dict
            )
        except NameBuilderError as e:
            log.critical('Name assembly FAILED: %s', e)
            raise AutonameowException

        log.info('Found new name for "%s" using rule "%s"',
                 self.fileobject, self._active_rule)
        log.info('New name: "%s"', enc.displayable_path(new_name))
        return new_name

    def _log_unable_to_find_new_name(self):
        log.warning('Unable to find new name for "%s" using rule "%s"',
                    self.fileobject, self._active_rule)

    def _log_fail(self, msg):
        log.info('("%s") %s', self.fileobject, msg)

    def _get_matched_rules(self):
        matcher = RuleMatcher(
            rules=self.active_config.rules,
            masterprovider=self._masterprovider,
            fileobject=self.fileobject,
            ui=self.ui,
            list_rulematch=self.opts.get('list_rulematch')
        )
        with logs.log_runtime(log, 'Rule-Matching'):
            # Returns a list of 'MatchedRule' named tuples.
            matched_rules = matcher.get_matched_rules()

        return matched_rules

    def _pop_from_matched_rules(self, _matched_rules):
        if not _matched_rules:
            return None

        if self.opts.get('interactive'):
            # Have the user select a rule from any candidate matches.
            log.warning('[UNIMPLEMENTED FEATURE] interactive mode')
            log.warning('TODO: Implement interactive rule selection.')
            # TODO: [TD0024][TD0025] Implement Interactive mode.

        # User rule selection did not happen or failed ..
        candidate_matched_rule = _matched_rules.pop(0)
        assert candidate_matched_rule
        candidate_rule = candidate_matched_rule.rule
        candidate_score = candidate_matched_rule.score

        # Is the score of the best matched rule high enough?
        RULE_SCORE_CONFIRM_THRESHOLD = 0.0
        if candidate_score > RULE_SCORE_CONFIRM_THRESHOLD:
            return candidate_rule

        # Best matched rule might be a bad fit.
        log.debug('Score %s is below threshold %s for rule "%s"',
                  candidate_score, RULE_SCORE_CONFIRM_THRESHOLD, candidate_rule)
        ok_to_use_rule = self._confirm_apply_rule(candidate_rule)
        if ok_to_use_rule:
            log.debug('Positive response. Using rule "%s"', candidate_rule)
            return candidate_rule

        log.debug('Negative response. Will not use rule "%s"', candidate_rule)
        return None

    def _confirm_apply_rule(self, rule):
        if self.opts.get('batch'):
            log.info('Rule required confirmation but in batch mode -- '
                     'Skipping file ..')
            return False

        user_response = interactive.ask_confirm_use_rule(self.fileobject, rule)
        log.debug('User response: "%s"', user_response)
        return user_response

    def _get_resolved_databundle_dict(self, placeholders, data_sources):
        log.debug('Setting up new TemplateFieldDataResolver to get '
                  'resolved databundle dict for %d placeholders from %d '
                  'data sources', len(placeholders), len(data_sources))

        resolver = TemplateFieldDataResolver(
            fileobject=self.fileobject,
            name_template_fields=placeholders,
            masterprovider=self._masterprovider,
            config=self.active_config
        )
        resolver.add_known_sources(data_sources)

        # TODO: Rework the rule matcher and this logic to try another candidate.

        if not resolver.mapped_all_template_fields():
            if self.opts.get('batch'):
                self._log_fail('Unable to resolve all name template fields. '
                               'Running in batch mode -- Aborting')
                self._log_unable_to_find_new_name()
                self.autonameow_exit_code = C.EXIT_WARNING
                return None

        resolver.collect()

        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        if not resolver.collected_all():
            log.info('Resolver has not collected all fields ..')
            if self.opts.get('batch'):
                self._log_fail('Unable to resolve all name template fields. '
                               'Running in batch mode -- Aborting')
                self._log_unable_to_find_new_name()
                return None

            # TODO: [TD0024][TD0025] Implement Interactive mode.
            for field in resolver.unresolved:
                candidates = resolver.lookup_candidates(field)
                log.info('Found %s candidates for field %s', len(candidates), field)
                choice = None
                if candidates:
                    # Returns instance of 'FieldDataCandidate' or 'Choice.ABORT'
                    choice = interactive.select_field(self.fileobject, field, candidates)

                # TODO: [TD0024] Use MeowURI prompt in interactive mode?
                if choice is interactive.Choice.ABORT:
                    log.info('Aborting ..')
                    return None

                if choice:
                    log.debug('User selected %s', choice)
                    # TODO: Translate generic 'choice.meowuri' to not generic..
                    resolver.add_known_source(field, choice.meowuri)

            resolver.collect()

        # TODO: [TD0024] Should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.
        if not resolver.collected_all():
            # TODO: Abort if running in "batch mode". Otherwise, ask the user.
            self._log_fail('Resolver could not collect all field data')
            self._log_unable_to_find_new_name()
            self.autonameow_exit_code = C.EXIT_WARNING
            return None

        return resolver.fields_data
