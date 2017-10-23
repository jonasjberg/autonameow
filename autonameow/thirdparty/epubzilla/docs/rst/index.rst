Epubzilla  Documentation
========================

.. image:: epubzilla.png
   :align: right
   :alt: "Reading maketh a full man; conference a ready man; and writing an exact man."
   :scale: 80%


Epubzilla is a Python library for extracting data from 
EPUB documents.

Currently, the only version supported is EPUB 2.0.1. There are grand plans
to support EPUB 3.0 in the near future.

This project is released under `GPLv3 <http://www.gnu.org/licenses/quick-guide-gplv3.html>`_

Download
--------

The source is available on `bitbucket <https://bitbucket.org/odeegan/epubzilla>`_

Clone the repository: https://bitbucket.org/odeegan/epubzilla.git

Install using pip: **pip install epubzilla**

Upgrade to the newest version: pip install -U epubzilla

Getting Help
------------
If you have questions about epubzilla, send an email to 
odeegan @ gmail . com

Requirements
============
 * Python 2.6+
 * `lxml <http://lxml.de/>`_ version 2.3.5 or later is required 


QuickStart
==========
>>> from epubzilla.epubzilla import Epub
>>> epub = Epub.from_file('Manly-DeathValley-images.epub')
>>> epub.author
'Manly, William Lewis'
>>> epub.title
"Death Valley in '49"


Navigating the Data Structure
=============================

An EPUB file is a zip file that contains a book's resources. And the 
EPUB standard uses XML, XHTML and CSS to both describe the book and format 
its content. That's a gross simplification, but it suffices for a general understanding.

If you're planning to do any real work with EPUBs, I suggest starting
your journey down the wiki rabbit hole `here <http://en.wikipedia.org/wiki/EPUB>`_.

File Layout
-----------

Here's the file layout of an unzipped EPUB from the 
Gutenberg project (`Manly-DeathValley-images.epub <http://www.gutenberg.org/ebooks/12236>`_) ::

 .
 ├── 12236
 │   ├── 0.css
 │   ├── 1.css
 │   ├── content.opf
 │   ├── cover.jpg
 │   ├── pgepub.css
 │   ├── toc.ncx
 │   ├── www.gutenberg.org@files@12236@12236-h@12236-h-0.htm
 │   ├── www.gutenberg.org@files@12236@12236-h@12236-h-1.htm
 │   ├── www.gutenberg.org@files@12236@12236-h@12236-h-2.htm
 │   ├── www.gutenberg.org@files@12236@12236-h@12236-h-3.htm
 │   ├── www.gutenberg.org@files@12236@12236-h@12236-h-4.htm
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_01.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_03.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_04.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_05.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_06.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_07.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_08.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_10.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_11.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_12.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_14.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_16.png
 │   ├── www.gutenberg.org@files@12236@12236-h@ch_17.png
 │   ├── www.gutenberg.org@files@12236@12236-h@frisky_oxen.png
 │   ├── www.gutenberg.org@files@12236@12236-h@frontispiece.png
 │   ├── www.gutenberg.org@files@12236@12236-h@leaving_dv.png
 │   └── www.gutenberg.org@files@12236@12236-h@pulling_oxen.png
 ├── META-INF
 │   └── container.xml
 └── mimetype


The bulk of an EPUBs descriptive data is contained in the **content.opf** file (an XML file). 
Its contents are made browsable in the epubzilla library via its four main elements:
**metadata**, **manifest**, **spine**, **guide**

To help you visualize its contents, here's a simplified view of the file layout::

	<package>
	  <metadata>
	    <title></title>
	    <creator></creator>
	    ...
	  </metadata>
	  <manifest>
	    <item><item>
	    ...
	  </manifest>
	  <spine>
	    <itemref><itemref/>
	    ...
	  </spine>
	  <guide>
	    <reference></reference>
	  	...
	  </guide>
	</package


To access the <title> element, you would do the following::

	epub.package.metadata.title
	# [class <Epub.Element>]

This returns a list of <title> elements. It's a little confusing at first, but it makes
sense when you realize an EPUB can have multiple titles. In fact, several of the metadata
types are allowed multiple entries. To prevent confusion, a list is returned be default.

To access the data contained in an element, do the following::

	epub.package.metadata.title[0].tag.name
	# {http://purl.org/dc/elements/1.1/}title

	epub.package.metadata.title[0].tag.localname
	# title

	epub.package.metadata.title[0].tag.namespace
	# http://purl.org/dc/elements/1.1/

	epub.package.metadata.title[0].tag.text
	# Death Valley in '49

	epub.package.metadata.title[0].as_xhtml
	# <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.idpf.org/2007/opf">Death Valley in '49</dc:title>
	


