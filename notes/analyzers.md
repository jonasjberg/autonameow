`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Analyzers
=========
Notes on "analyzers" --- content-specific data providers.

#### Revisions
* 2017-10-15 --- `jonasjberg` Initial.


Requirements
------------

* __Provide all possible data__  
    * Required when using the `--list-all` option and other similar cases
      where data providers are to be "queried" for which data could possibly
      be returned.

* __Provide specific data__
    * Currently implemented by querying the `Repository` for specific MeowURIs.
      The analyzers either does not run at all, or it runs and stores all data
      in the repository.


Structure of Returned Data
--------------------------
Compared to the extractors that return primitive data types, without context;
the analyzers are intended to work at the next level of abstraction.

The analyzers could return only specific fields, including "generic fields".
This could possibly eliminate the need to pass along information on the data
types; "coercer" class, whether it is "multivalued", etc. 

