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

import copy
import logging
import re

import util
from core import constants as C
from core import types
from core.config.configuration import Configuration
from core.config.rules import (
    get_valid_rule,
    InvalidRuleError
)
from core.config.field_parsers import (
    BooleanConfigFieldParser,
    DateTimeConfigFieldParser,
    NameTemplateConfigFieldParser,
)
from core.exceptions import (
    ConfigurationSyntaxError,
    ConfigError,
    FilesystemError,
)
from core.namebuilder.fields import is_valid_template_field
from util import encoding as enc
from util import (
    disk,
    sanity,
    text
)


log = logging.getLogger(__name__)


INITIAL_CONFIGURATION_OPTIONS = {
    'DATETIME_FORMAT': dict(),

    # Default ignores to be combined with any user-specified patterns.
    'FILESYSTEM': {
        'ignore': C.DEFAULT_FILESYSTEM_IGNORE
    },

    'FILETAGS_OPTIONS': dict(),
    'PERSISTENCE': dict(),
    'POST_PROCESSING': dict()
}


# TODO: [TD0154] Add "incrementing counter" placeholder field


class ConfigurationParser(object):
    def __init__(self):
        # NOTE(jonas): Make sure that defaults are not modified.
        #              Seems to solve problem of state not fully reset between
        #              regression test cases caused by various design flaws..
        self._options = copy.deepcopy(INITIAL_CONFIGURATION_OPTIONS)

    def parse(self, config_dict):
        _reusable_nametemplates = self._load_reusable_nametemplates(config_dict)
        self._options.update(
            self._load_template_fields(config_dict)
        )

        rule_parser = ConfigurationRuleParser(_reusable_nametemplates)
        _raw_rules = config_dict.get('RULES', dict())
        _rules = rule_parser.parse(_raw_rules)

        self._load_options(config_dict)
        version = self._load_version(config_dict)

        new_config = Configuration(
            options=self._options,
            rules_=_rules,
            reusable_nametemplates=_reusable_nametemplates,
            version=version
        )
        return new_config

    @staticmethod
    def _load_reusable_nametemplates(config_dict):
        validated = dict()

        raw_templates = config_dict.get('NAME_TEMPLATES', {})
        if not isinstance(raw_templates, dict):
            log.warning('Configuration templates is not of type dict')
            log.debug('Expected NAME_TEMPLATES to be of type "dict". '
                      'Got {}'.format(type(raw_templates)))
            return validated

        for raw_name, raw_templ in raw_templates.items():
            _error = 'Got invalid name template: "{!s}": {!s}"'.format(
                raw_name, raw_templ
            )
            str_name = types.force_string(raw_name).strip()
            str_template = types.force_string(raw_templ)
            if not str_name or not str_template:
                raise ConfigurationSyntaxError(_error)

            # Remove any non-breaking spaces in the name template.
            str_template = text.remove_nonbreaking_spaces(str_template)

            if NameTemplateConfigFieldParser.is_valid_nametemplate_string(str_template):
                validated[str_name] = str_template
            else:
                raise ConfigurationSyntaxError(_error)

        return validated

    @staticmethod
    def _load_template_fields(config_dict):
        # TODO: [TD0036] Allow per-field replacements and customization.
        validated = dict()

        raw_templatefields = config_dict.get('NAME_TEMPLATE_FIELDS')
        if not raw_templatefields:
            log.debug(
                'Configuration does not contain name template field options'
            )
            return validated
        if not isinstance(raw_templatefields, dict):
            log.warning('Name template field options is not of type dict')
            return validated

        for raw_field, raw_options in raw_templatefields.items():
            str_field = types.force_string(raw_field)
            if not is_valid_template_field(str_field):
                raise ConfigurationSyntaxError(
                    'Invalid name template field: "{!s}"'.format(raw_field)
                )

            # User-defined names with lists of patterns.
            for repl, pat_list in raw_options.get('candidates', {}).items():
                _validated_candidates = []
                for _pat in pat_list:
                    try:
                        compiled_pat = re.compile(_pat, re.IGNORECASE)
                    except re.error:
                        raise ConfigurationSyntaxError(
                            'Malformed regular expression: "{!s}"'.format(_pat)
                        )

                    log.debug(
                        'Added name template field pattern :: Match: "{!s}"'
                        ' Replace: "{!s}"'.format(_pat, repl)
                    )
                    _validated_candidates.append(compiled_pat)

                if _validated_candidates:
                    util.nested_dict_set(
                        validated,
                        ['NAME_TEMPLATE_FIELDS', str_field, 'candidates', repl],
                        _validated_candidates
                    )

        return validated

    def _load_options(self, config_dict):
        def _try_load_postprocessing_replacements():
            log.debug('Trying to load post-processing replacements')

            # TODO: [TD0141] Coerce raw values to a known type.
            if 'POST_PROCESSING' not in config_dict:
                log.debug('Did not find any post-processing options ..')
                return

            _reps = config_dict['POST_PROCESSING'].get('replacements')
            if not _reps or not isinstance(_reps, dict):
                log.warning('Unable to load post-processing replacements')
                return

            match_replace_pairs = []
            for regex, replacement in _reps.items():
                str_regex = types.force_string(regex)
                str_replacement = types.force_string(replacement)
                try:
                    compiled_pat = re.compile(str_regex)
                except re.error:
                    log.warning('Malformed regular expression: '
                                '"{!s}"'.format(str_regex))
                    log.warning('Skipped bad replacement :: "{!s}": '
                                '"{!s}"'.format(regex, replacement))
                else:
                    log.debug(
                        'Added post-processing replacement :: Match: "{!s}"'
                        ' Replace: "{!s}"'.format(regex, replacement)
                    )
                    match_replace_pairs.append((compiled_pat, str_replacement))

            self._options['POST_PROCESSING']['replacements'] = match_replace_pairs

        options_parser = ConfigurationOptionsParser(raw_options=config_dict,
                                                    initial_options=self._options)
        options_parser.try_load_option(
            section='DATETIME_FORMAT',
            key='date',
            validation_func=DateTimeConfigFieldParser.is_valid_datetime,
            default=C.DEFAULT_DATETIME_FORMAT_DATE
        )
        options_parser.try_load_option(
            section='DATETIME_FORMAT',
            key='time',
            validation_func=DateTimeConfigFieldParser.is_valid_datetime,
            default=C.DEFAULT_DATETIME_FORMAT_TIME
        )
        options_parser.try_load_option(
            section='DATETIME_FORMAT',
            key='datetime',
            validation_func=DateTimeConfigFieldParser.is_valid_datetime,
            default=C.DEFAULT_DATETIME_FORMAT_DATETIME
        )

        options_parser.try_load_option(
            section='FILETAGS_OPTIONS',
            key='filename_tag_separator',
            # TODO: [TD0141] Coerce raw values to a known type.
            validation_func=lambda x: True,
            default=C.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR
        )
        options_parser.try_load_option(
            section='FILETAGS_OPTIONS',
            key='between_tag_separator',
            # TODO: [TD0141] Coerce raw values to a known type.
            validation_func=lambda x: True,
            default=C.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR
        )

        options_parser.try_load_option(
            section='POST_PROCESSING',
            key='sanitize_filename',
            validation_func=BooleanConfigFieldParser.is_valid_boolean,
            default=C.DEFAULT_POSTPROCESS_SANITIZE_FILENAME
        )
        options_parser.try_load_option(
            section='POST_PROCESSING',
            key='sanitize_strict',
            validation_func=BooleanConfigFieldParser.is_valid_boolean,
            default=C.DEFAULT_POSTPROCESS_SANITIZE_STRICT
        )
        options_parser.try_load_option(
            section='POST_PROCESSING',
            key='lowercase_filename',
            validation_func=BooleanConfigFieldParser.is_valid_boolean,
            default=C.DEFAULT_POSTPROCESS_LOWERCASE_FILENAME
        )
        options_parser.try_load_option(
            section='POST_PROCESSING',
            key='uppercase_filename',
            validation_func=BooleanConfigFieldParser.is_valid_boolean,
            default=C.DEFAULT_POSTPROCESS_UPPERCASE_FILENAME
        )
        options_parser.try_load_option(
            section='POST_PROCESSING',
            key='simplify_unicode',
            validation_func=BooleanConfigFieldParser.is_valid_boolean,
            default=C.DEFAULT_POSTPROCESS_SIMPLIFY_UNICODE
        )

        options_parser.try_load_persistence_option(
            'cache_directory',
            C.DEFAULT_PERSISTENCE_DIR_ABSPATH
        )
        options_parser.try_load_persistence_option(
            'history_file_path',
            C.DEFAULT_HISTORY_FILE_ABSPATH
        )

        self._options.update(options_parser.parsed)

        # Handle conflicting upper-case and lower-case options.
        if (self._options['POST_PROCESSING']['lowercase_filename']
                and self._options['POST_PROCESSING']['uppercase_filename']):

            log.warning('Conflicting options: "lowercase_filename" and '
                        '"uppercase_filename". Ignoring "uppercase_filename".')
            self._options['POST_PROCESSING']['uppercase_filename'] = False

        # TODO: [TD0137] Add rule-specific replacements.
        _try_load_postprocessing_replacements()

        # Combine the default ignore patterns with any user-specified patterns.
        if 'FILESYSTEM_OPTIONS' in config_dict:
            _maybe_str_list = config_dict['FILESYSTEM_OPTIONS'].get('ignore')
            _user_ignores = [
                s for s in types.force_stringlist(_maybe_str_list) if s.strip()
            ]
            if _user_ignores:
                for s in _user_ignores:
                    log.debug('Added filesystem option :: '
                              '{!s}: {!s}'.format('user ignore', s))

                _defaults = self._options['FILESYSTEM']['ignore']
                _combined = _defaults.union(frozenset(_user_ignores))
                log.debug('Loaded {} filesystem ignore patterns ({} default + '
                          '{} user)'.format(len(_combined), len(_defaults),
                                            len(_user_ignores)))
                self._options['FILESYSTEM']['ignore'] = _combined

    @staticmethod
    def _load_version(config_dict):
        if 'COMPATIBILITY' in config_dict:
            _raw_version = config_dict['COMPATIBILITY'].get('autonameow_version')
            valid_version = parse_versioning(_raw_version)
            if valid_version:
                return valid_version
            else:
                log.debug('Read invalid version: "{!s}"'.format(_raw_version))

        log.error('Unable to read program version from configuration.')
        return None

    def from_file(self, path):
        """
        Returns a new Configuration instantiated from data at a given path.

        Args:
            path: Path of the (YAML) file to read, as an "internal" bytestring.

        Returns:
            An instance of 'Configuration', created from the data at "path".

        Raises:
            EncodingBoundaryViolation: Argument "path" is not a bytestring.
            ConfigError: The configuration file is empty.
        """
        sanity.check_internal_bytestring(path)

        try:
            _loaded_data = disk.load_yaml_file(path)
        except FilesystemError as e:
            raise ConfigError(e)

        if not _loaded_data:
            raise ConfigError('Read empty config: "{!s}"'.format(
                enc.displayable_path(path)
            ))

        return self.parse(_loaded_data)


