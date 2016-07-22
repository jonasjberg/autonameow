from unittest import TestCase

from file_object import FileObject


class TestFileObjectFilenamePartitioningLongNameNoTags(TestCase):
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


class TestFileObjectFilenamePartitioningLongNameWithTags(TestCase):
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


class TestFileObjectFilenamePartitioningHiddenFileNoExtensionNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name', self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo._filenamepart_base())
        self.assertEqual('.name', self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        self.assertIsNone(self.fo._filenamepart_ext())

    def test__filenamepart_tags(self):
        self.assertIsNone(self.fo._filenamepart_tags())


class TestFileObjectFilenamePartitioningHiddenFileNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name.jpg')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name', self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo._filenamepart_base())
        self.assertEqual('.name', self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo._filenamepart_ext())
        self.assertNotEqual(' ', self.fo._filenamepart_ext())
        self.assertNotEqual('', self.fo._filenamepart_ext())
        self.assertNotEqual('bla', self.fo._filenamepart_ext())
        self.assertEqual('jpg', self.fo._filenamepart_ext())

    def test__filenamepart_tags(self):
        self.assertIsNone(self.fo._filenamepart_tags())


class TestFileObjectFilenamePartitioningHiddenFileCompoundSuffix(TestCase):
    def setUp(self):
        self.fo = FileObject('.name.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        # self.assertEqual('.name.tar', self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo._filenamepart_base())
        self.assertEqual('.name', self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo._filenamepart_ext())
        self.assertNotEqual(' ', self.fo._filenamepart_ext())
        self.assertNotEqual('', self.fo._filenamepart_ext())
        self.assertNotEqual('tar', self.fo._filenamepart_ext())
        self.assertNotEqual('gz', self.fo._filenamepart_ext())
        self.assertEqual('tar.gz', self.fo._filenamepart_ext())

    def test__filenamepart_tags(self):
        self.assertIsNone(self.fo._filenamepart_tags())


class TestFileObjectFilenamePartitioningHiddenFileWithTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name -- firsttag 2ndtag.jpg')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name -- firsttag 2ndtag', self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo._filenamepart_base())
        self.assertEqual('.name', self.fo._filenamepart_base())

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo._filenamepart_ext())
        self.assertNotEqual(' ', self.fo._filenamepart_ext())
        self.assertNotEqual('', self.fo._filenamepart_ext())
        self.assertNotEqual('bla', self.fo._filenamepart_ext())
        self.assertEqual('jpg', self.fo._filenamepart_ext())

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo._filenamepart_tags())
        self.assertNotEqual(['firsttag'], self.fo._filenamepart_tags())
        self.assertNotEqual(['2ndtag'], self.fo._filenamepart_tags())
        self.assertEqual(['firsttag', '2ndtag'], self.fo._filenamepart_tags())
