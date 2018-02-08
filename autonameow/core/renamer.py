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

from core import (
    interactive,
    ui
)
from core.exceptions import FilesystemError
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
        sanity.check_internal_bytestring(dest_basename)
        log.debug('Destination basename (bytestring): "{!s}"'.format(
            enc.displayable_path(dest_basename)))

        from_basename = disk.file_basename(from_path)

        if self._basenames_are_equivalent(from_basename, dest_basename):
            self.stats['skipped'] += 1
            _msg = (
                'Skipped "{!s}" because the current name is the same as '
                'the new name'.format(enc.displayable_path(from_basename))
            )
            log.debug(_msg)
            ui.msg(_msg)
            return

        if self.mode_timid:
            log.debug('Timid mode enabled. Asking user to confirm ..')
            if not interactive.ask_confirm_rename(
                    enc.displayable_path(from_basename),
                    enc.displayable_path(dest_basename)):
                log.debug('Skipping rename following user response')
                return

        if self.dry_run:
            ui.msg_rename(from_basename, dest_basename, dry_run=self.dry_run)
            # TODO: Store number of dry-runs separately?

        self._rename_file(from_path, dest_basename)

    def _rename_file(self, from_path, dest_basename):
        # NOTE(jonas): Regression test runner monkey-patches this method.
        if self.dry_run:
            # TODO: [hack] Remove duplicated 'self.dry_run' test!
            log.debug('dry-run is enabled, skipping actual rename ..')
            return

        try:
            disk.rename_file(from_path, dest_basename)
        except (FileNotFoundError, FileExistsError, OSError) as e:
            # TODO: Failure count not handled by the regression test mock!
            self.stats['failed'] += 1
            raise FilesystemError(e)
        else:
            self.stats['renamed'] += 1

    def _basenames_are_equivalent(self, from_basename, dest_basename):
        return disk.compare_basenames(from_basename, dest_basename)
