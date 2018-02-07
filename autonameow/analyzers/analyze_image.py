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

import re
from datetime import datetime

from analyzers import BaseAnalyzer
from util import dateandtime


# TODO: [TD0040] Add assigning tags to GPS coordinates.


class ImageAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.1
    HANDLES_MIME_TYPES = ['image/*']

    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.

    def __init__(self, fileobject, config, request_data_callback):
        super(ImageAnalyzer, self).__init__(
            fileobject, config, request_data_callback
        )

        self.text = None

    def analyze(self):
        # self.text = self.request_data(self.fileobject,
        #                               'extractor.text.ocr.full')

        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = _maybe_text

        # TODO: Run (text) analysis on any text produced by OCR.
        #       (I.E. extract date/time, titles, authors, etc.)

        self._add_results('datetime', self.get_datetime())

    def get_datetime(self):
        results = []
        exif_timestamps = self._get_exif_datetime()
        if exif_timestamps:
            results += exif_timestamps

        # TODO: Fix this here below.
        ocr_timestamps = self._get_ocr_datetime()
        if ocr_timestamps:
            results += ocr_timestamps

        return results if results else None

    def _request_exiftool_metadata(self, field):
        return self.request_data(self.fileobject,
                                 'extractor.metadata.exiftool.{}'.format(field))

    def _get_exif_datetime(self):
        """
        Extracts date and time information from the EXIF data.
        The EXIF data could be corrupted or contain non-standard entries.
        Extraction should be fault-tolerant and able to handle non-standard
        entry formats.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : 'datetimeoriginal',
                     'weight'  : 1
                   }, .. ]
        """
        # TODO: Recheck the weights. Should they even be defined here?
        DATE_TAG_FIELDS = [['EXIF:DateTimeOriginal', 1],
                           ['EXIF:DateTimeDigitized', 1],
                           ['EXIF:DateTimeModified', 0.5],
                           ['EXIF:CreateDate', 1],
                           ['EXIF:ModifyDate', 0.5],
                           ['EXIF:DateTime', 0.75]]
        results = []
        self.log.debug('Extracting date/time-information from EXIF-tags')
        for field, weight in DATE_TAG_FIELDS:
            dtstr = self._request_exiftool_metadata(field)
            if not dtstr:
                continue

            dt = None
            # Expected date format:         2016:04:07 18:47:30
            date_pattern = re.compile(
                r'.*(\d{4}:[01]\d:[0123]\d [012]\d:[012345]\d:[012345]\d).*')
            try:
                re_match = date_pattern.search(dtstr)
            except TypeError:
                self.log.debug('TypeError while matching: "{!s}"'.format(dtstr))
            else:
                datetime_str = re_match.group(1)
                try:
                    dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    self.log.debug(
                        'Unable to parse datetime: "{!s}"'.format(field)
                    )
            if dt:
                results.append({'value': dt,
                                'source': field,
                                'weight': weight})

        self.log.debug('Searching for GPS date/time-information in EXIF-tags')
        gps_date = self._request_exiftool_metadata('GPSDateStamp')
        gps_time = self._request_exiftool_metadata('GPSTimeStamp')

        if gps_date and gps_time:
            dt = None
            gps_time_str = ''
            for toup in gps_time:
                gps_time_str += str(toup[0])

            gps_datetime_str = gps_date + gps_time_str
            try:
                dt = datetime.strptime(gps_datetime_str, '%Y:%m:%d%H%M%S')
            except ValueError:
                self.log.debug('Unable to parse GPS datetime from: '
                               '"{!s}"'.format(gps_datetime_str))
            if dt:
                results.append({'value': dt,
                                'source': 'gpsdatetime',
                                'weight': 1})

        # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
        # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
        device_make = self._request_exiftool_metadata('Make')
        device_model = self._request_exiftool_metadata('Model')
        if device_make == 'OnePlus' and device_model == 'ONE E1003':
            bad_exif_date = datetime.strptime('20021208_120000',
                                              '%Y%m%d_%H%M%S')
            try:
                # if results['Exif_DateTimeDigitized'] == bad_exif_date:
                #     del results['Exif_DateTimeDigitized']
                # http://stackoverflow.com/a/1235631
                # TODO: FIX THIS! Currently does not pass anything if the bad
                #                 exif date is in the dict.
                results[:] = [d for d in results if
                              (d.get('source') == 'DateTimeDigitized' and
                               d.get('value') != bad_exif_date)]
            except KeyError:
                pass

        return results

    def _get_ocr_datetime(self):
        """
        Extracts date and time information from the text produced by OCR.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : 'ocr',
                     'weight'  : 0.1
                   }, .. ]
        """
        if not self.text:
            self.log.debug('Found no date/time-information in OCR text.')
            return None

        results = []
        text = self.text
        if isinstance(text, list):
            text = ' '.join(text)

        dt_regex = dateandtime.regex_search_str(text)
        if dt_regex:
            for e in dt_regex:
                results.append({'value': e,
                                'source': 'image_ocr_regex',
                                'weight': 0.25})

        text_split = text.split('\n')
        self.log.debug('Try getting datetime from text split by newlines')
        for t in text_split:
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                for e in dt_brute:
                    results.append({'value': e,
                                    'source': 'image_ocr_brute',
                                    'weight': 0.1})

            dt_ocr_special = dateandtime.special_datetime_ocr_search(t)
            if dt_ocr_special:
                results.append({'value': dt_ocr_special,
                                'source': 'image_ocr_special',
                                'weight': 0.25})

        if not results:
            self.log.debug('Found no date/time-information in OCR text.')
            return None
        return results

    @classmethod
    def check_dependencies(cls):
        return True
