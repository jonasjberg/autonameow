from unittest import TestCase

from file_object import FileObject


class TestFileObjectFilenamePartitioningNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)

    def test__filenamepart_base(self):
        self.assertEqual('20160722 Descriptive name', self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        self.assertEqual('txt', self.fo._filenamepart_ext())
        pass

    def test__filenamepart_tags(self):
        # TODO: Implement ..
        pass


class TestFileObjectFilenamePartitioningWithTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)

    def test_fileobject_basics(self):
        self.assertEqual('20160722 Descriptive name -- firsttag tagtwo',
                         self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertEqual('20160722 Descriptive name', self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        # TODO: Implement ..
        pass

    def test__filenamepart_tags(self):
        # TODO: Implement ..
        pass