class ConfigurationRuleParser(object):
    def __init__(self, reusable_nametemplates=None):
        if reusable_nametemplates:
            self._reusable_nametemplates = reusable_nametemplates
        else:
            self._reusable_nametemplates = dict()

    def parse(self, rules_dict):
        if not isinstance(rules_dict, dict):
            raise ConfigurationSyntaxError('Expected rules to be type "dict". '
                                           'Got {!s}'.format(type(rules_dict)))

        validated = self._validate_rules(rules_dict)
        return validated

    def _validate_name_template(self, _raw_name_template):
        # TODO: [TD0180] Does this duplicate name template validation?
        str_template = types.force_string(_raw_name_template)
        if not str_template:
            return None

        # TODO: [TD0109] Allow arbitrary name template placeholder fields.

        # First test if the field data is a valid name template entry,
        if str_template in self._reusable_nametemplates:
            # If it is, use the format string defined in that entry.
            return self._reusable_nametemplates.get(str_template)
        else:
            # If not, check if it is a valid name template string.
            if NameTemplateConfigFieldParser.is_valid_nametemplate_string(str_template):
                # TODO: [TD0139] This currently passes just about everything.
                # If the user intends to use a "reusable name template" but
                # misspelled it slightly, it currently goes unnoticed.

                # TODO: [TD0139] Warn if sources do not match placeholders?
                return str_template

        return None

    def _to_rule_instance(self, raw_rule):
        """
        Validates one "raw" rule from a configuration and returns an
        instance of the 'Rule' class, representing the "raw" rule.

        Args:
            raw_rule: A single rule entry from a configuration.

        Returns:
            An instance of the 'Rule' class representing the given rule.

        Raises:
            ConfigurationSyntaxError: The given rule contains bad data,
                making instantiating a 'Rule' object impossible.
                Note that the message will be used in the following sentence:
                "Bad rule "x"; {message}"
        """
        raw_name_template = raw_rule.get('NAME_TEMPLATE')
        if not raw_name_template:
            raise ConfigurationSyntaxError('is missing name template')

        raw_name_template = text.remove_nonbreaking_spaces(raw_name_template)
        valid_template = self._validate_name_template(raw_name_template)
        if not valid_template:
            raise ConfigurationSyntaxError('uses invalid name template format')

        try:
            return get_valid_rule(
                raw_description=raw_rule.get('description'),
                raw_exact_match=raw_rule.get('exact_match'),
                raw_ranking_bias=raw_rule.get('ranking_bias'),
                format_string=valid_template,
                conditions=raw_rule.get('CONDITIONS'),
                raw_data_sources=raw_rule.get('DATA_SOURCES')
            )
        except InvalidRuleError as e:
            raise ConfigurationSyntaxError(e)

    def _validate_rules(self, rules_dict):
        validated = []

        for raw_name, raw_contents in rules_dict.items():
            str_name = types.force_string(raw_name)
            if not str_name:
                log.error('Skipped rule with bad name: "{!s}"'.format(raw_name))
                continue

            raw_contents.update({'description': str_name})
            log.debug('Validating rule "{!s}" ..'.format(str_name))
            try:
                valid_rule = self._to_rule_instance(raw_contents)
            except ConfigurationSyntaxError as e:
                log.error('Bad rule "{!s}"; {!s}'.format(str_name, e))
            else:
                log.debug('Validated rule "{!s}" .. OK!'.format(str_name))

                # Create and populate "Rule" objects with *validated* data.
                validated.append(valid_rule)

        return validated


