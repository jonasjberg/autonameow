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

import sys
from datetime import (
    datetime,
    timedelta
)

from core import (
    util,
    version
)

PYTHON_VERSION = sys.version.replace('\n', '')
PROGRAM_VERSION = 'v{}'.format(version.__version__)


# Each analyzer can be queried for these fields by calling either;
#   the_analyzer.get_FIELD()   or   the_analyzer.get('FIELD')
ANALYSIS_RESULTS_FIELDS = ['datetime', 'publisher', 'title', 'tags', 'author']


# Legal name template fields are defined here.
# These are used when constructing the file names and for unit tests.
NAME_TEMPLATE_FIELDS = (
    ANALYSIS_RESULTS_FIELDS + ['date', 'description', 'edition', 'extension']
)

# File "magic" MIME type lookup table keyed by shorthand. Each value is a
# list of file MIME types that is classified for that particular shorthand.
MAGIC_TYPE_LOOKUP = {'bmp':   ['image/x-ms-bmp'],
                     'gif':   ['image/gif'],
                     'jpg':   ['image/jpeg'],
                     'mov':   ['video/quicktime'],
                     'mp4':   ['video/mp4'],
                     'ogg':   ['video/ogg'],
                     'pdf':   ['application/pdf'],
                     'png':   ['image/png'],
                     'txt':   ['text/plain'],
                     'empty': ['inode/x-empty']}

# Default MIME type string used if the MIME type detection fails.
MAGIC_TYPE_UNKNOWN = 'MIME_UNKNOWN'

# Default values for required configuration fields.
DEFAULT_RULE_RANKING_BIAS = 0.5
DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR = ' -- '
DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR = ' '
DEFAULT_FILESYSTEM_SANITIZE_FILENAME = True
DEFAULT_FILESYSTEM_SANITIZE_STRICT = False

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
    _today = datetime.today()
    try:
        return _today.replace(year=_today.year + 1)
    except ValueError:
        # February 29th in a leap year
        # Add 365 days instead to arrive at March 1st
        return _today + timedelta(days=365)


# Ignore all date/time-information following the specified year (inclusive).
YEAR_UPPER_LIMIT = next_year()

# TODO: [TD0043] Allow storing these in the configuration file.
# Ignore all date/time-information for the specified year and years prior.
YEAR_LOWER_LIMIT = datetime.strptime('1900', '%Y')


# Exit code values returned to the executing shell or parent process.
# Normal, successful termination should return "0" (EXIT_SUCCESS)
# Any non-zero value is interpreted as an error. Higher values should
# correspond to increasingly critical error conditions.
EXIT_SUCCESS = 0    # Program finished successfully.
EXIT_WARNING = 1    # Program execution completed but there were errors.
EXIT_ERROR = 2      # Program execution halted due to irrecoverable errors.
