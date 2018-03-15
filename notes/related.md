# `autonameow`

--------------------------------------------------------------------------------

Similar and/or related projects
===============================
Notes on projects similar/related to automatic naming of files,
extracting/parsing metadata, etc.



`hachoir-metadata`
------------------
hachoir-metadata extracts metadata from multimedia files: music, picture,
video, but also archives.

* Sources: <http://bitbucket.org/haypo/hachoir/wiki/hachoir-metadata>

It tries to give as much information as possible. For some file formats, it
gives more information than libextractor for example, such as the RIFF parser,
which can extract creation date, software used to generate the file, etc. But
hachoir-metadata cannot guess informations. The most complex operation is just
to compute duration of a music using frame size and file size.


`metagoofil`
------------
Metagoofil is an information gathering tool designed for extracting metadata of
public documents (pdf,doc,xls,ppt,docx,pptx,xlsx) belonging to a target
company.

* Sources: <https://code.google.com/archive/p/metagoofil/>

The tool will perform a search in Google to identify and download the documents
to local disk and then will extract the metadata with different libraries like
Hachoir, PdfMiner and others. With the results it will generate a report with
usernames, software versions and servers or machine names that will help
Penetration testers in the information gathering phase.


`GNU Libextractor`
------------------
* Website: <https://www.gnu.org/software/libextractor/>
* Sources: <http://ftp.gnu.org/gnu/libextractor/>

GNU Libextractor is a library used to extract meta data from files.
The goal is to provide developers of file-sharing networks, browsers or
WWW-indexing bots with a universal library to obtain simple keywords and meta
data to match against queries and to show to users instead of only relying on
filenames.

libextractor contains the shell command `extract` that, similar to the
well-known `file` command, can extract meta data from a file an print the
results to stdout.

* "Reading File Metadata with extract and libextractor"
    Christian Grothoff. Linux Journal, 2005-04-28  
    <http://www.linuxjournal.com/article/7552>


`meta-extractor`
----------------
* Sources: <http://meta-extractor.sourceforge.net/>

Metadata Extraction Tool developed by the National Libary of New Zealand
The Metadata Extraction Tool was developed by the National Library of New
Zealand to programmatically extract preservation metadata from a range of file
formats like PDF documents, image files, sound files Microsoft office
documents, and many others.


`guessit`
---------
GuessIt is a python library that extracts as much information as possible
from a video filename.

* Website: <https://github.com/guessit-io/guessit>
* Sources: <https://github.com/guessit-io/guessit>
* Documentation: <http://guessit.readthedocs.org/en/latest/>

It has a very powerful matcher that allows to guess properties from a video
using its filename only. This matcher works with both movies and tv shows
episodes.


`Epinfer`
---------
* Sources: <https://github.com/skerit/epinfer>

Extract as much information as possible from a video filename.  
Inspired by wackou's guessit python module, but in no way as feature complete.


`guessfilename.py`
------------------
* Sources: <https://github.com/novoid/guess-filename.py>

Tries to come up with a new file name for each file from command line argument.

~~Part of a very interesting and very well thought out system, similar to what
I want to accomplish. I have already stolen a lot of ideas from [this blog][1],
starting when I found [this post][2] a couple of years ago.~~


`tvnamer`
---------
* Sources: <https://github.com/dbr/tvnamer>

tvnamer is a utility which to rename files from
`some.show.s01e03.blah.abc.avi` to `Some Show - [01x03] - The Episode Name.avi`
(by retrieving the episode name using data from tvdb_api)

~~Similar functionality and overall idea of automated renaming.~~


`beets`
-------
Media library management system for obsessive-compulsive music geeks.

* Website: <http://beets.io/>
* Sources: <https://github.com/beetbox/beets>

> Beets is the media library management system for obsessive-compulsive music
> geeks.  The purpose of beets is to get your music collection right once and for
> all. It catalogs your collection, automatically improving its metadata as it
> goes. It then provides a bouquet of tools for manipulating and accessing your
> music.