class ConfigurationOptionsParser(object):
    def __init__(self, raw_options, initial_options):
        if not isinstance(raw_options, dict):
            raise ConfigurationSyntaxError(
                'Expected options to be type "dict". Got {!s}'.format(
                    type(raw_options)))

        self.raw_options = raw_options

        # Add parsed options to initial options, which set up nested dicts.
        self.parsed = dict(initial_options)

    def try_load_option(self, section, key, validation_func, default):
        assert section in self.parsed, (
            'Invalid (not "default") options section: "{!s}"'.format(section)
        )
        assert callable(validation_func)

        if section in self.raw_options:
            raw_value = self.raw_options[section].get(key, None)
            if raw_value is not None and validation_func(raw_value):
                # TODO: [TD0141] Coerce raw values to a known type.
                log.debug('Added {} option :: '
                          '{!s}: "{!s}"'.format(section, key, raw_value))
                self.parsed[section][key] = raw_value
                return  # OK!

        # Use the default value.
        if __debug__:
            if not validation_func(default):
                raise AssertionError(
                    'Bad default "{!s}" value: "{!s}"'.format(key, default)
                )
        log.debug('Using default for {} option {!s}: "{!s}"'.format(
            key, section, default
        ))
        self.parsed[section][key] = default

    def try_load_persistence_option(self, option, default):
        # TODO: [TD0160] Improve handling of setting up working directories.
        #       This current accepts just about anything that can be coerced
        #       into a path. Probably should solve this better; "validate" the
        #       path but make sure to accept non-existing paths to be created
        #       later on. Should add a global system for setting up directories.
        if 'PERSISTENCE' in self.raw_options:
            raw_value = self.raw_options['PERSISTENCE'].get(option)
            if isinstance(raw_value, (str, bytes)) and raw_value.strip():
                try:
                    _bytes_path = types.AW_PATH.normalize(raw_value)
                except types.AWTypeError as e:
                    _dp = enc.displayable_path(raw_value)
                    log.error('Bad value for option {}: "{!s}"'.format(option,
                                                                       _dp))
                    log.debug(str(e))
                else:
                    log.debug('Added persistence option :: {!s}: {!s}'.format(
                        option, enc.displayable_path(_bytes_path)
                    ))
                    self.parsed['PERSISTENCE'][option] = _bytes_path
                    return

        _bytes_path = types.AW_PATH.normalize(default)
        log.debug(
            'Using default persistence option :: {!s}: {!s}'.format(
                option, enc.displayable_path(_bytes_path)
            )
        )
        self.parsed['PERSISTENCE'][option] = _bytes_path


def parse_versioning(semver_string):
    """
    Validates a "raw" version number string.

    The version number is expected to be a Unicode string on the form 'v1.2.3',
    where the initial 'v' is optional;  I.E. '111.222.333' is also valid.

    Args:
        semver_string: The version number to validate as a Unicode string.

    Returns:
        A tuple of three integers representing the "major", "minor" and
        "patch" version numbers.  Or None if the validation fails.
    """
    if not semver_string or not isinstance(semver_string, str):
        return None
    if not semver_string.strip():
        return None

    RE_VERSION_NUMBER = re.compile(r'v?(\d+)\.(\d+)\.(\d+)')
    match = RE_VERSION_NUMBER.search(semver_string)
    if match:
        try:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
        except TypeError:
            pass
        else:
            return major, minor, patch

    return None
