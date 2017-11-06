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

import unit_utils as uu


class AutonameowWrapper(object):
    def __init__(self, opts=None):
        if opts:
            assert isinstance(opts, dict)
            self.opts = opts
        else:
            self.opts = {}

        self.exit_code = None
        self.captured_stderr = None
        self.captured_stdout = None

    def mock_exit_program(self, exit_code):
        self.exit_code = exit_code

    def __call__(self):
        from core.autonameow import Autonameow
        Autonameow.exit_program = self.mock_exit_program

        with uu.capture_stdout() as stdout, uu.capture_stderr() as stderr:
            with Autonameow(self.opts) as ameow:
                ameow.run()

        self.captured_stdout = stdout.getvalue()
        self.captured_stderr = stderr.getvalue()