<metadata> is also an element, so the following is also valid::

	epub.package.metadata.tag.name
	# {http://www.idpf.org/2007/opf}metadata
	
	epub.package.metadata.tag.localname
	# metadata
	
	epub.package.metadata.tag.namespace
	# http://www.idpf.org/2007/opf

	epub.package.metadata.as_xhtml
	# <metadata xmlns="http://www.idpf.org/2007/opf" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	#	<dc:rights>Public domain in the USA.</dc:rights>
	#	<dc:identifier id="id" opf:scheme="URI">http://www.gutenberg.org/ebooks/12236</dc:identifier>
	#	<dc:creator opf:file-as="Manly, William Lewis">William Lewis Manly</dc:creator>
	#	<dc:title>Death Valley in '49</dc:title>
	#	<dc:language xsi:type="dcterms:RFC4646">en</dc:language>
	#	<dc:date opf:event="publication">2004-05-01</dc:date>
	#	<dc:date opf:event="conversion">2010-02-15T17:50:02.335756+00:00</dc:date>
	#	<dc:source>http://www.gutenberg.org/files/12236/12236-h/12236-h.htm</dc:source>
	#	<meta content="item26" name="cover"/>
	# </metadata>

To read up on XML namespaces in an EPUB, start `here <http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section1.3.2>`_.

You can access all of the elements contained within the metadata via the list property::

	epub.metadata.list
	# [class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>]

They can also be directly iterated over::

	for element in epub.metadata:
		print "%s : %s" %(element.tag.localname, element.tag.text)
		for k,v in element.tag.iteritems():
			print "\t %s : %s" %(k,v)
        
	# rights : Public domain in the USA.
	# identifier : http://www.gutenberg.org/ebooks/12236
	#  scheme : URI
	#  id : id
	# creator : William Lewis Manly
	#  file-as : Manly, William Lewis
	# title : Death Valley in '49
	# language : en
	#  type : dcterms:RFC4646
	# date : 2004-05-01
	#  event : publication
	# date : 2010-02-15T17:50:02.335756+00:00
	#  event : conversion
	# source : http://www.gutenberg.org/files/12236/12236-h/12236-h.htm
	# meta : 
	#  content : item26
	#  name : cover

There are typically several ways to access the same data within an EPUB. This is 
reflective of the highly self referential nature of the data. For example, a reference 
to a single image may appear in the metadata, the manifest, the spine and within the 
xhtml document that defines the book text. But we're getting ahead of ourselves...


Epub.Package
------------

The package element is the root element of the content.opf file. It contains the 
`XML namespace declaration <http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section1.3.2>`_
which must be declared at the root of all OPF Package Documents::

	print epub.package.tag.name
	# {http://www.idpf.org/2007/opf}package
 
	print epub.package.tag.namespace
	# http://www.idpf.org/2007/opf
 
	print epub.package.tag.localname
	# package
 
	print epub.package.tag.attributes
	# {u'version': '2.0', u'unique-identifier': 'id'}

The version attribute refers to the OPF version. 

The unique-identifier attribute is defined as follows:

 The package element must specify a value for its **unique-identifier** attribute. The unique-identifier attribute's value specifies which Dublin Core identifier element, described in Section 2.2.10, provides the package's preferred, or primary, identifier.

 The OPF Package Document's author is responsible for choosing a primary identifier that is unique to one and only one particular package (i.e., the set of files referenced from the package document's manifest).

 Notwithstanding the requirement for uniqueness, Reading Systems must not fail catastrophically if they encounter two distinct packages with the same purportedly unique primary identifier.
 --`idpf.org <http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.1>`_

This actual unique identifier is defined in the metadata element. Read below to see an example.

Epub.MetaData
-------------

Details of the EPUB are stored in the metadata element, for example: *title*, 
*creator*, *publisher*, *subject*, *description*, etc. Valid elements 
may come from both the `Dublin Core <http://dublincore.org/documents/2004/12/20/dces/>`_
and the `Open Package Format (OPF) <http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#TOC2.0>`_ 
specifications.::

	epub.metadata.as_xhtml
	# <metadata xmlns="http://www.idpf.org/2007/opf" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	#	<dc:rights>Public domain in the USA.</dc:rights>
	#	<dc:identifier id="id" opf:scheme="URI">http://www.gutenberg.org/ebooks/12236</dc:identifier>
	#	<dc:creator opf:file-as="Manly, William Lewis">William Lewis Manly</dc:creator>
	#	<dc:title>Death Valley in '49</dc:title>
	#	<dc:language xsi:type="dcterms:RFC4646">en</dc:language>
	#	<dc:date opf:event="publication">2004-05-01</dc:date>
	#	<dc:date opf:event="conversion">2010-02-15T17:50:02.335756+00:00</dc:date>
	#	<dc:source>http://www.gutenberg.org/files/12236/12236-h/12236-h.htm</dc:source>
	#	<meta content="item26" name="cover"/>
	# </metadata>

