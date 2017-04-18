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
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

from core.fileobject import FileObject


class NameBuilder(object):
    """
    Builds a new filename for a FileObject from a set of rules.
    The 'rule' contains a 'new_name_template', which is filled out with data
    from 'analysis_results'.
    The rule also specifies which data from 'analysis_results' is to be used.
    """
    def __init__(self, file_object, analysis_results, rule):
        assert isinstance(file_object, FileObject)
        # assert isinstance(analysis_results, dict)
        # assert isinstance(rule, dict)

        self.file_object = file_object
        self.analysis_results = analysis_results
        self.rule = rule
        self.fields = None

        self.new_name = None

    def _populate_fields(self, analysis_results, rule):
        """
        Assembles a dict with keys matching the fields in the new name template
        defined in the rule. The dict values come from the analysis results,
        which ones is also defined in the rule.
        :param analysis_results:
        :return:
        """

        def get_field_by_alias(field, alias):
            logging.debug('Trying to get "field" by "alias": '
                          '[{}] [{}]'.format(field, alias))
            for key in analysis_results[field]:
                if analysis_results[field][key]:
                    for result in analysis_results[field][key]:
                        if result['source'] == alias:
                            return result['value']
                        else:
                            logging.debug('NOPE -- result["source"] == {'
                                          '}'.format(result['source']))
                else:
                    return None

        ardate = artime = artags = artitle = None
        try:
            ardate = get_field_by_alias('datetime', rule['prefer_datetime'])
            artitle = get_field_by_alias('title', rule['prefer_title'])
            arauthor = get_field_by_alias('author', rule['prefer_author'])
            arpublisher = get_field_by_alias('publisher', rule['prefer_publisher'])
        except TypeError:
            pass

        if artime:
            artime.strftime('%H%M%S')
        if ardate:
            ardate = ardate.strftime('%Y-%m-%d')

        populated_fields = {
            'author': arauthor or None,
            'date': ardate or None,
            'description': artitle or None,
            'publisher': arpublisher or None,
            'title': artitle or None,
            'tags': artags or None,
            'ext': os.path.extsep + self.file_object.filenamepart_ext
        }
        return populated_fields

    def _fill_template(self, populated_fields, rule):
        # TODO: Finish this method. Very much a work in progress.
        if populated_fields is not None:
            return rule['new_name_template'] % populated_fields
        else:
            return None

    def build(self):
        self.fields = self._populate_fields(self.analysis_results, self.rule)
        self.new_name = self._fill_template(self.fields, self.rule)
        print('-' * 78)
        print('Automagic generated name: "{}"'.format(self.new_name))
