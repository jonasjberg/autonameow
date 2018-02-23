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

# Source repo:           https://github.com/jonasjberg/image-utils
# Based on commit hash:  2972dae5df58b335e80244ab176d38281d49171e

# This is me playing around with the Microsoft Vision API on a friday night.

import http.client as httplib
import os
import json
from urllib.parse import urlencode

from core import types
from core import constants as C
from core.exceptions import AutonameowPluginError
from core.model import WeightedMapping
from core.namebuilder import fields
from plugins import BasePlugin
from util import mimemagic


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
        response_data = response.read().decode(C.DEFAULT_ENCODING)
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
        return None
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
        return None
    else:
        if count and len(tags) > count:
            return tags[:count]
        return tags


def _read_api_key_from_file(file_path):
    try:
        with open(file_path, mode='r', encoding=C.DEFAULT_ENCODING) as f:
            api_key = f.read()
            return api_key.strip()
    except OSError:
        return None


class MicrosoftVisionPlugin(BasePlugin):
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
    DISPLAY_NAME = 'MicrosoftVision'
    MEOWURI_LEAF = DISPLAY_NAME.lower()
    # TODO: [TD0178] Store only strings in 'FIELD_LOOKUP'.
    FIELD_LOOKUP = {
        'caption': {
            'coercer': types.AW_STRING,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1),
                WeightedMapping(fields.Description, probability=1)
            ],
            'generic_field': None
        },
        'tags': {
            'coercer': types.AW_STRING,
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            'generic_field': 'tags'
        }
    }

    api_key_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), 'microsoft_vision.key'
    )
    API_KEY = _read_api_key_from_file(api_key_path)

    def __init__(self):
        super().__init__(display_name=self.DISPLAY_NAME)

    def execute(self, fileobject):
        source_path = fileobject.abspath
        response = query_api(source_path, self.API_KEY)
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

        # TODO: Improve error handling!

        results = dict()
        _caption = get_caption_text(response)
        if _caption:
            _coerced_caption = self.coerce_field_value('caption', _caption)
            if _coerced_caption is not None:
                results['caption'] = _coerced_caption

        _tags = get_tags(response)
        if _tags:
            _coerced_tags = self.coerce_field_value('tags', _tags)
            if _coerced_tags is not None:
                results['tags'] = _coerced_tags

        return results

    def can_handle(self, fileobject):
        return mimemagic.eval_glob(fileobject.mime_type, 'image/*')

    @classmethod
    def test_init(cls):
        return cls.API_KEY is not None
