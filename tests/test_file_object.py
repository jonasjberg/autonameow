from unittest import TestCase

from file_object import FileObject


class TestFileObjectFilenamePartitioningSimple(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)

    def test__filenamepart_base(self):
        # TODO: Implement ..
        pass

    def test__filenamepart_ext(self):
        # TODO: Implement ..
        pass

    def test__filenamepart_tags(self):
        # TODO: Implement ..
        pass
