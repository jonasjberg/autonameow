`autonameow` -- Design Document
================================================================================


Similar and/or related projects
===============================
Notes on projects similar/related to automatic naming of files,
extracting/parsing metadata, etc.



`hachoir-metadata`
------------------
<http://bitbucket.org/haypo/hachoir/wiki/hachoir-metadata>

hachoir-metadata extracts metadata from multimedia files: music, picture,
video, but also archives.

It tries to give as much information as possible. For some file formats, it
gives more information than libextractor for example, such as the RIFF parser,
which can extract creation date, software used to generate the file, etc. But
hachoir-metadata cannot guess informations. The most complex operation is just
to compute duration of a music using frame size and file size.


`metagoofil`
------------
<https://code.google.com/archive/p/metagoofil/>

Metagoofil is an information gathering tool designed for extracting metadata of
public documents (pdf,doc,xls,ppt,docx,pptx,xlsx) belonging to a target
company.

The tool will perform a search in Google to identify and download the documents
to local disk and then will extract the metadata with different libraries like
Hachoir, PdfMiner and others. With the results it will generate a report with
usernames, software versions and servers or machine names that will help
Penetration testers in the information gathering phase.


GNU `Libextractor`
------------------
<https://www.gnu.org/software/libextractor/>

GNU Libextractor is a library used to extract meta data from files. 
The goal is to provide developers of file-sharing networks, browsers or
WWW-indexing bots with a universal library to obtain simple keywords and meta
data to match against queries and to show to users instead of only relying on
filenames.
libextractor contains the shell command `extract` that, similar to the well-known
`file` command, can extract meta data from a file an print the results to stdout.


* "Reading File Metadata with extract and libextractor"
    Christian Grothoff. Linux Journal, 2005-04-28  
    <http://www.linuxjournal.com/article/7552>


Metadata Extraction Tool developed by the National Libary of New Zealand
------------------------------------------------------------------------
<http://meta-extractor.sourceforge.net/>

The Metadata Extraction Tool was developed by the National Library of New
Zealand to programmatically extract preservation metadata from a range of file
formats like PDF documents, image files, sound files Microsoft office
documents, and many others.


`guessit`
---------
<https://github.com/guessit-io/guessit>
<http://guessit.readthedocs.org/en/latest/>

GuessIt is a python library that extracts as much information as possible from
a video filename.

It has a very powerful matcher that allows to guess properties from a video
using its filename only. This matcher works with both movies and tv shows
episodes.



`Epinfer`
---------
<https://github.com/skerit/epinfer>

Extract as much information as possible from a video filename.  
Inspired by wackou's guessit python module, but in no way as feature complete.

