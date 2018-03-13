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


class AWAssertionError(AssertionError):
    """Error due to incorrect assumptions about internal interactions.
       Equivalent to assertions, intended to prevent bugs and regressions."""


class AutonameowException(Exception):
    """Base exception. All custom exceptions should subclass this."""


class DependencyError(AutonameowException):
    """Failed to import a required module or other dependency error."""
    def __init__(self, missing_modules=None):
        if missing_modules is not None:
            if not isinstance(missing_modules, list):
                missing_modules = [missing_modules]
            self.missing_modules = missing_modules
        else:
            self.missing_modules = None

    def __str__(self):
        msg = 'Missing required module(s): '
        if self.missing_modules:
            mods = sorted(set(self.missing_modules))
            msg += ' '.join(['"{!s}"'.format(m) for m in mods])
        else:
            msg += '(unspecified)'
        return msg


class EncodingBoundaryViolation(AWAssertionError):
    """Error due to unexpected string encoding."""


class InvalidFileArgumentError(AutonameowException):
    """The argument (file) is not suited for processing."""


class ConfigError(AutonameowException):
    """Base class for exceptions raised when querying a configuration."""


class NameBuilderError(AutonameowException):
    """An error occurred while constructing a name. Unable to proceed."""


class FilesystemError(AutonameowException):
    """Errors occured while reading/writing files on disk. Should be used by
    the filesystem abstraction layer as a catch-all for failed operations."""


class InvalidMeowURIError(ConfigError):
    """An error caused by an invalid "meowURI"."""


class NameTemplateSyntaxError(ConfigError):
    """The name format template is invalid."""
    pass


class ConfigurationSyntaxError(ConfigError):
    """The configuration contains invalid entries."""
    pass
