`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------

`autonameow` TODO-list
======================

~~Please refer to the [Product
Backlog](https://github.com/1dv430/js224eh-project/wiki/backlog) for a current
listing.~~


High Priority
-------------

* Internal "API" -- data storage structures and communication between modules.
    * Replace the old way of calling the analyzer `get_{fieldname}` methods
      with passing the `Analysis` class method `collect_results` as a callback.
    * Think about distinguishing between *simple "static"* data
      (`filesystem.basename.full`) and "derived data", like a `datetime`-object
      extracted from matched UNIX timestamp in `filesystem.basename.full`.
        * Should the simple static information be collected in a separate run?
        * Should the `Analysis` class `Results` instance only contain "simple
          static" data?
        * Use a separate container for "derived data"?
        * Store all types of results in the `Analysis` class `Results` instance
          but modify the `Results` class to distinguish between the types?


Medium Priority
---------------

* Implement proper plugin interface
    * Have plugins "register" themselves to a plugin handler?
    * Querying plugins might need some translation layer between the
      `autonameow` field naming convention and the specific plugins naming
      convention. For instance, querying a plugin for `title` might require
      actually querying the plugin for `document:title` or similar.
    * Abstract base class for all plugins;
        * Means of providing input data to the plugin.
        * Means of executing the plugin.
        * Means of querying for all or a specific field.


Low Priority
------------

* Add additional filetype-specific "extractors".
    * __Word Documents__
        * Extract plain text and metadata from Word documents.
        * Probably trivially implemented by using some Python library.
* Add support for MacOS Spotlight metadata (`mdls`)


Wishlist
--------

* Construct file rules from user-specified __template__ and __filename__.

  The user specifies a expected __file name template__ and
  a __expected file name__ for a given file;

  ```
  Given file:        "cats-tale.pdf"
  Desired Template:  {datetime} {title} -- {tags}.{extension}
  Expected Filename: "2017-06-10T224655 A Cats Taile -- gibson biography.pdf"
  ```

  The program should then figure out *which data* from *which sources*
  should be used to construct the expected file name.


