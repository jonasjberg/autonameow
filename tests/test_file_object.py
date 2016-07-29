from unittest import TestCase

from file_object import FileObject


class TestFileObjectFilenamePartitioningLongNameNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name', self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('20160722 Descriptive name',
                         self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('jpg', self.fo.filenamepart_ext)
        self.assertEqual('txt', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningLongNameWithTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name -- firsttag tagtwo',
                         self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('20160722 Descriptive name',
                         self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('jpg', self.fo.filenamepart_ext)
        self.assertEqual('txt', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tagtwo'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', 'tagtwo'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningLongNameWithTagsDashesInName(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722--23 Descriptive-- name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722--23 Descriptive-- name -- firsttag tagtwo',
                         self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('20160722--23 Descriptive-- name',
                         self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('jpg', self.fo.filenamepart_ext)
        self.assertEqual('txt', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tagtwo'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', 'tagtwo'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileNoExtensionNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name', self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNone(self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name.jpg')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name', self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('bla', self.fo.filenamepart_ext)
        self.assertEqual('jpg', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileCompoundSuffix(TestCase):
    def setUp(self):
        self.fo = FileObject('.name.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        # self.assertEqual('.name.tar', self.fo.basename_no_ext)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileWithTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name -- firsttag 2ndtag.jpg')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name -- firsttag 2ndtag', self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('bla', self.fo.filenamepart_ext)
        self.assertEqual('jpg', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', '2ndtag'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileCompoundSuffixTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name -- firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name -- firsttag 2ndtag', self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', '2ndtag'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningDifficultCombination(TestCase):
    def setUp(self):
        self.fo = FileObject('.name -- tar firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name -- tar firsttag 2ndtag',
                         self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['tar', 'firsttag', '2ndtag'],
                         self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningAnotherDifficultCombination(TestCase):
    def setUp(self):
        self.fo = FileObject('.tar name -- gz firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.tar name -- gz firsttag 2ndtag',
                         self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.tar name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['gz', 'firsttag', '2ndtag'],
                         self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningEvenMoreDifficultCombination(TestCase):
    def setUp(self):
        self.fo = FileObject('.tar.gz name -- gz firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.tar.gz name -- gz firsttag 2ndtag',
                         self.fo.fnbase)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.tar.gz name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['gz', 'firsttag', '2ndtag'],
                         self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningReturnValueType(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name -- firsttag tagtwo',
                         self.fo.fnbase)

    def test__filenamepart_base_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_base))

    def test__filenamepart_ext_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_ext))

    def test__filenamepart_tags_returns_list_of_string_or_empty_list(self):
        self.assertIs(list, type(self.fo.filenamepart_tags))


class TestFileObjectFilenamePartitioningReturnValueTypeNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name', self.fo.fnbase)

    def test__filenamepart_base_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_base))

    def test__filenamepart_ext_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_ext))

    def test__filenamepart_tags_returns_list_of_string_or_empty_list(self):
        self.assertIs(list, type(self.fo.filenamepart_tags))
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningReturnValueTypeNoTagsNoExt(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name', self.fo.fnbase)

    def test__filenamepart_base_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_base))

    def test__filenamepart_ext_returns_string_or_none(self):
        self.assertIsNot(str, type(self.fo.filenamepart_ext))
        self.assertIsNone(self.fo.filenamepart_ext)

    def test__filenamepart_tags_returns_list_of_string_or_empty_list(self):
        self.assertIs(list, type(self.fo.filenamepart_tags))
        self.assertEqual([], self.fo.filenamepart_tags)