The only three required elements are:
	* title
	* identifier
	* language

The proper format, restrictions and suggested use of all valid elements can be found in the links above.


Epub.Manifest
-------------

The manifest element lists the actual files used in the EPUB::

	for item in epub.manifest:
		print item.tag.attributes
 
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@frontispiece.png', u'id': 'item1', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_01.png', u'id': 'item2', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_03.png', u'id': 'item3', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_04.png', u'id': 'item4', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_05.png', u'id': 'item5', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_06.png', u'id': 'item6', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_07.png', u'id': 'item7', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_08.png', u'id': 'item8', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@leaving_dv.png', u'id': 'item9', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_10.png', u'id': 'item10', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@frisky_oxen.png', u'id': 'item11', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@pulling_oxen.png', u'id': 'item12', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_11.png', u'id': 'item13', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_12.png', u'id': 'item14', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_14.png', u'id': 'item15', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_16.png', u'id': 'item16', u'media-type': 'image/png'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_17.png', u'id': 'item17', u'media-type': 'image/png'}
	# {u'href': 'pgepub.css', u'id': 'item18', u'media-type': 'text/css'}
	# {u'href': '0.css', u'id': 'item19', u'media-type': 'text/css'}
	# {u'href': '1.css', u'id': 'item20', u'media-type': 'text/css'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@12236-h-0.htm', u'id': 'item21', u'media-type': 'application/xhtml+xml'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@12236-h-1.htm', u'id': 'item22', u'media-type': 'application/xhtml+xml'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@12236-h-2.htm', u'id': 'item23', u'media-type': 'application/xhtml+xml'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@12236-h-3.htm', u'id': 'item24', u'media-type': 'application/xhtml+xml'}
	# {u'href': 'www.gutenberg.org@files@12236@12236-h@12236-h-4.htm', u'id': 'item25', u'media-type': 'application/xhtml+xml'}
	# {u'href': 'cover.jpg', u'id': 'item26', u'media-type': 'image/jpeg'}
	# {u'href': 'toc.ncx', u'id': 'ncx', u'media-type': 'application/x-dtbncx+xml'}


There are a few cheater methods available to quickly test for the media-type of the manifest element::

	for item in epub.manifest:
		if item.isDocument():
			print "document"
		if item.isImage():
			print "image"
		if item.isCSS():
			print "css"
		if item.isTOC():
			print "table of contents"
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# image
	# css
	# css
	# css
	# document
	# document
	# document
	# document
	# document
	# image
	# table of contents

If a manifest element references a file, it can be accessed via the element's 
`get_file()` method. A string buffer will be returned.::

 type(epub.manifest[2].get_file())
 #<type 'str'>

TOC (Table of Contents)
^^^^^^^^^^^^^^^^^^^^^^^

The toc manifest element is a reference to the toc.ncx file in the EPUB archive.
NCX stands for **Navigation Control for XML**. It's used by ereaders to create the 
navigational table of contents. This can also be performed with links and anchor tags
in the document text; however, the format is standardized here to allow ereaders
to do various fancy things with the content::

	print epub.manifest[26].get_file()


	# <?xml version='1.0' encoding='UTF-8'?>
	# <!DOCTYPE ncx PUBLIC '-//NISO//DTD ncx 2005-1//EN' 
	#              'http://www.daisy.org/z3986/2005/ncx-2005-1.dtd'>
	#
	# <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">
	#  <head>
	#    <meta content="http://www.gutenberg.org/ebooks/12236" name="dtb:uid"/>
	#    <meta content="3" name="dtb:depth"/>
	#    <meta content="Project Gutenberg EPUB-Maker v0.02 by Marcello Perathoner &lt;webmaster@gutenberg.org&gt;" name="dtb:generator"/>
	#    <meta content="0" name="dtb:totalPageCount"/>
	#    <meta content="0" name="dtb:maxPageNumber"/>
	#  </head>
	#  <docTitle>
	#    <text>Death Valley in '49</text>
	#  </docTitle>
	#  <navMap>
	#    <navPoint id="np-1" playOrder="1">
	#      <navLabel>
	#        <text>INDEX OF CHAPTERS</text>
	#      </navLabel>
	#      <content src="www.gutenberg.org@files@12236@12236-h@12236-h-0.htm#pgepubid00000"/>
	#    </navPoint>
	#    <navPoint id="np-2" playOrder="2">
	#      <navLabel>
	#        <text>INDEX OF ILLUSTRATIONS</text>
	#      </navLabel>
	#      <content src="www.gutenberg.org@files@12236@12236-h@12236-h-0.htm#pgepubid00001"/>
	#      <navPoint id="np-3" playOrder="3">
	#        <navLabel>
	#          <text>CHAPTER I.</text>
	#        </navLabel>
	#        <content src="www.gutenberg.org@files@12236@12236-h@12236-h-0.htm#pgepubid00002"/>
	#      </navPoint>
	#		...
	#		... (omitted for brevity)
	#		...
	#  </navMap>
	# </ncx>


