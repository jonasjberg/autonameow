`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Notes on e-book Metadata Extraction
===================================
Notes on extracting metadata from electronic books; `pdf`/`mobi`/`epub`, etc.

#### Revisions
* 2017-08-10 --- `jonasjberg` Initial
* 2017-09-22 --- `jonasjberg` Added notes on DOIs.
* 2017-10-17 --- `jonasjberg` Added notes on merging authors.


Unique Identifiers
------------------

### ISBN
The simplest way and most reliable method for finding valid book metadata is
through __ISBN numbers__.
Find ISBN-numbers in the books plain text and use them to query some web
service for information.


#### Methods for finding ISBN-numbers more likely to be correct

* Weight ISBN-numbers found in the first few pages higher
* Weight ISBN-numbers found in the last few pages higher. But watch out for
  list of references to other books!
* If some metadata is already known, weight ISBN numbers located close to say
  the publisher name or the authors name higher.
* Weight multiple variations of ISBN-numbers that appear within close proximity
  in the text higher. Often, more than one type of ISBN-number is listed.
  ISBN-10, ISBN-13, ISBN for the e-book, etc.

### DOI
DOI (Digital Object Identifiers) are unique identifiers similar to ISBN-numbers.
They are commonly used in scientific literature.
Would be integrated into `autonameow` in a manner close to that of ISBN-numbers.


Miscellaneous Notes
-------------------

### Date/Time
If all else fails; search any reference section for valid years. The book
probably doesn't reference something from the future. Maybe the book is
published in the latest mentioned year? (biggest number, if sorted numerically)

Could also search the entire text for `\b[0-9]{4}\b`, sort and assume the
biggest resulting number to be at least indicative to the correct year of
publication. One could use this to weight other results.


Merging ISBN Metadata
---------------------
Log dump illustrating a case currently not handled correctly:

```
analyzers.analyze_ebook   run                   Extracted ISBN: 9781118236086
analyzers.analyze_ebook   _get_isbn_metadata    Using cached metadata for ISBN: 9781118236086
analyzers.analyze_ebook   run                   Metadata for ISBN: 9781118236086
analyzers.analyze_ebook   run                   Title     : Mastering Windows Network Forensics And Investigation
analyzers.analyze_ebook   run                   Authors   : ['Steven Anson', 'Steve Bunting', 'Ryan Johnson', 'Scott Pearson']
analyzers.analyze_ebook   run                   Publisher : Sybex
analyzers.analyze_ebook   run                   Year      : 2012
analyzers.analyze_ebook   run                   Language  : eng
analyzers.analyze_ebook   run                   ISBN-10   : 1118236084
analyzers.analyze_ebook   run                   ISBN-13   : 9781118236086
analyzers.analyze_ebook   run                   Extracted ISBN: 9781118264119
analyzers.analyze_ebook   _get_isbn_metadata    Using cached metadata for ISBN: 9781118264119
analyzers.analyze_ebook   run                   Metadata for ISBN: 9781118264119
analyzers.analyze_ebook   run                   Title     : Mastering Windows Network Forensics And Investigation
analyzers.analyze_ebook   run                   Authors   : ['Steve Anson ... [et al.]']
analyzers.analyze_ebook   run                   Publisher : Wiley
analyzers.analyze_ebook   run                   Year      : 2012
analyzers.analyze_ebook   run                   Language  : eng
analyzers.analyze_ebook   run                   ISBN-10   : 1118264118
analyzers.analyze_ebook   run                   ISBN-13   : 9781118264119
analyzers.analyze_ebook   run                   Extracted ISBN: 9781118226148
analyzers.analyze_ebook   _get_isbn_metadata    Using cached metadata for ISBN: 9781118226148
analyzers.analyze_ebook   run                   Metadata for ISBN: 9781118226148
analyzers.analyze_ebook   run                   Title     : Mastering Windows Network Forensics And Investigation
analyzers.analyze_ebook   run                   Authors   : ['Steven Anson', 'Steve Bunting', 'Ryan Johnson', 'Scott Pearson']
analyzers.analyze_ebook   run                   Publisher : Wiley
analyzers.analyze_ebook   run                   Year      : 2012
analyzers.analyze_ebook   run                   Language  : eng
analyzers.analyze_ebook   run                   ISBN-10   : 1118226143
analyzers.analyze_ebook   run                   ISBN-13   : 9781118226148
analyzers.analyze_ebook   run                   Extracted ISBN: 9781118163825
analyzers.analyze_ebook   _get_isbn_metadata    Using cached metadata for ISBN: 9781118163825
analyzers.analyze_ebook   run                   Metadata for ISBN: 9781118163825
analyzers.analyze_ebook   run                   Title     : Mastering Windows Network Forensics And Investigation
analyzers.analyze_ebook   run                   Authors   : ['Steven Anson', 'Steve Bunting', 'Ryan Johnson', 'Scott Pearson']
analyzers.analyze_ebook   run                   Publisher : John Wiley & Sons
analyzers.analyze_ebook   run                   Year      : 2012
analyzers.analyze_ebook   run                   Language  : eng
analyzers.analyze_ebook   run                   ISBN-10   : 1118163826
analyzers.analyze_ebook   run                   ISBN-13   : 9781118163825
analyzers.analyze_ebook   run                   Got 4 instances of ISBN metadata
analyzers.analyze_ebook   _add_results          EbookAnalyzer passing "analyzer.ebook.title" to "add_results" callback
```


Three of the resulting metadata sets lists the same four authors:
```
Authors: ['Steven Anson', 'Steve Bunting', 'Ryan Johnson', 'Scott Pearson']
```


One of the metadata sets lists only one author, adding `... [et al.]`:
```
Authors: ['Steve Anson ... [et al.]']
```


This is not detected correctly. These sets should probably by seen as
duplicates to be merged into one single set of metadata.
