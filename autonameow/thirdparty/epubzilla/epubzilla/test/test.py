#!/usr/bin/env python3

import os
import sys

from bs4 import BeautifulSoup

from ..epubzilla import *

base_dir = os.path.dirname(os.getcwd())
sys.path.append(base_dir)
sys.path.append(base_dir + '../')

import zipfile
import io

e = Epub()

# for element in epub.metadata:
#     print(element.localname, " : ", element.text)

# ADD METADATA ELEMENT
language = Element(name="language",
                   text="en",
                   namespace=PACKAGE_NSMAP['dc'])
e.metadata.add_sub_element(language)

title = Element(name="title",
                text="My First Document",
                namespace=PACKAGE_NSMAP['dc'])
e.metadata.add_sub_element(title)

creator = Element(name="creator",
                  text="Nicholas ODeegan",
                  namespace=PACKAGE_NSMAP['dc'])
e.metadata.add_sub_element(creator)

identifier = Element(name="identifier",
                     text="urn:c00299ac-4b89-11e4-9e35-164230d1df67",
                     namespace=PACKAGE_NSMAP['dc'],
                     attributes={'id': 'id'})
e.metadata.add_sub_element(identifier)
# e.metadata.to_string()

# ADD FILES
string = """
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
</head>
<body>
<h1>Header</h1>
<p>First line.</p>
</body>
</html>

"""

html = bytes('')
e.files.set('OEBPS/first.html', string)

# ADD TO MANIFEST

item_ncx = Element(name="item",
                   attributes={
                       'id': 'ncx',
                       'href': 'toc.ncx',
                       'media-type': 'application/x-dtbncx+xml'
                   })

item_html = Element(name="item",
                    attributes={
                        'id': 'first',
                        'href': 'first.html',
                        'media-type': 'application/xhtml+xml'
                    })

e.manifest.add_sub_element(item_ncx)
e.manifest.add_sub_element(item_html)

# ADD TO SPINE

e.spine.add_itemref('first')

e.make('our_first.epub')

# epub = Epub.from_file("our_first.epub")


# print(epub.package.to_string())



# print(epub)

# test = Epub.from_file("Manly-DeathValley-images.epub")

# print(test.metadata.to_string())

# for order, part in enumerate(epub.manifest.parts):
#   # grab the body text.        
#   soup = BeautifulSoup(epub.files.get(part['href']), 'html.parser')
#   # find all the old href values for images in the original text
#   print(soup)


# for filename in zip.namelist():
#    print(filename)

# print(e.metadata.identifier[0].text)
# print(e.toc.to_string())
# print(e.spine.to_string())



# print(e.toc.to_string())

# print(e.get_file(e.parts[1].attributes['href']))