This is typically auto-generated from data in the other package elements, so I won't go into
much detail. It's important to note; however, that *the playOrder attribute of the content
tag does **not*** determine the actual order of the book's content 
(i.e. the order in which it's read). That is defined in the spine element.


Epub.Spine
-------------

Elements in the spine refer to files referenced in the manifest. Their order in the spine
determines the order the book will be displayed in by an ereader::

	for order, element in enumerate(epub.spine):
		print '[%s] %s' %(order, element.tag.localname)
		for k,v in element.tag.iteritems():
			print '\t%s : %s' %(k,v)
	# [0] itemref
	#	idref : item21
	#	linear : yes
	# [1] itemref
	#	idref : item22
	#	linear : yes
	# [2] itemref
	#	idref : item23
	#	linear : yes
	# [3] itemref
	#	idref : item24
	#	linear : yes
	# [4] itemref
	#	idref : item25
	#	linear : yes

The manifest element referenced by the spine element can be retreived directly from the spine::

	spine_element = epub.spine[0]
	spine_element.tag.attributes
	#{u'idref': 'item21', u'linear': 'yes'}

	manifest_element = epub.spine.get_manifest_element(spine_element)
	manifest_element.tag.attributes
	#{u'href': 'www.gutenberg.org@files@12236@12236-h@12236-h-0.htm', u'id': 'item21', u'media-type': 'application/xhtml+xml'}

Additionally, if you know the *id* of the manifest element, you can retrieve it from the manifest::

	epub.manifest.getElementById('item21').tag.attributes
	#{u'href': 'www.gutenberg.org@files@12236@12236-h@12236-h-0.htm', u'id': 'item21', u'media-type': 'application/xhtml+xml'}


Epub.Guide
-------------

The guide element is optional, and has largely been replaced by the TOC. The guide lets you 
identify the specific roll (refered to as type) of each file in the manifest. Here are a few 
example types

 * cover
 * title-page
 * toc
 * index
 * glossary
 * acknowledgements
 * bibliography

The full list of guide types can be found in the `OPF specification <http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.6>`_.

::


	for element in epub.guide:
		print "%s : %s" %(element.tag.localname, element.tag.text)
	for k,v in element.tag.iteritems():
		print "\t %s : %s" %(k,v)

	# reference : 
	#	 href : cover.jpg
	#	 type : cover
	#	 title : Cover Image


Epub.Parts
-------------

This is a shortcut to the manifest elements with a media-type attribute of 
"application/xhtml+xml". They represent the epub text::

	epub.parts
	# [class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>]
 

Epub.Images
-------------

This is a shortcut to the manifest elements with a media-type attribute of 
"image/".


Epub.CSS
-------------

This is a shortcut to the manifest elements with a media-type attribute of 
"text/css".


Additional Shortcuts
====================

Get the epub cover image::

	epub.cover
	# {u'href': 'cover.jpg', u'id': 'item26', u'media-type': 'image/jpeg'}
 
	type(epub.cover.get_file())
	# <type 'str'>

There is no explicit cover element. There is a meta element in the metadata that points
to an image in the manifest::

	<meta content="item26" name="cover"/>

This indicates that the image with id **"item26"** is the cover image. Which
corresponds to an item element in the manifest::

	<item href="cover.jpg" id="item26" media-type="image/jpeg"/>

Which points to an actual file in the EPUB zip file. See above for an overview of
the `File Layout`_.


You can skip the package element when navigating the datastructure::

	epub.package.manifest
	# class <Epub.Manifest>

	epub.manifest
	# class <Epub.Manifest>
	
It's a bit of a cheat, but each of the major elements is a subelement of package, so it
saves you a few characters.

The following methods for accessing tag attributes are equivalent::

	print epub.cover.tag.attributes['id']
	# item26
 
	print epub.cover.tag['id']
	# item26


EPUB Validation
===============

EPUB tools does not perform validation. It brazenly assumes it's being fed
a valid EPUB 2.0.1 file. 

In the meantime, here are two free tools.

 * `idpf.org EPUB checker <http://validator.idpf.org/>`_
 * `epubcheck <http://code.google.com/p/epubcheck/>`_


Creating EPUBs from scratch
===========================

coming soon...
