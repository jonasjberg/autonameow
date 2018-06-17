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
from core.config.configuration import Configuration
from core.config.field_parsers import BooleanConfigFieldParser
from core.config.field_parsers import DateTimeConfigFieldParser
from core.config.field_parsers import NameTemplateConfigFieldParser
from core.config.rules import get_valid_rule
from core.config.rules import InvalidRuleConditionError
from core.config.rules import InvalidRuleError
from core.config.rules import RuleCondition
from core.exceptions import ConfigError
from core.exceptions import ConfigurationSyntaxError
from core.exceptions import FilesystemError
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.namebuilder.fields import is_valid_template_field
from util import coercers
from util import disk
from util import encoding as enc
from util import sanity
from util import text


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
# TODO: [cleanup][hack] This entire file is way too complicated and messy!


class ConfigurationParser(object):
    def __init__(self):
        # NOTE(jonas): Make sure that defaults are not modified.
        #              Seems to solve problem of state not fully reset between
        #              regression test cases caused by various design flaws..
        self._options = copy.deepcopy(INITIAL_CONFIGURATION_OPTIONS)

    def parse(self, config_dict):
        reusable_name_templates = self._load_reusable_name_templates(config_dict)
        self._options.update(
            self._load_placeholder_field_options(config_dict)
        )

        rule_parser = ConfigurationRuleParser(reusable_name_templates)
        raw_rules = config_dict.get('RULES', dict())
        valid_rules = rule_parser.parse(raw_rules)

        self._load_options(config_dict)
        version = self._load_version(config_dict)

        new_config = Configuration(
            options=self._options,
            rules_=valid_rules,
            reusable_nametemplates=reusable_name_templates,
            version=version
        )
        return new_config

    @staticmethod
    def _load_reusable_name_templates(config_dict):
        raw_templates = config_dict.get('NAME_TEMPLATES', {})
        if not raw_templates:
            return dict()

        if not isinstance(raw_templates, dict):
            raise ConfigurationSyntaxError(
                'Expected "NAME_TEMPLATES" to be of type dict. Got {}'.format(type(raw_templates))
            )

        validated = dict()
        for raw_name, raw_format_string in raw_templates.items():
            error = 'Invalid name template: "{!s}": {!s}"'.format(raw_name, raw_format_string)
            str_name = _coerce_string(raw_name).strip()
            str_format_string = _coerce_string(raw_format_string)
            if not str_name or not str_format_string:
                raise ConfigurationSyntaxError(error)

            if NameTemplateConfigFieldParser.is_valid_nametemplate_string(str_format_string):
                validated[str_name] = str_format_string
            else:
                raise ConfigurationSyntaxError(error)

        return validated

    @staticmethod
    def _load_placeholder_field_options(config_dict):
        # TODO: [TD0036] Allow per-field replacements and customization.
        raw_name_template_fields = config_dict.get('NAME_TEMPLATE_FIELDS')
        if not raw_name_template_fields:
            log.debug(
                'Configuration does not contain any name template field options'
            )
            return dict()

        if not isinstance(raw_name_template_fields, dict):
            log.warning('Name template field options is not of type dict')
            return dict()

        validated = dict()
        for raw_field, raw_options in raw_name_template_fields.items():
            str_field = _coerce_string(raw_field)
            if not is_valid_template_field(str_field):
                raise ConfigurationSyntaxError(
                    'Invalid name template field: "{!s}"'.format(raw_field)
                )

            # User-defined names with lists of patterns.
            for repl, pat_list in raw_options.get('candidates', {}).items():
                _validated_candidates = list()
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
                    _nested_dict_set(
                        dictionary=validated,
                        list_of_keys=['NAME_TEMPLATE_FIELDS', str_field, 'candidates', repl],
                        value=_validated_candidates
                    )

        return validated

    def _load_options(self, config_dict):
        options_parser = ConfigurationOptionsParser(
            raw_options=config_dict,
            initial_options=self._options
        )

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
            option='cache_directory',
            default=C.DEFAULT_PERSISTENCE_DIR_ABSPATH
        )
        options_parser.try_load_persistence_option(
            option='history_file_path',
            default=C.DEFAULT_HISTORY_FILE_ABSPATH
        )

        # TODO: [cleanup] This is way too complicated and not at all readable.
        self._options.update(options_parser.parsed)

        # Handle conflicting upper-case and lower-case options.
        if (self._options['POST_PROCESSING']['lowercase_filename']
                and self._options['POST_PROCESSING']['uppercase_filename']):

            log.warning('Conflicting options: "lowercase_filename" and '
                        '"uppercase_filename". Ignoring "uppercase_filename".')
            self._options['POST_PROCESSING']['uppercase_filename'] = False

        # TODO: [TD0137] Add rule-specific replacements.
        self._try_load_postprocessing_replacements(config_dict)

        self._try_load_filesystem_options(config_dict)

    def _try_load_postprocessing_replacements(self, config_dict):
        log.debug('Trying to load post-processing replacements')

        # TODO: [TD0141] Coerce raw values to a known type.
        if 'POST_PROCESSING' not in config_dict:
            log.debug('Did not find any post-processing options ..')
            return

        raw_replacements = config_dict['POST_PROCESSING'].get('replacements')
        if not raw_replacements or not isinstance(raw_replacements, dict):
            log.warning('Unable to load post-processing replacements')
            return

        match_replace_pairs = list()
        for regex, replacement in raw_replacements.items():
            str_regex = _coerce_string(regex)
            str_replacement = _coerce_string(replacement)
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

    def _try_load_filesystem_options(self, config_dict):
        # Combine the default ignore patterns with any user-specified patterns.
        if 'FILESYSTEM_OPTIONS' in config_dict:
            _maybe_str_list = config_dict['FILESYSTEM_OPTIONS'].get('ignore')
            _user_ignores = [
                s for s in _coerce_stringlist(_maybe_str_list) if s.strip()
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
            raw_version = config_dict['COMPATIBILITY'].get('autonameow_version')
            valid_version = parse_versioning(raw_version)
            if valid_version:
                return valid_version
            log.debug('Read invalid version: "{!s}"'.format(raw_version))

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
            ConfigError: The configuration file is empty or could not be parsed.
        """
        sanity.check_internal_bytestring(path)

        try:
            loaded_data = disk.load_yaml_file(path)
        except FilesystemError as e:
            raise ConfigError(e)

        if not loaded_data:
            raise ConfigError('Read empty config: "{!s}"'.format(
                enc.displayable_path(path)
            ))

        return self.parse(loaded_data)


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
        return self._parse_rules(rules_dict)

    def _parse_rules(self, rules_dict):
        parsed_rules = list()

        for raw_rule_name, raw_rule_data in rules_dict.items():
            str_rule_name = _coerce_string(raw_rule_name)
            if not str_rule_name:
                log.error('Skipped rule with bad name: "{!s}"'.format(raw_rule_name))
                continue

            raw_rule_data.update({'description': str_rule_name})
            log.debug('Validating rule "{!s}" ..'.format(str_rule_name))
            try:
                valid_rule = self._to_rule_instance(raw_rule_data)
            except ConfigurationSyntaxError as e:
                log.error('Validation failed for rule "{!s}" :: {!s}'.format(str_rule_name, e))
            else:
                log.debug('Validated rule "{!s}" .. OK!'.format(str_rule_name))
                parsed_rules.append(valid_rule)

        return parsed_rules

    def _to_rule_instance(self, raw_rule):
        """
        Validates one "raw" rule from a configuration and returns an
        instance of the 'Rule' class, representing the "raw" rule.

        Args:
            raw_rule: A single rule entry from a configuration.

        Returns:
            An instance of the 'Rule' class representing the given rule.

        Raises:
            ConfigurationSyntaxError: Validation of the raw rule data failed
                                      could not be used to instantiate objects.
        """
        description = _coerce_string(raw_rule.get('description'))
        format_string = self._parse_format_string(raw_rule.get('NAME_TEMPLATE'))
        conditions = parse_rule_conditions(raw_rule.get('CONDITIONS'))
        exact_match = parse_rule_exact_match(raw_rule.get('exact_match'))
        ranking_bias = parse_rule_ranking_bias(raw_rule.get('ranking_bias'))

        try:
            return get_valid_rule(
                description=description,
                exact_match=exact_match,
                ranking_bias=ranking_bias,
                format_string=format_string,
                conditions=conditions,
                raw_data_sources=raw_rule.get('DATA_SOURCES')
            )
        except InvalidRuleError as e:
            raise ConfigurationSyntaxError(e)

    def _parse_format_string(self, raw_format_string):
        str_format_string = _coerce_string(raw_format_string)
        if not str_format_string:
            raise ConfigurationSyntaxError('missing name template format string')

        valid_format_string = self._lookup_name_template_format_string(str_format_string)
        if not valid_format_string:
            raise ConfigurationSyntaxError('bad name template format string')

        return valid_format_string

    def _lookup_name_template_format_string(self, str_template):
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


def _coerce_string(data):
    str_data = coercers.force_string(data)
    return text.remove_nonbreaking_spaces(str_data)


def _coerce_stringlist(data_list):
    str_data_list = coercers.force_stringlist(data_list)
    return [text.remove_nonbreaking_spaces(s) for s in str_data_list]


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
                # OK!
                return

        # Use the default value.
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
                    bytes_value = coercers.coerce_to_normalized_path(raw_value)
                except coercers.AWTypeError as e:
                    log.error('Bad value for option {}: "{!s}"'.format(
                        option, coercers.force_string(raw_value)
                    ))
                    log.debug(str(e))
                else:
                    log.debug('Added persistence option :: {!s}: {!s}'.format(
                        option, enc.displayable_path(bytes_value)
                    ))
                    self.parsed['PERSISTENCE'][option] = bytes_value
                    # OK!
                    return

        # Use the default value.
        bytes_default = coercers.coerce_to_normalized_path(default)
        log.debug(
            'Using default persistence option :: {!s}: {!s}'.format(
                option, enc.displayable_path(bytes_default)
            )
        )
        self.parsed['PERSISTENCE'][option] = bytes_default


def parse_rule_conditions(raw_conditions):
    if not raw_conditions:
        return list()

    if not isinstance(raw_conditions, dict):
        raise ConfigurationSyntaxError('Expected conditions of type "dict". '
                                       'Got {!s}'.format(type(raw_conditions)))

    log.debug('Parsing {} raw conditions ..'.format(len(raw_conditions)))
    passed = list()
    for str_meowuri, raw_expression in raw_conditions.items():
        try:
            uri = MeowURI(str_meowuri)
        except InvalidMeowURIError as e:
            raise ConfigurationSyntaxError(e)
        else:
            try:
                valid_condition = RuleCondition(uri, raw_expression)
            except InvalidRuleConditionError as e:
                raise ConfigurationSyntaxError(e)

            passed.append(valid_condition)
            log.debug('Validated condition: "{!s}"'.format(valid_condition))

    log.debug(
        'Returning {} (out of {}) valid conditions'.format(len(passed),
                                                           len(raw_conditions))
    )
    return passed


def parse_rule_exact_match(raw_exact_match):
    try:
        return coercers.AW_BOOLEAN(raw_exact_match)
    except coercers.AWTypeError:
        raise ConfigurationSyntaxError('bad value for "exact match"')


def parse_rule_ranking_bias(value):
    """
    Validates data to be used as a "ranking_bias".

    The value must be an integer or float between 0 and 1.
    To allow for an unspecified bias, None values are allowed and substituted
    with the default bias defined by "DEFAULT_RULE_RANKING_BIAS".

    Args:
        value: The "raw" value to parse.
    Returns:
        The specified value if the value is a number type in the range 0-1.
        If the specified value is None, a default bias is returned.
    Raises:
        ConfigurationSyntaxError: The value is of an unexpected type or not
                                  within the range 0-1.
    """
    if value is None:
        return C.DEFAULT_RULE_RANKING_BIAS

    try:
        float_value = coercers.AW_FLOAT(value)
    except coercers.AWTypeError:
        raise ConfigurationSyntaxError(
            'Expected float but got "{!s}" ({!s})'.format(value, type(value))
        )
    else:
        if not 0.0 <= float_value <= 1.0:
            raise ConfigurationSyntaxError(
                'Expected float between 0.0 and 1.0. Got {} -- Using default: '
                '{}'.format(value, C.DEFAULT_RULE_RANKING_BIAS)
            )
        return float_value


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
    if not isinstance(semver_string, str) or not semver_string.strip():
        return None

    RE_VERSION_NUMBER = re.compile(r'v?(\d+)\.(\d+)\.(\d+)')
    match = RE_VERSION_NUMBER.search(semver_string)
    if match:
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        return major, minor, patch

    return None


def _nested_dict_set(dictionary, list_of_keys, value):
    """
    Sets a value in a nested dictionary structure.

    The structure is traversed using the given list of keys and the destination
    dictionary is set to the given value, unless the traversal fails by
    attempting to overwrite an already existing value with a new dictionary
    entry.

    The list of keys can not contain any None or whitespace-only items.

    Note that the dictionary is modified IN PLACE.

    Based on this post:  https://stackoverflow.com/a/37704379/7802196

    Args:
        dictionary: The dictionary from which to retrieve a value.
        list_of_keys: List of keys to the value to set, as any hashable type.
        value: The new value that will be set in the given dictionary.
    Raises:
        ValueError: Arg 'list_of_keys' contains None or whitespace-only string.
        KeyError: Existing value would have been clobbered.
    """
    assert list_of_keys and isinstance(list_of_keys, list), (
        'Expected "list_of_keys" to be a list of strings'
    )

    if (None in list_of_keys or
            any(k.strip() == '' for k in list_of_keys if isinstance(k, str))):
        raise ValueError(
            'Expected "list_of_keys" to not contain any None/"empty" items'
        )

    for key in list_of_keys[:-1]:
        dictionary = dictionary.setdefault(key, {})

    try:
        dictionary[list_of_keys[-1]] = value
    except TypeError:
        # TODO: Add keyword-argument to allow overwriting any existing.
        # This happens when the dictionary contains a non-dict item where one
        # of the keys would go. For example;
        #
        #    example_dict = {'a': 2,
        #                    'b': {'c': 4,
        #                          'foo': 6}})
        #
        # Calling "_nested_dict_set(example_dict, ['a', 'foo'], 1])" would
        # fail because 'a' stores the integer "2" where we would like to
        # create the new dict;  "{'foo': 6}"
        raise KeyError('Caught TypeError (would have clobbered existing value)')
