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

import logging as log

import analyzers
import extractors
import plugins
from core import (
    exceptions,
    util
)


class Repository(object):
    def __init__(self):
        self.data = {}
        self.meowuri_class_map = {}
        self.mapped_meowuris = set()

    def initialize(self):
        self.meowuri_class_map = meowuri_class_map_dict()
        # self._log_string_class_map()

        self.mapped_meowuris = unique_map_meowuris(
            self.meowuri_class_map
        )

    def _log_string_class_map(self):
        pass
        # for key in self.meowuri_class_map.keys():
        #     for meowuri, klass in self.meowuri_class_map[key].items():
        #         print('Mapped meowURI "{!s}" to <{!s}> ({!s})'.format(
        #             meowuri, klass, key))

    def store(self, file_object, meowuri, data):
        """
        Collects data. Should be passed to "non-core" components as a callback.

        Adds data related to a given 'file_object', at a storage location
        defined by the given 'meowuri'.

            STORAGE = {
                'file_object_A': {
                    'meowuri_a': [1, 2]
                    'meowuri_b': ['foo']
                }
                'file_object_B': {
                    'meowuri_a': ['bar']
                    'meowuri_b': [2, 1]
                }
            }

        If argument "data" is a dictionary, it is "flattened" here.
        Example:

          Incoming arguments:
          LABEL: 'metadata.exiftool'     DATA: {'a': 'b', 'c': 'd'}

          Would be "flattened" to:
          LABEL: 'metadata.exiftool.a'   DATA: 'b'
          LABEL: 'metadata.exiftool.c'   DATA: 'd'

        """
        if not meowuri:
            raise exceptions.InvalidDataSourceError(
                'Missing required argument "meowuri"'
            )
        if not isinstance(meowuri, str):
            raise exceptions.InvalidDataSourceError(
                'Argument "meowuri" must be of type str'
            )

        if data is None:
            log.warning('Attempted to add None data with meowURI'
                        ' "{!s}"'.format(meowuri))
            return

        if isinstance(data, dict):
            flat_data = util.flatten_dict(data)
            for k, v in flat_data.items():
                merged_meowuri = meowuri + '.' + str(k)
                self._store(file_object, merged_meowuri, v)
        else:
            self._store(file_object, meowuri, data)

    def _store(self, file_object, meowuri, data):
        try:
            any_existing = util.nested_dict_get(self.data,
                                                [file_object, meowuri])
        except KeyError:
            pass
        else:
            if any_existing is not None:
                assert(not isinstance(data, list))
                data = [any_existing] + [data]

        util.nested_dict_set(self.data, [file_object, meowuri], data)
        log.debug('Repository stored: {{"{!s}": {{"{!s}": {!s}}}}}'.format(
            file_object, meowuri, data
        ))

    def resolve(self, file_object, meowuri):
        if not meowuri:
            raise exceptions.InvalidDataSourceError(
                'Unable to resolve empty meowURI'
            )

        try:
            d = util.nested_dict_get(self.data, [file_object, meowuri])
        except KeyError as e:
            log.debug('Repository request raised KeyError: {!s}'.format(e))
            return None
        else:
            return d

    def resolvable(self, meowuri):
        if not meowuri:
            return False

        resolvable = list(self.mapped_meowuris)
        if any([meowuri.startswith(r) for r in resolvable]):
            return True
        return False

    def __len__(self):
        return util.count_dict_recursive(self.data)

    def __str__(self):
        out = []
        for file_object, data in self.data.items():
            out.append('FileObject basename: "{!s}"'.format(file_object))
            _abspath = util.displayable_path(file_object.abspath)
            out.append('FileObject absolute path: "{!s}"'.format(_abspath))
            out.append('')

            # TODO: [TD0066] Handle all encoding properly.
            temp = {}
            for key, value in data.items():
                if isinstance(value, bytes):
                    temp[key] = util.displayable_path(value)
                else:
                    temp[key] = value

                # Often *a lot* of text, trim to arbitrary size..
                if key == 'contents.textual.raw_text':
                    temp[key] = truncate_text(temp[key])

            expanded = util.expand_meowuri_data_dict(temp)
            out.append(util.dump(expanded))
            out.append('\n')

        return '\n'.join(out)

    def __repr__(self):
        out = {}

        for key, value in self.data.items():
            # TODO: [TD0066] Handle all encoding properly.
            if isinstance(value, bytes):
                out[key] = util.displayable_path(value)
            else:
                out[key] = value

        return out


def truncate_text(text, number_chars=500):
    msg = '  (.. TRUNCATED to {}/{} characters)'.format(number_chars, len(text))
    return text[0:number_chars] + msg


def meowuri_class_map_dict():
    # The 'MeowURIClassMap' attributes in non-core modules keep
    # references to the available component classes.
    # These are dicts with keys being the "meowURIs" that the respective
    # component uses when storing data and the contained values are lists of
    # classes mapped to the "meowURI".
    _meowuri_class_map = {
        'extractors': extractors.MeowURIClassMap,
        'analyzers': analyzers.MeowURIClassMap,
        'plugins': plugins.MeowURIClassMap
    }
    return _meowuri_class_map


def unique_map_meowuris(meowuri_class_map):
    out = set()

    # for key in ['extractors', 'analyzers', 'plugins']:
    for key in meowuri_class_map.keys():
        for meowuri, _ in meowuri_class_map[key].items():
            assert not (isinstance(meowuri, list))
            out.add(meowuri)

    return out


SessionRepository = Repository()
SessionRepository.initialize()
