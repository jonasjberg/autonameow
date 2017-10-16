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

import logging
import os
import re

from core import constants as C
from core import (
    config,
    exceptions,
    types,
    util
)
from core.config import rules
from core.config.field_parsers import (
    DateTimeConfigFieldParser,
    NameFormatConfigFieldParser,
    parse_versioning
)
from core.namebuilder import fields
from core.util import sanity


log = logging.getLogger(__name__)


class Configuration(object):
    """
    Container for a loaded and active configuration.

    Loads and validates data from a dictionary or YAML file.
    """
    def __init__(self, source):
        """
        Instantiates a new Configuration object.

        Loads configuration from a dictionary.
        All parsing and loading happens at instantiation.

        Args:
            source: Configuration data to load as a dict.
        """
        self._rules = []
        self._reusable_nametemplates = {}
        self._options = {'DATETIME_FORMAT': {},
                         'FILETAGS_OPTIONS': {}}
        self._version = None
        self.referenced_meowuris = set()

        if not isinstance(source, dict):
            raise TypeError('Expected Configuration source to be type dict')

        self._load_from_dict(source)

        if self.version:
            if self.version != C.STRING_PROGRAM_VERSION:
                log.warning('Possible configuration compatibility mismatch!')
                log.warning('Loaded configuration created by {} (currently '
                            'running {})'.format(self.version,
                                                 C.STRING_PROGRAM_VERSION))
                log.info(
                    'The current recommended procedure is to move the '
                    'current config to a temporary location, re-run '
                    'the program so that a new template config file is '
                    'generated and then manually transfer rules to this file.'
                )

    @classmethod
    def from_file(cls, path):
        """
        Returns a new Configuration instantiated from data at a given path.

        Args:
            path: Path of the (YAML) file to read, as an "internal" bytestring.

        Returns:
            An instance of 'Configuration', created from the data at "path".

        Raises:
            EncodingBoundaryViolation: Argument "path" is not a bytestring.
            ConfigReadError: The configuration file could not be read.
            ConfigError: The configuration file is empty.
        """
        sanity.check_internal_bytestring(path)

        _loaded_data = config.load_yaml_file(path)
        if not _loaded_data:
            raise exceptions.ConfigError(
                'Read empty config: "{!s}"'.format(util.displayable_path(path))
            )

        return cls(_loaded_data)

    def _load_from_dict(self, data):
        if not data:
            raise exceptions.ConfigError('Attempted to load empty data')

        self._data = data
        self._load_reusable_nametemplates()
        self._load_template_fields()
        self._load_rules()
        self._load_options()
        self._load_version()

        # For Debugging/development only.
        _referenced_meowuris = sorted(self.referenced_meowuris)
        for _meowuri in _referenced_meowuris:
            log.debug('Configuration Rule referenced meowURI'
                      ' "{!s}"'.format(_meowuri))

    def write_to_disk(self, dest_path):
        # TODO: This method is currently unused. Remove?
        if os.path.exists(dest_path):
            raise FileExistsError
        else:
            config.write_yaml_file(dest_path, self._data)

    def _load_reusable_nametemplates(self):
        raw_templates = self._data.get('NAME_TEMPLATES')
        if not raw_templates:
            log.debug('Configuration does not contain any name reusable name '
                      'templates')
            return
        if not isinstance(raw_templates, dict):
            log.debug('Configuration templates is not of type dict')
            return

        validated = {}
        for raw_name, raw_templ in raw_templates.items():
            _error = 'Got invalid name template: "{!s}": {!s}"'.format(
                raw_name, raw_templ
            )
            name = types.force_string(raw_name)
            if not name:
                raise exceptions.ConfigurationSyntaxError(_error)

            templ = types.force_string(raw_templ)
            if not templ:
                raise exceptions.ConfigurationSyntaxError(_error)

            # Remove any non-breaking spaces in the name template.
            templ = util.remove_nonbreaking_spaces(templ)

            if NameFormatConfigFieldParser.is_valid_nametemplate_string(templ):
                validated[name] = templ
            else:
                raise exceptions.ConfigurationSyntaxError(_error)

        self._reusable_nametemplates.update(validated)

    def _load_template_fields(self):
        # TODO: [TD0036] Allow per-field replacements and customization.
        raw_templatefields = self._data.get('NAME_TEMPLATE_FIELDS')
        if not raw_templatefields:
            log.debug(
                'Configuration does not contain name template field options'
            )
            return
        if not isinstance(raw_templatefields, dict):
            log.warning('Name template field options is not of type dict')
            return

        for raw_field, raw_options in raw_templatefields.items():
            field = types.force_string(raw_field)
            if not field or not fields.is_valid_template_field(field):
                raise exceptions.ConfigurationSyntaxError(
                    'Invalid name template field: "{!s}"'.format(raw_field)
                )

            # User-defined names with lists of patterns.
            for repl, pat_list in raw_options.get('candidates', {}).items():
                _validated_candidates = []
                for _pat in pat_list:
                    try:
                        compiled_pat = re.compile(_pat, re.IGNORECASE)
                    except re.error:
                        log.warning(
                            'Malformed regular expression: "{!s}"'.format(_pat)
                        )
                    else:
                        log.debug(
                            'Added name template field pattern :: Match: "{!s}"'
                            ' Replace: "{!s}"'.format(_pat, repl)
                        )
                        _validated_candidates.append(compiled_pat)

                if _validated_candidates:
                    util.nested_dict_set(
                        self._options,
                        ['NAME_TEMPLATE_FIELDS', field, 'candidates', repl],
                        _validated_candidates
                    )

    def _load_rules(self):
        raw_rules = self._data.get('RULES')
        if not raw_rules:
            raise exceptions.ConfigError(
                'The configuration file does not contain any rules'
            )

        for raw_name, raw_contents in raw_rules.items():
            name = types.force_string(raw_name)
            if not name:
                log.error('Skipped rule with bad name: "{!s}"'.format(raw_name))
                continue

            raw_contents.update({'description': name})
            log.debug('Validating rule "{!s}" ..'.format(name))
            try:
                valid_rule = self.to_rule_instance(raw_contents)
            except exceptions.ConfigurationSyntaxError as e:
                log.error('Bad rule "{!s}"; {!s}'.format(name, e))
            else:
                log.debug('Validated rule "{!s}" .. OK!'.format(name))

                # Create and populate "Rule" objects with *validated* data.
                self._rules.append(valid_rule)

                # Keep track of all "meowURIs" referenced by rules.
                self.referenced_meowuris.update(
                    valid_rule.referenced_meowuris()
                )

    def _validate_name_format(self, _raw_name_format):
        _format = types.force_string(_raw_name_format)
        if not _format:
            return None

        # TODO: [TD0109] Allow arbitrary name template placeholder fields.

        # First test if the field data is a valid name template entry,
        if _format in self.reusable_nametemplates:
            # If it is, use the format string defined in that entry.
            return self.reusable_nametemplates.get(_format)
        else:
            # If not, check if it is a valid format string.
            if NameFormatConfigFieldParser.is_valid_nametemplate_string(_format):
                return _format

        return None

    def to_rule_instance(self, raw_rule):
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
        if 'NAME_FORMAT' not in raw_rule:
            raise exceptions.ConfigurationSyntaxError(
                'is missing name template format'
            )
        valid_format = self._validate_name_format(raw_rule.get('NAME_FORMAT'))
        if not valid_format:
            raise exceptions.ConfigurationSyntaxError(
                'uses invalid name template format'
            )
        name_template = util.remove_nonbreaking_spaces(valid_format)

        try:
            _rule = rules.Rule(description=raw_rule.get('description'),
                               exact_match=raw_rule.get('exact_match'),
                               ranking_bias=raw_rule.get('ranking_bias'),
                               name_template=name_template,
                               conditions=raw_rule.get('CONDITIONS'),
                               data_sources=raw_rule.get('DATA_SOURCES'))
        except exceptions.InvalidRuleError as e:
            raise exceptions.ConfigurationSyntaxError(e)
        else:
            return _rule

    def _load_options(self):
        def _try_load_datetime_format_option(option, default):
            if 'DATETIME_FORMAT' in self._data:
                _value = self._data['DATETIME_FORMAT'].get(option, None)
                if (_value is not None and
                        DateTimeConfigFieldParser.is_valid_datetime(_value)):
                    log.debug('Added datetime format option :: '
                              '{!s}: "{!s}"'.format(option, _value))
                    self._options['DATETIME_FORMAT'][option] = _value
                    return  # OK!

            # Use verified default value.
            if DateTimeConfigFieldParser.is_valid_datetime(default):
                log.debug('Using default datetime format option :: '
                          '{!s}: "{!s}"'.format(option, default))
                self._options['DATETIME_FORMAT'][option] = default
            else:
                sanity.check(
                    False,
                    'Invalid internal default value "{!s}: {!s}"'.format(
                        option, default)
                )

        def _try_load_filetags_option(option, default):
            if 'FILETAGS_OPTIONS' in self._data:
                _value = self._data['FILETAGS_OPTIONS'].get(option)
            else:
                _value = None
            if _value is not None:
                log.debug('Added filetags option :: '
                          '{!s}: "{!s}"'.format(option, _value))
                self._options['FILETAGS_OPTIONS'][option] = _value
            else:
                log.debug('Using default filetags option :: '
                          '{!s}: "{!s}"'.format(option, _value))
                self._options['FILETAGS_OPTIONS'][option] = default

        def _try_load_custom_postprocessing_option(option, default):
            if 'CUSTOM_POST_PROCESSING' in self._data:
                _value = self._data['CUSTOM_POST_PROCESSING'].get(option)
            else:
                _value = None
            if _value is not None:
                log.debug('Added post-processing option :: '
                          '{!s}: {!s}'.format(option, _value))
                util.nested_dict_set(
                    self._options, ['CUSTOM_POST_PROCESSING', option], _value
                )
            else:
                log.debug('Using default post-processing option :: '
                          '{!s}: {!s}'.format(option, default))
                util.nested_dict_set(
                    self._options, ['CUSTOM_POST_PROCESSING', option], default
                )

        def _try_load_custom_postprocessing_replacements():
            if 'CUSTOM_POST_PROCESSING' in self._data:
                _reps = self._data['CUSTOM_POST_PROCESSING'].get('replacements')
                if not _reps or not isinstance(_reps, dict):
                    return

                match_replace_pairs = []
                for regex, replacement in _reps.items():
                    _match = types.force_string(regex)
                    _replace = types.force_string(replacement)
                    if None in (_match, _replace):
                        log.warning('Skipped bad replacement: "{!s}": '
                                    '"{!s}"'.format(regex, replacement))
                        continue

                    try:
                        compiled_pat = re.compile(_match)
                    except re.error:
                        log.warning('Malformed regular expression: '
                                    '"{!s}"'.format(_match))
                    else:
                        log.debug(
                            'Added post-processing replacement :: Match: "{!s}"'
                            ' Replace: "{!s}"'.format(regex, replacement)
                        )
                        match_replace_pairs.append((compiled_pat, _replace))

                if match_replace_pairs:
                    util.nested_dict_set(
                        self._options,
                        ['CUSTOM_POST_PROCESSING', 'replacements'],
                        match_replace_pairs
                    )

        def _try_load_persistence_option(option, default):
            _value = None
            if 'PERSISTENCE' in self._data:
                try:
                    _value = self._data['PERSISTENCE'].get(option)
                except AttributeError:
                    pass

            if _value is not None:
                try:
                    _bytes_path = types.AW_PATH.normalize(_value)
                except types.AWTypeError as e:
                    _dp = util.displayable_path(_value)
                    log.error(
                        'Invalid cache directory "{!s}"; {!s}'.format(_dp, e)
                    )
                else:
                    _dp = util.displayable_path(_bytes_path)
                    log.debug('Added persistence option :: '
                              '{!s}: {!s}'.format(option, _dp))
                    util.nested_dict_set(
                        self._options, ['PERSISTENCE', option], _bytes_path
                    )
                    return

            _bytes_path = util.normpath(default)
            _dp = util.displayable_path(_bytes_path)
            log.debug('Using default persistence option :: '
                      '{!s}: {!s}'.format(option, _dp))
            util.nested_dict_set(
                self._options, ['PERSISTENCE', option], _bytes_path
            )

        _try_load_datetime_format_option(
            'date', C.DEFAULT_DATETIME_FORMAT_DATE
        )
        _try_load_datetime_format_option(
            'time', C.DEFAULT_DATETIME_FORMAT_TIME
        )
        _try_load_datetime_format_option(
            'datetime', C.DEFAULT_DATETIME_FORMAT_DATETIME
        )

        _try_load_filetags_option(
            'filename_tag_separator',
            C.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR
        )
        _try_load_filetags_option(
            'between_tag_separator',
            C.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR
        )
        _try_load_custom_postprocessing_option(
            'sanitize_filename',
            C.DEFAULT_FILESYSTEM_SANITIZE_FILENAME
        )
        _try_load_custom_postprocessing_option(
            'sanitize_strict',
            C.DEFAULT_FILESYSTEM_SANITIZE_STRICT
        )
        _try_load_custom_postprocessing_option(
            'lowercase_filename',
            C.DEFAULT_FILESYSTEM_LOWERCASE_FILENAME
        )
        _try_load_custom_postprocessing_option(
            'uppercase_filename',
            C.DEFAULT_FILESYSTEM_UPPERCASE_FILENAME
        )

        _try_load_custom_postprocessing_replacements()

        # Handle conflicting upper-case and lower-case options.
        if (self._options['CUSTOM_POST_PROCESSING'].get('lowercase_filename')
                and self._options['CUSTOM_POST_PROCESSING'].get('uppercase_filename')):

            log.warning('Conflicting options: "lowercase_filename" and '
                        '"uppercase_filename". Ignoring "uppercase_filename".')
            self._options['CUSTOM_POST_PROCESSING']['uppercase_filename'] = False

        # Unlike the previous options; first load the default ignore patterns,
        # then combine these defaults with any user-specified patterns.
        util.nested_dict_set(
            self._options, ['FILESYSTEM_OPTIONS', 'ignore'],
            C.DEFAULT_FILESYSTEM_IGNORE
        )
        if 'FILESYSTEM_OPTIONS' in self._data:
            _user_ignores = self._data['FILESYSTEM_OPTIONS'].get('ignore')
            if isinstance(_user_ignores, list):
                _user_ignores = util.filter_none(_user_ignores)
                if _user_ignores:
                    for _ui in _user_ignores:
                        log.debug('Added filesystem option :: '
                                  '{!s}: {!s}'.format('ignore', _ui))

                    _defaults = util.nested_dict_get(
                        self._options, ['FILESYSTEM_OPTIONS', 'ignore']
                    )
                    log.debug('Adding {} default filesystem ignore '
                              'patterns'.format(len(_defaults)))

                    _combined = _defaults.union(frozenset(_user_ignores))
                    log.debug('Using combined total of {} filesystem ignore '
                              'patterns'.format(len(_combined)))
                    util.nested_dict_set(
                        self._options, ['FILESYSTEM_OPTIONS', 'ignore'],
                        _combined
                    )

        _try_load_persistence_option(
            'cache_directory',
            C.DEFAULT_CACHE_DIR_ABSPATH
        )
        _try_load_persistence_option(
            'history_file_path',
            C.DEFAULT_HISTORY_FILE_ABSPATH
        )

    def _load_version(self):
        if 'COMPATIBILITY' in self._data:
            _raw_version = self._data['COMPATIBILITY'].get('autonameow_version')
            valid_version = parse_versioning(_raw_version)
            if valid_version:
                self._version = valid_version
                return
            else:
                log.debug('Read invalid version: "{!s}"'.format(_raw_version))

        log.error('Unable to read program version from configuration.')

    def get(self, key_list):
        try:
            return util.nested_dict_get(self._options, key_list)
        except KeyError:
            return None

    @property
    def version(self):
        """
        Returns:
            The version number of the program that wrote the configuration as
            a Unicode string, if it is available.  Otherwise None.
        """
        if self._version:
            return 'v' + '.'.join(map(str, self._version))
        else:
            return None

    @property
    def options(self):
        """
        Public interface for configuration options.
        Returns:
            Current and valid configuration options.
        """
        return self._options

    @property
    def data(self):
        """
        NOTE: Intended for debugging and testing!

        Returns:
            Raw configuration data as a dictionary.
        """
        return self._data

    @property
    def rules(self):
        if self._rules and len(self._rules) > 0:
            return self._rules
        else:
            return []

    @property
    def reusable_nametemplates(self):
        return self._reusable_nametemplates

    @property
    def name_templates(self):
        _rule_templates = [r.name_template for r in self.rules]
        _reusable_templates = [t for t in self.reusable_nametemplates.values()]
        return _rule_templates + _reusable_templates

    def __str__(self):
        out = ['Written by autonameow version v{}\n\n'.format(self.version)]

        for number, rule in enumerate(self.rules):
            out.append('Rule {}:\n'.format(number + 1))
            out.append(util.indent(str(rule), amount=4) + '\n')

        out.append('\nReusable Name Templates:\n')
        out.append(
            util.indent(util.dump(self.reusable_nametemplates), amount=4)
        )

        out.append('\nMiscellaneous Options:\n')
        out.append(util.indent(util.dump(self.options), amount=4))

        return ''.join(out)
