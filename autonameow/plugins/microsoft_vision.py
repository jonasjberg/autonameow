#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Written in 2017 by Jonas Sjöberg
#   http://www.jonasjberg.com
#   https://github.com/jonasjberg
#   _____________________________________________________________________
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   _____________________________________________________________________

# Source repo:  https://github.com/jonasjberg/image-utils
# Commit hash:  2972dae5df58b335e80244ab176d38281d49171e

# This is me playing around with the Microsoft Vision API on a friday night.

import os
import json

from urllib.parse import urlencode
import http.client as httplib

from core import (
    util,
    fields,
    types
)
from extractors import ExtractedData
from plugins import BasePlugin
from core.exceptions import AutonameowPluginError


def query_api(image_file, api_key):
    """
    Queries the Microsoft Vision API with a given image.

    :param image_file: Path to the image file used in the query.
    :return: The API JSON data response.
    """
    if not api_key:
        # log.error('Unable to continue without an API key!')
        return None

    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': api_key,
    }

    params = urlencode({
        'maxCandidates': '1',
    })

    content = open(image_file, 'rb')
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/vision/v1.0/describe?%s" % params, content,
                     headers)
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        json_data = json.loads(response_data)
        conn.close()
        return json_data

    except Exception as e:
        # log.error('[ERROR] Caught exception when querying the API;')
        # if e:
        #     log.error(str(e))
        return None


def get_caption_text(json_data):
    """
    Extracts the caption text from the JSON response.

    :param json_data: API JSON response.
    :return: The image caption text.
    """
    try:
        caption = json_data['description']['captions'][0]['text']
    except KeyError as e:
        # log.error('[ERROR] Unable to get caption text: ', str(e))
        pass
    else:
        return caption


def get_tags(json_data, count=None):
    """
    Returns a specified number of tags from the JSON response.

    NOTE:  Added after integration into autonameow.

    Args:
        json_data: API JSON response.
        count: Number of tags to return.

    Returns:
        The specified number of tags, or all tags if no count is specified.

    """
    if count:
        try:
            count = int(count)
        except TypeError:
            count = None
        else:
            if count < 0:
                raise ValueError
    try:
        tags = json_data['description']['tags']
    except KeyError as e:
        # log.error('[ERROR] Unable to get tags: ', str(e))
        pass
    else:
        if count and len(tags) > count:
            return tags[:count]
        else:
            return tags


def _read_api_key_from_file(file_path):
    try:
        with open(file_path, mode='r', encoding='utf8') as f:
            api_key = f.read()
            return api_key.strip()
    except OSError:
        return None


class MicrosoftVisionPlugin(BasePlugin):
    meowuri_root = 'plugin.microsoft_vision'
    DISPLAY_NAME = 'MicrosoftVision'

    """
    'microsoft_vision.py'
    =====================
    Queries the Microsoft Vision API with images for information about visual
    content found in the image.

    Requires a Microsoft Visual API key, available for free at:
      <https://www.microsoft.com/cognitive-services/en-us/sign-up>

    Add your API key to the file 'microsoft_vision.key' in this directory,
    or modify the line below to point to the file containing your API key.
    """
    api_key_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), 'microsoft_vision.key'
    )
    API_KEY = _read_api_key_from_file(api_key_path)

    def __init__(self):
        super(MicrosoftVisionPlugin, self).__init__(
            display_name=self.DISPLAY_NAME
        )

    @classmethod
    def test_init(cls):
        return cls.API_KEY is not None

    def can_handle(self, file_object):
        _mime_type = self.request_data(file_object,
                                       'filesystem.contents.mime_type')
        return util.eval_magic_glob(_mime_type, ['image/png', 'image/jpeg'])

    def execute(self, file_object):
        _source_path = self.request_data(file_object, 'filesystem.abspath.full')
        if _source_path is None:
            raise AutonameowPluginError('Required data unavailable')

        response = query_api(_source_path, self.API_KEY)
        if not response:
            raise AutonameowPluginError('Did not receive a valid response')

        if 'statusCode' in response:
            if response['statusCode'] == 401:
                raise AutonameowPluginError(
                    'Error: {!s}'.format(
                        response.get('message',
                                     'Status code 401 (Access denied)')
                    )
                )

        _caption = get_caption_text(response)
        self.log.debug('Returning caption: "{!s}"'.format(_caption))
        self.add_results(
            file_object,
            'caption',
            ExtractedData(
                wrapper=types.AW_STRING,
                mapped_fields=[
                    fields.WeightedMapping(fields.title, probability=1),
                    fields.WeightedMapping(fields.description, probability=1)
                ]
            )(_caption)
        )

        _tags = get_tags(response)
        _tags_pretty = ' '.join(map(lambda x: '"' + x + '"', _tags))
        self.log.debug('Returning tags: {}'.format(_tags_pretty))
        self.add_results(
            file_object,
            'tags',
            ExtractedData(
                wrapper=types.AW_STRING,
                mapped_fields=[
                    fields.WeightedMapping(fields.tags, probability=1),
                ]
            )(_tags)
        )


