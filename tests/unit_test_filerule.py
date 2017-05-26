from unittest import TestCase

from core.config.configuration import FileRule


class TestFileRule(TestCase):
    def setUp(self):
        self.maxDiff = None

        _rule_contents = {
            '_description': 'First Entry in the Default Configuration',
            '_exact_match': False,
            '_weight': None,
            'name_template': 'default_template_name',
            'conditions': {
                'filename': {
                    'pathname': None,
                    'basename': None,
                    'extension': None
                },
                'contents': {
                    'mime_type': None
                }
            },
            'data_sources': {
                'datetime': None,
                'description': None,
                'title': None,
                'author': None,
                'publisher': None,
                'extension': 'filename.extension'
            }
        }
        self.filerule = FileRule(_rule_contents)

    def test_get_conditions(self):
        _expect_conditions = {
            'filename': {
                'pathname': None,
                'basename': None,
                'extension': None
            },
            'contents': {
                'mime_type': None
            }
        }
        self.assertEqual(self.filerule.get_conditions(), _expect_conditions)

    def test_get_data_sources(self):
        _expect_data_sources = {
                'datetime': None,
                'description': None,
                'title': None,
                'author': None,
                'publisher': None,
                'extension': 'filename.extension'
            }

        self.assertEqual(self.filerule.get_data_sources(), _expect_data_sources)