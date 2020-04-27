# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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
import time

from vendor import isbnlib


log = logging.getLogger(__name__)


class ISBNMetadataService(object):
    def __init__(self):
        # TODO: Limit number of requests within fixed time windows.
        self.available = True

    def query(self, isbn_number):
        if not self.available:
            return None

        return self._query(isbn_number)

    def _query(self, isbn_number):
        logging.disable(logging.DEBUG)

        try:
            return isbnlib.meta(isbn_number)
        except isbnlib.NotValidISBNError as e:
            log.error('Metadata query FAILED for ISBN "%s"', isbn_number)
            log.debug(str(e))
        except Exception as e:
            # TODO: [TD0132] Improve blacklisting failed requests..
            # NOTE: isbnlib does not expose all exceptions.
            # We should handle 'ISBNLibHTTPError' ("with code 403 [Forbidden]")
            log.error(e)
        finally:
            # Tiny sleep to maybe avoid getting blocked by the service ..
            time.sleep(0.2)
            logging.disable(logging.NOTSET)

        return None


ISBN_METADATA_SERVICE = ISBNMetadataService()