~~I use this myself and it does work well for automatically restructuring a
music collection.~~


`filebot`
---------
* Website: <http://www.filebot.net>
* Sources: <https://github.com/filebot/filebot>

FileBot is the ultimate tool for organizing and renaming your movies, tv shows
or anime, and music well as downloading subtitles and artwork. It's smart and
just works.


`Movie Renamer`
---------------
* Website: <http://movie-renamer.fr>
* Sources: <https://code.google.com/archive/p/movie-renamer>

> Movie Renamer is an Open Source application Windows/Linux/OSX, totally free
> written in java, for easily renaming movie files.


`grobid`
--------
A machine learning software for extracting information from scholarly documents.

* Sources: <https://github.com/kermitt2/grobid>

> GROBID is a machine learning library for extracting, parsing and re-structuring
> raw documents such as PDF into structured TEI-encoded documents with a
> particular focus on technical and scientific publications.


`CERMINE`
---------
Content ExtRactor and MINEr.

* Sources: <https://github.com/CeON/CERMINE>

> CERMINE is a Java library and a web service (cermine.ceon.pl) for extracting
> metadata and content from PDF files containing academic publications.  CERMINE
> is written in Java at Centre for Open Science at Interdisciplinary Centre for
> Mathematical and Computational Modelling, University of Warsaw.


`Rexa metatagger`
-----------------
Scientific paper header and reference extraction.

* Sources: <https://github.com/iesl/rexa1-metatagger>

> Metatagger is a system which consumes the output of the Rexa's pstotext tool
> and produces an annotated version of the text, finishing by writing the results
> to an XML file. The system is a structured series of pipelined components, each
> performing some task, such as layout analysis (e.g., header block, abstract,
> body text), or finer-grained labelling, such as identifying reference fields.


`movemetafs`
------------
A searchable filesystem metadata store for Linux.

* Website: <https://pts.50.hu>

> movemetafs is a searchable filesystem metadata store for Linux (with MySQL,
> Perl and FUSE), which lets users tag local files (including image, video,
> audio and text files) by simply moving the files to a special folder using
> any file manager, and it also lets users find files by tags, using a boolean
> search query. The original files (and their names) are kept intact.
> movemetafs doesn't have its own user interface, but it is usable with any
> file manager. movemetafs also lets users attach (unsearchable) textual
> description to files.


`Apache Tika`
-------------
Apache Tika(TM) is a toolkit for detecting and extracting metadata and
structured text content from various documents using existing parser libraries.

* Website: <https://tika.apache.org>
* Sources: <https://gitbox.apache.org/repos/asf/tika.git>
* Sources: <https://github.com/apache/tika/>

> The Apache Tika(TM) toolkit detects and extracts metadata and text from over a
> thousand different file types (such as PPT, XLS, and PDF). All of these file
> types can be parsed through a single interface, making Tika useful for search
> engine indexing, content analysis, translation, and much more.


`yargy`
-------
Tiny package for information extraction

* Sources: <https://github.com/natasha/yargy>
* Documentation: <http://yargy.readthedocs.io/en/latest/>

> Yargy is a Earley parser, that uses russian morphology for facts extraction
> process, and written in pure python


`iepy`
-------
Information Extraction in Python

* Sources: <https://github.com/machinalis/iepy>
* Documentation: <http://iepy.readthedocs.org/en/latest/>

> IEPY is an open source tool for Information Extraction focused on Relation Extraction.
> Yargy is a Earley parser, that uses russian morphology for facts extraction
> process, and written in pure python


`DeepDive`
----------
* Website: <http://deepdive.stanford.edu/>
* Sources: <https://github.com/HazyResearch/deepdive>
* Documentation: <https://github.com/HazyResearch/deepdive/blob/master/doc/index.md>

