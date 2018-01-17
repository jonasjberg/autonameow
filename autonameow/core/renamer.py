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

from core import ui
from core.exceptions import AutonameowException
from util import encoding as enc
from util import (
    disk,
    sanity
)


log = logging.getLogger(__name__)


class FileRenamer(object):
    def __init__(self, dry_run, mode_timid):
        """
        Creates a new renamer instance for use during by one program instance.

        Args:
            dry_run: Controls whether the renaming is actually performed.
            mode_timid: Require user confirmation before every rename.
        """
        self.dry_run = bool(dry_run)
        self.mode_timid = bool(mode_timid)

        self.stats = {
            'failed': 0,
            'skipped': 0,
            'renamed': 0,
        }

    def do_rename(self, from_path, new_basename):
        """
        Renames a file at the given path to the specified basename.

        If the basenames of the file at "from_path" and "new_basename" are
        equal, the renaming operation is skipped and True is returned.

        Args:
            from_path: Path to the file to rename as an "internal" byte string.
            new_basename: The new basename for the file as a Unicode string.

        Returns:
            True if the rename succeeded or would be a NO-OP, otherwise False.
        """
        # TODO: [TD0143] Add option to execute "hooks" at certain events.
        # TODO: [TD0092] Add storing history and ability to "undo" renames.
        sanity.check_internal_bytestring(from_path)
        sanity.check_internal_string(new_basename)

        # Encoding boundary.  Internal str --> internal filename bytestring
        dest_basename = enc.bytestring_path(new_basename)
        log.debug('Destination basename (bytestring): "{!s}"'.format(
            enc.displayable_path(dest_basename)))
        sanity.check_internal_bytestring(dest_basename)

        from_basename = disk.file_basename(from_path)

        if disk.compare_basenames(from_basename, dest_basename):
            self.stats['skipped'] += 1
            _msg = (
                'Skipped "{!s}" because the current name is the same as '
                'the new name'.format(enc.displayable_path(from_basename),
                                      enc.displayable_path(dest_basename))
            )
            log.debug(_msg)
            ui.msg(_msg)
        else:
            self.stats['renamed'] += 1
            if not self.dry_run:
                # TODO: [TD0155] Implement "timid mode".
                try:
                    disk.rename_file(from_path, dest_basename)
                except (FileNotFoundError, FileExistsError, OSError) as e:
                    self.stats['failed'] += 1
                    log.error('Rename FAILED: {!s}'.format(e))
                    raise AutonameowException

            ui.msg_rename(from_basename, dest_basename, dry_run=self.dry_run)
