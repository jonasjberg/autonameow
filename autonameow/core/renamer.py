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

from core.exceptions import FilesystemError
from util import disk
from util import encoding as enc
from util import sanity


log = logging.getLogger(__name__)


# TODO: [TD0143] Add option to execute "hooks" at certain events.
# TODO: [TD0092] Add storing history and ability to "undo" renames.


class FilenameDelta(object):
    def __init__(self, from_path, new_basename):
        self.from_path = from_path
        self.new_basename = new_basename

        self.displayable_old = self._get_displayable_from_path_basename()
        self.displayable_new = self._get_displayable_new_basename()

    def _get_displayable_from_path_basename(self):
        from_basename = disk.basename(self.from_path)
        sanity.check_internal_bytestring(from_basename)
        return enc.displayable_path(from_basename)

    def _get_displayable_new_basename(self):
        # TODO: Is this unnecessary round-tripping?
        new_basename = enc.bytestring_path(self.new_basename)
        sanity.check_internal_bytestring(new_basename)
        return enc.displayable_path(new_basename)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.from_path == other.from_path
                and self.new_basename == other.new_basename
            )
        return False

    def __hash__(self):
        return hash((self.from_path, self.new_basename))

    def __repr__(self):
        return '"{!s}" -> "{!s}"'.format(self.displayable_old,
                                         self.displayable_new)


class FileRenamer(object):
    def __init__(self, dry_run, timid):
        """
        Creates a new renamer instance for use by one program instance.

        Example usage with a "timid" renamer:

            renamer = FileRenamer(dry_run=True, timid=True)
            renamer.add_pending(b'/foo/bar', 'baz')
            if renamer.needs_confirmation:
                for filename_delta in renamer.needs_confirmation:
                    renamer.confirm(filename_delta)
            renamer.do_renames()

        Example usage with a renamer that does not require confirmation:

            renamer = FileRenamer(dry_run=True, timid=False)
            renamer.add_pending(b'/foo/bar', 'baz')
            renamer.do_renames()

        Args:
            timid: If True, pending renames will have to be confirmed
                   in order to be renamed when calling 'do_rename()'.
            dry_run: Controls whether the renaming is actually performed.
        """
        self.dry_run = bool(dry_run)
        self.timid = bool(timid)

        self.stats = {
            'failed': 0,
            'skipped': 0,
            'renamed': 0,
        }
        self._skipped = list()
        self._needs_confirmation = list()
        self._pending = list()

    @property
    def skipped(self):
        """
        NOTE: Skipped files are removed from the list of skipped files!
        Returns: Files that will not be renamed as instances of 'FilenameDelta'.
        """
        while self._skipped:
            yield self._skipped.pop()

    @property
    def pending(self):
        """
        Returns: Files that will be renamed when calling 'do_rename()'
                 as instances of 'FilenameDelta'.
        """
        yield from self._pending

    @property
    def needs_confirmation(self):
        """
        Returns: Files that need confirmation in order to be renamed when
                 calling 'do_rename()', as instances of 'FilenameDelta'.
        """
        yield from self._needs_confirmation

    def _add_skipped(self, from_path, new_basename):
        self.stats['skipped'] += 1
        self._skipped.append(FilenameDelta(from_path, new_basename))

    def _add_pending(self, from_path, new_basename):
        self._pending.append(FilenameDelta(from_path, new_basename))

    def _add_need_confirmation(self, from_path, new_basename):
        self._needs_confirmation.append(FilenameDelta(from_path, new_basename))

    def add_pending(self, from_path, new_basename):
        """
        Adds a new file renaming operation.

        The file is not actually renamed until 'do_renames()' is called.
        If 'timid' is True, the file must be confirmed in order to be renamed
        when calling 'do_renames()'.
        If the current file basename is the same as the new basename, the file
        will not be renamed when calling 'do_renames()'.

        Args:
            from_path: Path to the file to rename as an "internal" byte string.
            new_basename: The new basename for the file as a Unicode string.
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

        from_basename = disk.basename(from_path)
        sanity.check_internal_bytestring(from_basename)

        if self._basenames_are_equivalent(from_basename, dest_basename):
            self._add_skipped(from_path, dest_basename)
        elif self.timid:
            self._add_need_confirmation(from_path, dest_basename)
        else:
            self._add_pending(from_path, dest_basename)

    def confirm(self, filename_delta):
        """
        Confirm that a file should be renamed when calling 'do_rename()'.

        Args:
            filename_delta: File to confirm as an instance of 'FilenameDelta'.
        """
        assert filename_delta in self._needs_confirmation, (
            '{!s} does not need to be confirmed'.format(filename_delta)
        )
        self._needs_confirmation.remove(filename_delta)
        self._pending.append(filename_delta)

    def reject(self, filename_delta):
        """
        Opposite of 'confirm()', do NOT rename file when calling 'do_rename()'.

        Args:
            filename_delta: File to reject as an instance of 'FilenameDelta'.
        """
        assert filename_delta in self._needs_confirmation, (
            '{!s} does not need to be confirmed'.format(filename_delta)
        )
        self._needs_confirmation.remove(filename_delta)

    def do_renames(self):
        """
        Rename the (confirmed if "timid") pending files.

        Raises:
            FilesystemError: The file could not be successfully renamed.
        """
        for filename_delta in self._pending:
            self._rename_file(filename_delta.from_path,
                              filename_delta.new_basename)
            self._pending.remove(filename_delta)

    def _rename_file(self, from_path, dest_basename):
        # NOTE(jonas): Regression test runner monkey-patches this method.
        if self.dry_run:
            # TODO: [hack] Remove duplicated 'self.dry_run' test!
            log.debug('dry-run is enabled, skipping actual rename ..')
            return

        try:
            disk.rename_file(from_path, dest_basename)
        except FilesystemError:
            # TODO: Failure count not handled by the regression test mock!
            self.stats['failed'] += 1
            raise
        except FileExistsError as e:
            # TODO: Failure count not handled by the regression test mock!
            # TODO: [TD0164][TD0193] Clean this up!
            self.stats['failed'] += 1
            raise FilesystemError(e)
        except FileNotFoundError as e:
            # TODO: Failure count not handled by the regression test mock!
            # TODO: [TD0164][TD0193] Clean this up!
            self.stats['failed'] += 1
            raise FilesystemError(e)
        else:
            self.stats['renamed'] += 1

    def _basenames_are_equivalent(self, from_basename, dest_basename):
        return disk.compare_basenames(from_basename, dest_basename)
