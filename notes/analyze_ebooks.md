`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Notes on e-book Metadata Extraction
===================================
Notes on extracting metadata from electronic books; `pdf`/`mobi`/`epub`, etc.

#### Revisions
* 2017-08-10 --- `jonasjberg` Initial
* 2017-09-22 --- `jonasjberg` Added notes on DOIs.


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
