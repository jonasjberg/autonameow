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

import datetime
import os
import sys

import core


STRING_PYTHON_VERSION = sys.version.replace('\n', '')

STRING_PROGRAM_VERSION_PREFIX = 'v'
STRING_PROGRAM_VERSION = '{}{}'.format(STRING_PROGRAM_VERSION_PREFIX,
                                       core.version.__version__)
STRING_PROGRAM_RELEASE_DATE = str(core.version.RELEASE_DATE)

STRING_PROGRAM_NAME = core.version.__title__.lower()
STRING_AUTHOR_EMAIL = str(core.version.__email__)
STRING_COPYRIGHT_NOTICE = str(core.version.__copyright__)
STRING_URL_MAIN = str(core.version.__url__)
STRING_URL_REPO = str(core.version.__url_repo__)


_this_dir = os.path.abspath(os.path.dirname(__file__))
_parent_dir = os.path.normpath(os.path.join(_this_dir, os.pardir))

# Absolute path to the autonameow source root directory.
# NOTE: Assumes running from source code (as per the original repository)
AUTONAMEOW_SRCROOT_DIR = os.path.realpath(os.path.join(_parent_dir, os.pardir))


# Color used to highlight post-processing replacements.
REPLACEMENT_HIGHLIGHT_COLOR = 'RED'
REPLACEMENT_SECONDARY_HIGHLIGHT_COLOR = 'LIGHTRED_EX'

# Used by command-line interface functions.
CLI_MSG_HEADING_CHAR = '='


# Each analyzer can be queried for these fields by calling either;
#   the_analyzer.get_FIELD()   or   the_analyzer.get('FIELD')
ANALYSIS_RESULTS_FIELDS = ['datetime', 'publisher', 'title', 'tags', 'author']


# Default file size in bytes, if the size can not be determined.
UNKNOWN_BYTESIZE = 0


# Fallback encoding.
DEFAULT_ENCODING = 'utf8'


# Default values for required configuration fields.
DEFAULT_RULE_RANKING_BIAS = 0.5
DEFAULT_RULE_DESCRIPTION = 'UNDESCRIBED'
DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR = ' -- '
DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR = ' '
DEFAULT_POSTPROCESS_SANITIZE_FILENAME = True
DEFAULT_POSTPROCESS_SANITIZE_STRICT = False
DEFAULT_POSTPROCESS_LOWERCASE_FILENAME = False
DEFAULT_POSTPROCESS_UPPERCASE_FILENAME = False
DEFAULT_POSTPROCESS_SIMPLIFY_UNICODE = True
DEFAULT_DATETIME_FORMAT_DATETIME = '%Y-%m-%dT%H%M%S'
DEFAULT_DATETIME_FORMAT_DATE = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT_TIME = '%H-%M-%S'


DEFAULT_FILESYSTEM_IGNORE_DARWIN = frozenset([
    # Metadata
    '*/.DS_Store',
    '*/.AppleDouble',
    '*/.LSOverride',

    # Thumbnails
    '*/._*',

    # Files that might appear in the root of a volume
    '*/.DocumentRevisions-V100',
    '*/.fseventsd',
    '*/.Spotlight-V100',
    '*/.TemporaryItems',
    '*/.Trashes',
    '*/.VolumeIcon.icns',
    '*/.com.apple.timemachine.donotpresent',

    # Directories potentially created on remote AFP share
    '*/.AppleDB',
    '*/.AppleDesktop',
    '*/Network Trash Folder',
    '*/Temporary Items',
    '*/.apdisk'
])

DEFAULT_FILESYSTEM_IGNORE_LINUX = frozenset([
    # Temporary/backup files
    '*~',

    # FUSE temporary files
    '*/.fuse_hidden*',

    # KDE directory preferences
    '*/.directory',

    # Trash directories found at partition/disk roots
    '*/.Trash-*',

    # Created by NFS when an open file is removed but is still being accessed
    '*/.nfs*'
])

DEFAULT_FILESYSTEM_IGNORE_WINDOWS = frozenset([
    # Shortcuts
    '*.lnk',

    # Folder configuration
    '*/Desktop.ini',

    # Thumbnail cache files
    '*/ehthumbs.db',
    '*/ehthumbs_vista.db',
    '*/Thumbs.db',

    # Recycle Bin used on file shares
    '*/$RECYCLE.BIN*'
])

