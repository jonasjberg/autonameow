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


class QueryResponseFailure(object):
    def __init__(self, fileobject=None, uri=None, msg=None):
        self.fileobject = fileobject
        self.uri = uri or 'unspecified MeowURI'
        self.msg = msg or ''

    def __repr__(self):
        if self.fileobject:
            str_fileobject = repr(self.fileobject)
        else:
            str_fileobject = '(Unknown FileObject)'

        if self.msg:
            _msg = ' :: {!s}'.format(self.msg)
        else:
            _msg = ''

        return '{}->[{!s}]{!s}'.format(str_fileobject, self.uri, _msg)

    def __str__(self):
        return 'Failed query ' + repr(self)

    def __bool__(self):
        return False
