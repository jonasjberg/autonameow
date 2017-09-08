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

import yaml


class AutonameowException(Exception):
    """Base exception. All custom exceptions should subclass this."""


class InvalidFileArgumentError(AutonameowException):
    """The argument (file) is not suited for processing."""


class ConfigError(AutonameowException):
    """Base class for exceptions raised when querying a configuration."""


class AutonameowPluginError(AutonameowException):
    """A plugin encountered an unrecoverable error."""


class AnalysisResultsFieldError(AutonameowException):
    """Attempt to query/access an invalid analyzer data field."""


class InvalidDataSourceError(AutonameowException):
    """Attempt to use an invalid data source."""


class NameBuilderError(AutonameowException):
    """An error occurred while constructing a name. Unable to proceed."""


class RuleMatcherError(AutonameowException):
    """An error occurred while matching rules. Unable to proceed."""


class InvalidMeowURIError(ConfigError):
    """An error caused by an invalid "meowURI"."""


class RulePriorityError(ConfigError):
    """Failed to prioritize rules. Rule comparison failed."""


class NameTemplateSyntaxError(ConfigError):
    """The name format template is invalid."""
    pass


class ConfigurationSyntaxError(ConfigError):
    """The configuration contains invalid entries."""
    pass


class InvalidRuleError(ConfigError):
    """The Rule is in a bad state. The Rule state should only be set
    with known good data. This error implies data validation has failed."""


YAML_TAB_PROBLEM = "found character '\\t' that cannot start any token"


class ConfigReadError(ConfigError):
    """A configuration file could not be read."""
    def __init__(self, filename, reason=None):
        self.filename = filename
        self.reason = reason

        message = u'file {0} could not be read'.format(filename)
        if (isinstance(reason, yaml.scanner.ScannerError)
                and reason.problem == YAML_TAB_PROBLEM):
            # Special-case error message for tab indentation in YAML markup.
            message += u': found tab character at line {0}, column {1}'.format(
                reason.problem_mark.line + 1,
                reason.problem_mark.column + 1,
            )
        elif reason:
            # Generic error message uses exception's message.
            message += u': {0}'.format(reason)

        super(ConfigReadError, self).__init__(message)


class ConfigWriteError(ConfigError):
    """A configuration file could not be written."""