DEFAULT_FILESYSTEM_IGNORE_VCS = frozenset([
    # Git
    '*/.git*', '*/.repo',

    # Mercurial
    '*/.hg', '*/.hgignore',

    # SVN
    '*/.svn', '*/.svnignore',

    # Microsoft TFS config
    '*/.tfignore',

    # Visual Source Safe
    '*/vssver.scc',

    # CVS
    '*/CVS', '*/.cvsignore', '*/RCS', '*/SCCS',

    # Monotone
    '*/_MTN',

    # Darcs
    '*/_darcs',
])


DEFAULT_FILESYSTEM_IGNORE = DEFAULT_FILESYSTEM_IGNORE_DARWIN.union(
    DEFAULT_FILESYSTEM_IGNORE_LINUX).union(
        DEFAULT_FILESYSTEM_IGNORE_WINDOWS).union(
            DEFAULT_FILESYSTEM_IGNORE_VCS)


def next_year():
    # http://stackoverflow.com/a/11206511
    _today = datetime.datetime.today()
    try:
        return _today.replace(year=_today.year + 1)
    except ValueError:
        # February 29th in a leap year
        # Add 365 days instead to arrive at March 1st
        return _today + datetime.timedelta(days=365)


# Ignore all date/time-information following the specified year (inclusive).
YEAR_UPPER_LIMIT = next_year()

# TODO: [TD0043] Allow storing these in the configuration file.
# Ignore all date/time-information for the specified year and years prior.
#
# Arbitrarily set to 1455 "The Gutenberg Bible (in Latin) was the first major
# book printed in Europe with movable metal type by Johannes Gutenberg."
YEAR_LOWER_LIMIT = datetime.datetime.strptime('1455', '%Y')


# Exit code values returned to the executing shell or parent process.
# Normal, successful termination should return "0" (EXIT_SUCCESS)
# Any non-zero value is interpreted as an error. Higher values should
# correspond to increasingly critical error conditions.
EXIT_SUCCESS = 0     # Program finished successfully.
EXIT_WARNING = 1     # Program execution completed but there were errors.
EXIT_ERROR = 2       # Program execution halted due to irrecoverable errors.
EXIT_SANITYFAIL = 3  # Program failure due to failed sanity check.


# Repository and internal data storage
MEOWURI_NODE_GENERIC = 'generic'
MEOWURI_UNDEFINED_PART = 'NULL'
MEOWURI_SEPARATOR = '.'
RE_ALLOWED_MEOWURI_PART_CHARS = r'[\w:-]'

MEOWURI_ROOT_SOURCE_ANALYZERS = 'analyzer'
MEOWURI_ROOT_SOURCE_EXTRACTORS = 'extractor'
MEOWURI_ROOT_GENERIC = 'generic'

MEOWURI_ROOTS_SOURCES = frozenset([
    MEOWURI_ROOT_SOURCE_ANALYZERS,
    MEOWURI_ROOT_SOURCE_EXTRACTORS,
])
MEOWURI_ROOTS = frozenset([MEOWURI_ROOT_GENERIC]).union(MEOWURI_ROOTS_SOURCES)


# Persistence and paths.
# TODO: [TD0107] FIX THIS!
DEFAULT_PERSISTENCE_DIR_ABSPATH = b'/tmp/autonameow_cache'
DEFAULT_HISTORY_FILE_BASENAME = b'prompt_history'
DEFAULT_HISTORY_FILE_ABSPATH = b'/tmp/autonameow_cache/prompt_history'
DEFAULT_CACHE_MAX_FILESIZE = 50 * 1024**2  # ~50MB
TEXT_EXTRACTOR_CACHE_MAX_FILESIZE = 50 * 1024**2  # ~50MB


# Extractor settings
# Used by the 'PandocMetadataExtractor' and the 'MarkdownTextExtractor'.
MARKDOWN_BASENAME_SUFFIXES = frozenset([b'md', b'markdown', b'mkd'])
EXTRACTOR_FIELDMETA_BASENAME_SUFFIX = '_fieldmeta.yaml'
