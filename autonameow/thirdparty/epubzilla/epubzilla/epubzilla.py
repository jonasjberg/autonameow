#!/usr/bin/env python3

import io
import os
import zipfile

# used to parse and generate xml
from lxml import etree

# used to generate a unique id when generating an EPUB
import uuid

# used to parse html to add anchor tags and generate the table of contents
from bs4 import BeautifulSoup

from util import encoding as enc

"""epubzilla.py: a python library for creating, editing and extracting data from EPUB files
__author__: "Nicholas O'Deegan"
__license__: "GPLv3"
__email__: "odeegan@gmail.com"
"""

# Modified for Python 3 compatibility by Jonas Sjöberg 2017-08-19.
__version__ = '0.2.1'

PATH_TO_CONTAINER_XML = "META-INF/container.xml"

CONTAINER_NSMAP = {'n': 'urn:oasis:names:tc:opendocument:xmlns:container'}

PACKAGE_NSMAP = {'opf': 'http://www.idpf.org/2007/opf',
                 'dc': 'http://purl.org/dc/elements/1.1/',
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                 'dcterms': 'http://purl.org/dc/terms/'}

TOC_NSMAP = {'xml': 'http://www.w3.org/XML/1998/namespace',
             'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}


class Epub(object):
    def __init__(self):
        self.filename = None
        self.mimetype = "application/epub+zip"
        self.files = Files()
        self.container = Container(self.files)
        self.package = Package(self.files)
        self.toc = Toc(self)

    @property
    def metadata(self):
        return self.package.metadata

    @property
    def manifest(self):
        return self.package.manifest

    @property
    def spine(self):
        return self.package.spine

    @property
    def guide(self):
        return self.package.guide

    @property
    def title(self):
        """Returns the EPUBS title"""
        return self.metadata.get('title')

    @title.setter
    def title(self, string):
        print("adding title: %s" % string)

    @property
    def author(self):
        """Returns the value of the 'file-as' attribute of the first creator
        listed in the manifest file. If the attribute is not present, it returns
        the text value enclosed by the creator element."""

        for item in self.metadata:
            if item.localname == "creator":
                if 'file-as' in item.attributes:
                    return item.attributes['file-as']
                else:
                    return item.text

    @property
    def cover(self):
        # TODO: This is confusing. Should it return an image iostream, the
        # metdata element, or the manifest element?
        for element in self.metadata:
            if element.localname == 'meta' and 'name' in element.attributes:
                # TODO: test that including namespaces in the key didn't break this
                if element.attributes['name'] == 'cover':
                    return self.manifest.get_element_by_id(
                        element.attributes['content'])
        return None

    @staticmethod
    def from_file(epub_file):
        """Creates an instance of Epub from an epub file
           Accepts epub_file as the fullpath to file or a file object 
        """
        self = Epub()

        # TODO: zipfile.ZipFile accepts a filename or a fileobject.
        # That seems ambiguous. We should probably create a 
        # separate method to create an EPUB from a file object to be more
        # clear.

        if isinstance(epub_file, io.IOBase):
            self.filename = io.FileIO.name

        elif isinstance(epub_file, str):
            self.filename = epub_file
        elif isinstance(epub_file, bytes):
            self.filename = enc.decode_(epub_file)
            epub_file = enc.decode_(epub_file)

        try:
            archive = zipfile.ZipFile(epub_file)

            container_xml = archive.read(PATH_TO_CONTAINER_XML)
            container_xml_tree = etree.fromstring(container_xml)
            path_to_opf = \
                container_xml_tree.xpath('n:rootfiles/n:rootfile/@full-path',
                                         namespaces=CONTAINER_NSMAP)[0]
            # this MUST be set before we begin importing content
            self.container.path_to_content = os.path.dirname(path_to_opf)
            # loads every file into our contents dict
            # key'd on the filename
            for filename in archive.namelist():
                self.files.set(filename, archive.read(filename))
                # print filename
        except (OSError, zipfile.BadZipFile):
            print('Could not open zipfile "%s" \n' % self.filename)
            raise
            # exit(1)

        # parse container.xml for full path to content.opf file

        # Set the base directory to the content files in the archive.
        # We need this to read the individual files later.
        # (for example, images, documents, css, etc.)
        # Each major XML element in the content.opf file is mapped to its own
        # class. This dict maps those classes to the XPaths that point to the
        # corresponding XML element.
        # For example, the XPath "opf:package" points to the '<package>' XML
        # element which is mapped to the Package class
        element_map = [{'name': 'package',
                        'class': Package,
                        'element_xpath': '/opf:package'},
                       {'name': 'metadata',
                        'class': MetaData,
                        'element_xpath': '/opf:package/opf:metadata',
                        'sub_element_xpath': "./*"},
                       {'name': 'manifest',
                        'class': Manifest,
                        'element_xpath': '/opf:package/opf:manifest',
                        'sub_element_xpath': 'opf:item'},
                       {'name': 'spine',
                        'class': Spine,
                        'element_xpath': '/opf:package/opf:spine',
                        'sub_element_xpath': 'opf:itemref'},
                       {'name': 'guide',
                        'class': Guide,
                        'element_xpath': '/opf:package/opf:guide',
                        'sub_element_xpath': 'opf:reference',
                        'optional': True}]

        tree = etree.fromstring(self.files.get(path_to_opf))

        for element_type in element_map:
            try:
                element_tree = tree.xpath(element_type['element_xpath'],
                                          namespaces=PACKAGE_NSMAP)[0]
            except IndexError as e:
                # If the element is marked as optional, just keep going if we
                # don't find it.
                if element_type['optional']:
                    continue
                else:
                    print("%s not found in element_map" % element_type)

            element = getattr(self, element_type['name'])
            element.attributes = element_tree.attrib
            element.name = etree.QName(element_tree).localname
            element.namespace = etree.QName(element_tree).namespace
            element.text = element_tree.text

            if 'sub_element_xpath' in element_type:
                sub_element_tree = element_tree.xpath(
                    element_type['sub_element_xpath'], namespaces=PACKAGE_NSMAP
                )
                for k in sub_element_tree:
                    sub_element = Element()
                    sub_element.attributes = k.attrib
                    sub_element.text = k.text
                    sub_element.name = etree.QName(k.tag).localname
                    sub_element.namespace = etree.QName(k.tag).namespace
                    element.add_sub_element(sub_element)
        return self

        # TODO: rewrite to create the file structure properly

    def make(self, filename, write_file=False):
        # write mimetype file
        self.files.set('mimetype', self.mimetype)

        # write container.xml
        self.files.set(PATH_TO_CONTAINER_XML,
                       self.container.to_string(xml_declaration=True))
        # write content.opf
        self.files.set('%s/%s' % (self.files.dir, 'content.opf'),
                       self.package.to_string(xml_declaration=True))

        # recreate the table of contents
        self.toc.build()
        self.files.set('%s/%s' % (self.files.dir, 'toc.ncx'),
                       self.toc.to_string(xml_declaration=True))

        # create archive
        string = io.StringIO()

        with zipfile.ZipFile(string, 'w') as zip:
            # mimetype has to be the first file written
            zip.writestr('mimetype', self.files.get('mimetype'))
            for epub_file_path, contents in self.files.items():
                if epub_file_path != 'mimetype':
                    zip.writestr(epub_file_path, contents)

        return string


class Files(object):
    def __init__(self):
        self.dir = 'OEBPS'
        self.dictionary = {}

        # TODO: Fix this for outputting, not every file should go in OEBPS

    def set(self, path_to_file, string_buffer):
        self.dictionary[path_to_file] = string_buffer

    def get(self, path_to_file):
        return self.dictionary[path_to_file]

    def get_from_manifest_item(self, manifest_item):
        file_path = "%s/%s" % (self.dir, manifest_item['href'])
        return self.get(file_path)

    def iteritems(self):
        return iter(self.dictionary.items())

    @property
    def file_list(self):
        return sorted(self.dictionary.keys())


class Element(object):
    def __init__(self, parent=None, name="", namespace="", text="",
                 attributes={}):
        self.parent = parent
        self.name = name
        self.attributes = attributes
        self.text = text
        self._namespace = namespace
        self._localname = None

    def get_truncated_attributes(self):
        truncated_attributes = {}
        for k, v in self.attributes.items():
            if '}' in k:
                ns, ln = k.split('}')
                truncated_attributes[ln] = v
            else:
                truncated_attributes[k] = v
        return truncated_attributes

    @property
    def name(self):
        if self.namespace:
            return '{%s}%s' % (self.namespace, self.localname)
        else:
            return self.localname

    @name.setter
    def name(self, name):
        if '}' in name:
            ns, ln = name.split('}')
            self.namespace = ns
            self._localname = ln
        else:
            self._localname = name

    @property
    def localname(self):
        return self._localname

    @property
    def namespace(self):
        if self._namespace:
            return self._namespace
        if self.parent:
            return self.parent.namespace
        return ""

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace

    def __getitem__(self, attribute_name):
        for key, value in self.attributes.items():
            if attribute_name == key:
                return value
        raise KeyError(attribute_name)

    def __repr__(self):
        return "class <Epub.Element>"

    def _xml_tree(self, root=None, tree=None):
        """Creates an lxml etree structure
           Returns both the etree and the root"""
        if tree and root != None:
            subelement = tree.SubElement(root, self.name,
                                         attrib=self.attributes)
            subelement.text = self.text
        else:
            root = etree.Element(self.localname,
                                 attrib=self.attributes,
                                 # every sub_element should not get this nsmap
                                 # nsmap=PACKAGE_NSMAP
                                 )

            root.text = self.text
            return (etree, root)

    def is_image(self):
        return 0 in [x.find('image') for x in list(self.attributes.values())]

    def is_part(self):
        return 0 in [x.find('application/xhtml+xml') for x in
                     list(self.attributes.values())]

    def is_toc(self):
        return 0 in [x.find('application/x-dtbncx+xml') for x in
                     list(self.attributes.values())]

    def is_css(self):
        return 0 in [x.find('text/css') for x in list(self.attributes.values())]

    def to_string(self, xml_declaration=False, encoding="utf-8"):
        print(self.localname)
        etree, root = self._xml_tree()
        return etree.tostring(root,
                              xml_declaration=xml_declaration,
                              encoding=encoding,
                              pretty_print=True)


class CompositeElement(Element):
    def __init__(self, *args, **kwargs):
        super(CompositeElement, self).__init__(*args, **kwargs)
        self._nsmap = None
        self.list = []

    def __repr__(self):
        return "class <Epub.CompositeElement>"

    def add_sub_element(self, sub_element):
        """ Create an appropriate subelement and append it to this
        CompositeElement's list """
        sub_element.parent = self
        self.list.append(sub_element)
        return sub_element

    @property
    def nsmap(self):
        if self._nsmap:
            return self._nsmap
        else:
            if self.parent:
                return self.parent.nsmap
        return self._nsmap

    @nsmap.setter
    def nsmap(self, nsmap):
        self._nsmap = nsmap

    def __len__(self):
        return len(self.list)

    def __getitem__(self, index):
        return self.list[index]

    def __setitem__(self, index, value):
        """ only use when explicitly setting a member of its list element"""
        self.list[index] = value

    def __getattr__(self, name):
        """If there is more than one element with the same name, 
        this returns them as a list of elements"""
        return [element for element in self.list if element.localname == name]

    def _xml_tree(self, root=None, tree=None):
        """Creates an lxml etree structure. If there are child elements,
        it will add them to the tree. Returns both the etree and the root"""

        if tree and root != None:
            subelement = tree.SubElement(root, self.name,
                                         attrib=self.attributes)
            subelement.text = self.text
            for child in self.list:
                child._xml_tree(root=subelement, tree=tree)
        else:
            root = etree.Element(self.localname,
                                 nsmap=self.nsmap,
                                 attrib=self.attributes)
            root.text = self.text
            # set default namespace
            if self.namespace:
                root.set("xmlns", self.namespace)
            for subelement in self.list:
                subelement._xml_tree(root=root, tree=etree)

            return (etree, root)


class Package(CompositeElement):
    """A class representing the package XHTML element found in the contents.opf
    file of an epub
    """

    def __init__(self, epub_contents):
        super(Package, self).__init__()

        self.name = "package"
        self.attributes = {"version": "2.0",
                           "unique-identifier": "id"}
        # default XML namespace for children of the package element
        self.namespace = PACKAGE_NSMAP['opf']
        self.nsmap = PACKAGE_NSMAP

        self.metadata = MetaData()
        self.guide = Guide()
        self.spine = Spine()
        self.manifest = Manifest(self.spine)
        self.add_sub_element(self.metadata)
        self.add_sub_element(self.manifest)
        self.add_sub_element(self.spine)
        self.add_sub_element(self.guide)

    def __repr__(self):
        return "class <Epub.Package>"


class MetaData(CompositeElement):
    """A class representing the metadata XHTML element found in the contents.opf
    file of an epub
    """

    dublin_core_elements = {'title': (),
                            'creator': ('role'),
                            'subject': (),
                            'description': (),
                            'publisher': (),
                            'contributor': (),
                            'date': ('event'),
                            'type': (),
                            'format': (),
                            'identifier': ('scheme'),
                            'source': (),
                            'language': (),
                            'relation': (),
                            'coverage': (),
                            'rights': ()}

    def __init__(self):
        super(MetaData, self).__init__()
        self.name = "metadata"

    def __repr__(self):
        return "class <Epub.MetaData>"

    @property
    def identifier(self):
        identifier = self.get('identifier')
        if not identifier:
            return "bogus"

    def add_sub_element(self, sub_element):
        """ Create an appropriate subelement and append it to this
        CompositeElement's list. Returns the element just created. """

        if sub_element.localname in MetaData.dublin_core_elements \
                and PACKAGE_NSMAP['dc'] != sub_element.namespace:
            # Correct an improperly defined namespace
            # TODO: this code belongs in a suite of element
            # value validators, not here
            sub_element.namespace = PACKAGE_NSMAP['dc']

        super(MetaData, self).add_sub_element(sub_element)

    # TODO: test if this still works
    def get(self, element_name):
        for element in self.list:
            if element_name == element.localname:
                return element.text


class Manifest(CompositeElement):
    """A class representing the manifest XHTML element found in the contents.opf
    file of an epub
    """
    MEDIA_TYPES = {'htm': 'application/xhtml+xml',
                   'html': 'application/xhtml+xml',
                   'jpg': 'image/jpg',
                   'png': 'image/png',
                   'css': 'text/css',
                   'ncx': 'application/x-dtbncx+xml',
                   }

    def __init__(self, spine):
        super(Manifest, self).__init__()
        self.name = "manifest"
        self.spine = spine

    def __repr__(self):
        return "class <Epub.Manifest>"

    @property
    def parts(self):
        return [self.get_item_by_id(s['idref']) for s in self.spine.list]

    @property
    def css(self):
        return [element for element in self.list if element.is_css()]

    @property
    def images(self):
        return [element for element in self.list if element.is_image()]

    def get_item_by_id(self, element_id):
        for item in self.list:
            if item['id'] == element_id:
                return item
        raise Exception(
            "Could not find element with id=%s in the manifest" % element_id)

    def _add_item(self, itemid, file_path):
        for media_type in list(self.MEDIA_TYPES.keys()):
            if file_path.endswith(media_type):
                self.add_sub_element(Element(name='item',
                                             attributes={
                                                 'media-type': media_type,
                                                 'href': file_path,
                                                 'id': str(itemid)}))


class Spine(CompositeElement):
    """A class representing the spine XHTML element found in the contents.opf
    file of an epub
    """

    def __init__(self):
        super(Spine, self).__init__()
        self.name = "spine"
        self.attributes = {'toc': 'ncx'}

    def __repr__(self):
        return "class <Epub.Spine>"

    def add_itemref(self, idref):
        self.add_sub_element(Element(
            name='itemref',
            attributes={'linear': 'yes',
                        'idref': str(idref)}))


class Guide(CompositeElement):
    """A class representing the guide XHTML element found in the contents.opf
    file of an epub
    """

    def __init__(self):
        super(Guide, self).__init__()
        self.name = "guide"

    def __repr__(self):
        return "class <Epub.Guide>"


class Container(CompositeElement):
    """A class representing the container.xml file"""

    def __init__(self, files, path_to_content='OEBPS'):
        super(Container, self).__init__()
        self.name = "container"
        self.namespace = CONTAINER_NSMAP['n']
        self.nsmap = CONTAINER_NSMAP
        self.attributes = {'version': '1.0'}
        self._path_to_content = path_to_content
        self.files = files
        self._build_xml()

    @property
    def path_to_content(self):
        return self._path_to_content

    @path_to_content.setter
    def path_to_content(self, path_to_content):
        # Each time the full_path is changed, rebuild the container
        self._path_to_content = path_to_content
        self.files.dir = path_to_content
        # print "path to content = %s" %self.files.dir
        self._build_xml()

    def _build_xml(self):
        # remove all sub_elements
        self.list = []
        # readd them from scratch with new full_path
        rootfiles = self.add_sub_element(CompositeElement(name="rootfiles"))
        rootfiles.add_sub_element(Element(
            name="rootfile",
            attributes={"media-type": "application/oebps-package+xml",
                        "full-path": '%s%s' % (
                            self.path_to_content, '/content.opf')
                        }))

    def __repr__(self):
        return "class <Epub.Container>"


class Toc(CompositeElement):
    """A class representing the container.xml file. It expects an instance
    of the epub in order to generate the table of contents"""

    def __init__(self, epub, depth=2):
        super(Toc, self).__init__()
        self.epub = epub
        self.name = "ncx"
        # self.nsmap = TOC_NSMAP
        # set default namespace
        # self.namespace = "http://www.daisy.org/z3986/2005/ncx/"
        self.attributes = {"xmlns": TOC_NSMAP['ncx'],
                           "version": "2005-1",
                           "{%s}%s" % (TOC_NSMAP['xml'], 'lang'): "en"}
        self.depth = 1

    def build(self):
        # remove all the child elements and start fresh
        self.list = []
        self._build_head()
        self._build_doc_title()
        self._build_navmap()

    def _build_head(self):
        self.head = self.add_sub_element(CompositeElement(name="head"))
        self.head.add_sub_element(
            Element(name="meta",
                    attributes={
                        "name": "dtb:depth",
                        "content": str(self.depth)
                    }))
        self.head.add_sub_element(
            Element(name="meta",
                    attributes={
                        "name": "dtb:generator",
                        "content": "Epubzilla %s" % __version__
                    }))
        self.head.add_sub_element(
            Element(name="meta",
                    attributes={
                        "name": "dtb:totalPageCount",
                        "content": "0"
                    }))
        self.head.add_sub_element(
            Element(name="meta",
                    attributes={
                        "name": "dtb:maxPageNumber",
                        "content": "0"
                    }))
        self.head.add_sub_element(
            Element(name="meta",
                    attributes={
                        "name": "dtb:uid",
                        # This is the epub's unique identifier.
                        # epub.metadata.identifier returns a list because,
                        # most metadata elements can appear multiple times.
                        # identifier is an exception, so we're safe always
                        # taking the first element.
                        # TODO: need to add a method to create the
                        # metadata identifier
                        "content": "urn:c00299ac-4b89-11e4-9e35-164230d1df67"
                    }))

    def _build_doc_title(self):
        doc_title = self.add_sub_element(CompositeElement(name="docTitle"))
        doc_title_text = doc_title.add_sub_element(Element(name="text"))
        doc_title_text.text = self.epub.title

    def _build_navmap(self):
        self.navmap = self.add_sub_element(CompositeElement(name="navMap"))
        all_headers = []
        header_name_set = set()
        # parse the text parts for header tags
        counter = 0
        spine_elements = [e for e in self.epub.spine.list]
        # get correct document part order from the spine, then
        # grab the corresponding items from the manifest
        parts = [self.epub.manifest.get_item_by_id(se['idref']) for se in
                 spine_elements]

        for part in parts:
            path_to_file = part.attributes['href']
            soup = BeautifulSoup(self.epub.files.get('OEBPS/' + path_to_file))
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
            for header_tag in headers:
                header_id = 'tocheader_' + str(counter)
                header_name_set.add(header_tag.name)
                header_tag['id'] = header_id
                self.epub.files.set('OEBPS/' + path_to_file, str(soup))
                all_headers.append((header_id, header_tag, path_to_file))
                counter = counter + 1
        header_name_list = sorted(list(header_name_set))
        # restrict the depth of our table of contents
        header_name_list = header_name_list[:self.depth]
        toc_header_tuples = [htuple for htuple in all_headers if
                             htuple[1].name in header_name_list]

        for header_id, header_tag, path_to_file in toc_header_tuples:
            self._add_navpoint(header_id, header_tag.text, path_to_file)

    def _add_navpoint(self, header_id, header_tag_text, path_to_file):
        navpoint = CompositeElement(name='navPoint',
                                    attributes={'id': 'np-' + str(
                                        len(self.navmap.list))})
        navlabel = CompositeElement(name='navLabel')
        navlabel_text = Element(name='text', text=header_tag_text)
        content = Element(name='content',
                          attributes={
                              'src': '%s#%s' % (path_to_file, header_id)})

        self.navmap.add_sub_element(navpoint)
        navpoint.add_sub_element(navlabel)
        navlabel.add_sub_element(navlabel_text)
        navpoint.add_sub_element(content)

    def __repr__(self):
        return "class <Epub.Toc>"
