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

from core.fileobject import eval_magic_glob


class Extractor(object):
    """
    Top-level abstract base class for all extractor classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting extractor classes.
    """

    # List of MIME types that this extractor can extract information from.
    # Example:  ['image/jpeg', 'application/pdf']
    handles_mime_types = None

    # Query string label for the data returned by this extractor.
    #    NOTE:  Must be defined in 'constants.VALID_DATA_SOURCES'!
    # Example:  'metadata.exiftool'
    data_query_string = None

    def __init__(self, source):
        """
        Creates a extractor instance acting on the specified source data.

        Args:
            source: Source of data from which to extract information.
        """
        self.source = source

    def query(self, field=None):
        """
        Queries the extractor for extracted data.

        Argument "field" is optional. All data is returned by default.

        Args:
            field: Optional refinement of the query.
                Expect format and type is defined by the extractor class.

        Returns:
            All data gathered by the extractor if no field is specified.
            Else the data matching the specified field.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def can_handle(cls, file_object):
        """
        Tests if this extractor class can handle the given file.

        The extractor is considered to be able to handle the given file if the
        file MIME type is listed in the class attribute 'handles_mime_types'.

        Inheriting extractor classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        the given file object.

        Args:
            file_object: The file to test as an instance of 'FileObject'.

        Returns:
            True if the extractor class can extract data from the given file,
            else False.
        """
        if eval_magic_glob(file_object.mime_type, cls.handles_mime_types):
            return True
        else:
            return False

    @classmethod
    def __str__(cls):
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