> DeepDive is a system to extract value from dark data. Like dark matter, dark
> data is the great mass of data buried in text, tables, figures, and images,
> which lacks structure and so is essentially unprocessable by existing software.
> DeepDive helps bring dark data to light by creating structured data (SQL
> tables) from unstructured information (text documents) and integrating such
> data with an existing structured database. DeepDive is used to extract
> sophisticated relationships between entities and make inferences about facts
> involving those entities. DeepDive helps one process a wide variety of dark
> data and put the results into a database. With the data in a database, one can
> use a variety of standard tools that consume structured data; e.g.,
> visualization tools like Tableau or analytics tools like Excel.


`Wandora`
---------
* Website: <http://wandora.org/www/>
* Sources: <https://github.com/wandora-team/wandora>
* Documentation: <http://wandora.org/wiki/Main_Page>

> Wandora is a desktop application to collect, store, manipulate and publish
> information, especially associative data and data about WWW resources.


`FRIL`
------
Fine-Grained Records Integration and Linkage Tool

* Website: <http://fril.sourceforge.net/>
* Sources: <http://fril.sourceforge.net/download.html>
* Documentation: <http://fril.sourceforge.net/publications.html>

> FRIL is FREE open source tool that enables fast and easy record linkage.
> The tool extends traditional record linkage tools with a richer set of
> parameters.
> Users may systematically and iteratively explore the optimal combination
> of parameter values to enhance linking performance and accuracy.


`MALLET`
--------
MAchine Learning for LanguagE Toolkit

* Website: <http://mallet.cs.umass.edu/>
* Sources: <https://github.com/mimno/Mallet>
* Documentation: <http://mallet.cs.umass.edu/classification.php>

> MALLET is a Java-based package for statistical natural language processing,
> document classification, clustering, topic modeling, information extraction,
> and other machine learning applications to text.


`parserator`
------------
A toolkit for making domain-specific probabilistic parsers

* Website: <http://parserator.datamade.us/>
* Sources: <https://github.com/datamade/parserator>
* Documentation: <http://parserator.rtfd.org/>

> Do you have domain-specific text data that would be much more useful if you
> could derive structure from the strings? This toolkit will help you create a
> custom NLP model that learns from patterns in real data and then uses that
> knowledge to process new strings automatically. All you need is some training
> data to teach your parser about its domain.


`Hazel`
-------
Automated Organization for Your Mac.

* Website: <https://www.noodlesoft.com/>
* Sources: *N/A*
* Documentation: <https://www.noodlesoft.com/manual/hazel>

> Hazel helps you reduce clutter and save time by automatically moving,
> sorting, renaming, and performing various other actions on the folders that
> tend to accumulate lots of files (such as your Desktop and Downloads
> folders).


`Archivematica`
---------------
Free and open-source digital preservation system designed to maintain
standards-based, long-term access to collections of digital objects.

* Website: <https://www.archivematica.org/>
* Sources: <https://github.com/artefactual/archivematica>
* Documentation: <https://www.archivematica.org/>

> Archivematica is a web- and standards-based, open-source application which
> allows your institution to preserve long-term access to trustworthy,
> authentic and reliable digital content. Our target users are archivists,
> librarians, and anyone working to preserve digital objects.


`Autonomio`
-----------
Autonomio provides a very high level abstraction layer for rapidly testing
research ideas and instantly creating neural network based decision making
models.

* Website: <https://mikkokotila.github.io/slate/#introduction>
* Sources: <https://github.com/autonomio/autonomio>
* Documentation: <https://mikkokotila.github.io/slate/#introduction>

> Autonomio provides a high-level abstraction layer to building, configuring
> and optimizing neural networks and then using the trained models to make
> predictions in any environment. Unlike with other similar solutions, there is
> no need for signing up, API keys, cloud instances, or GPUs, and you have 100%
> control over the model. A typical installation takes a minute, and training a
> model not more than few minutes including data transformation from raw
> dataset with even thousands of columns, open text, and unstructured labels.
> Nothing is pre-trained, and only you have access to your data and
> predictions. There is no commercial entity behind Autonomio, but a non-profit
> research Foundation.




[1]: http://karl-voit.at
[2]: http://karl-voit.at/managing-digital-photographs/
