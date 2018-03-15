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

try:
    import isbnlib
except ImportError:
    isbnlib = None
    # TODO: [hack] Handle missing 'isbnlib' module properly!
    _isbnlib_NotValidISBNError = Exception
else:
    _isbnlib_NotValidISBNError = isbnlib.NotValidISBNError

from util import sanity


log = logging.getLogger(__name__)


# TODO: [TD0182] Isolate third-party metadata services like 'isbnlib'.


def _isbnlib_meta(isbnlike):
    assert isbnlib
    # TODO: [TD0182] Clean this up. Handle missing 'isbnlib' properly.
    return isbnlib.meta(isbnlike)


def _isbnlib_get_isbnlike(text):
    assert isbnlib
    # TODO: [TD0182] Clean this up. Handle missing 'isbnlib' properly.
    return isbnlib.get_isbnlike(text)


def _isbnlib_get_canonical_isbn(isbnlike):
    assert isbnlib
    # TODO: [TD0182] Clean this up. Handle missing 'isbnlib' properly.
    return isbnlib.get_canonical_isbn(isbnlike)


def _isbnlib_clean(isbnlike):
    assert isbnlib
    # TODO: [TD0182] Clean this up. Handle missing 'isbnlib' properly.
    return isbnlib.clean(isbnlike)


def _isbnlib_notisbn(isbnlike):
    assert isbnlib
    # TODO: [TD0182] Clean this up. Handle missing 'isbnlib' properly.
    return isbnlib.notisbn(isbnlike)


def extract_isbnlike_from_text(text):
    sanity.check_internal_string(text)

    possible_isbns = _isbnlib_get_isbnlike(text)
    if possible_isbns:
        return [_isbnlib_get_canonical_isbn(i)
                for i in possible_isbns if validate_isbn(i)]
    return list()


def validate_isbn(possible_isbn):
    if not possible_isbn:
        return None

    sanity.check_internal_string(possible_isbn)

    isbn_number = _isbnlib_clean(possible_isbn)
    if not isbn_number or _isbnlib_notisbn(isbn_number):
        return None
    return isbn_number


class ISBNMetadataService(object):
    def __init__(self):
        # TODO: [TD0182] Clean this up. Handle missing 'isbnlib' properly.
        self.available = bool(isbnlib)

    def query(self, isbn_number):
        if not self.available:
            return None
        return self._query(isbn_number)

    def _query(self, isbn_number):
        logging.disable(logging.DEBUG)

        try:
            return _isbnlib_meta(isbn_number)
        except _isbnlib_NotValidISBNError as e:
            log.error(
                'Metadata query FAILED for ISBN: "{}"'.format(isbn_number)
            )
            log.debug(str(e))
        except Exception as e:
            # TODO: [TD0132] Improve blacklisting failed requests..
            # NOTE: isbnlib does not expose all exceptions.
            # We should handle 'ISBNLibHTTPError' ("with code 403 [Forbidden]")
            log.error(e)
        finally:
            logging.disable(logging.NOTSET)

        return None


def fetch_isbn_metadata(isbn_number):
    isbn_metadata_service = ISBNMetadataService()
    return isbn_metadata_service.query(isbn_number)

