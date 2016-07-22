from unittest import TestCase

from file_object import FileObject


class TestFileObjectFilenamePartitioningNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name', self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo._filenamepart_base())
        self.assertEqual('20160722 Descriptive name',
                         self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo._filenamepart_ext())
        self.assertNotEqual(' ', self.fo._filenamepart_ext())
        self.assertNotEqual('', self.fo._filenamepart_ext())
        self.assertNotEqual('jpg', self.fo._filenamepart_ext())
        self.assertEqual('txt', self.fo._filenamepart_ext())

    def test__filenamepart_tags(self):
        self.assertIsNone(self.fo._filenamepart_tags())


class TestFileObjectFilenamePartitioningWithTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name -- firsttag tagtwo',
                         self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo._filenamepart_base())
        self.assertEqual('20160722 Descriptive name',
                         self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo._filenamepart_ext())
        self.assertNotEqual(' ', self.fo._filenamepart_ext())
        self.assertNotEqual('', self.fo._filenamepart_ext())
        self.assertNotEqual('jpg', self.fo._filenamepart_ext())
        self.assertEqual('txt', self.fo._filenamepart_ext())

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo._filenamepart_tags())
        self.assertNotEqual(['firsttag'], self.fo._filenamepart_tags())
        self.assertNotEqual(['tagtwo'], self.fo._filenamepart_tags())
        self.assertEqual(['firsttag', 'tagtwo'], self.fo._filenamepart_tags())


