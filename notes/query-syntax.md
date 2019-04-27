`autonameow`
============
*Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------

General Query Syntax
====================
Various examples of query syntax used by other programs for similar purposes.

#### Revisions
* 2018-01-06 --- `jonasjberg` Initial.


Windows Advanced Query Syntax
-----------------------------
<https://msdn.microsoft.com/en-us/library/aa965711(vs.85).aspx>

Excerpt from above document;

> The Advanced Query Syntax (AQS) is used by Microsoft Windows Desktop
> Search (WDS) to help users and programmers better define and narrow
> their searches. Using AQS is an easy way to narrow searches and deliver
> better result sets. Searches can be narrowed by the following
> parameters:
>
> -   File kinds: folders, documents, presentations, pictures and so on.
> -   File stores: specific databases and locations.
> -   File properties: size, date, title and so on.
> -   File contents: keywords like "project deliverables," "AQS," "blue
>     suede shoes," and so on.
>
> Furthermore, search parameters can be combined using search operators.
> The remainder of this section explains the query syntax, the parameters
> and operators, and how they can be combined to offer targeted search
> results. The tables describe the syntax to use with WDS, as well as the
> properties that can be queried for each file kind displayed in the
> **Windows Desktop Search** results window.
>
> ### Desktop Search Syntax
>
> A search query can include one or more keywords, with Boolean operators
> and optional criteria. These optional criteria can narrow a search based
> on the following:
>
> -   Scope or data store in which files reside
> -   Kinds of files
> -   Managed properties of files
>
> The optional criteria, described in greater detail following, use the
> following syntax:
>
> `<scope name>:<value>`
>
> `<file kind>:<value>`
>
> `<property name>:<value>`
>
> Suppose a user wants to search for a document containing the phase "last
> quarter," created by John or Joanne, and that the user saved to the
> folder mydocuments. The query may look like this:
>
> `"last quarter" author:(john OR joanne) foldername:mydocuments`


Apple File Metadata Search
--------------------------
File Metadata Search Programming Guide

* [Introduction -- About File Metadata Queries](https://developer.apple.com/library/content/documentation/Carbon/Conceptual/SpotlightQuery/Concepts/Introduction.html>)
* [Searching File Metadata with NSMetadataQuery](https://developer.apple.com/library/content/documentation/Carbon/Conceptual/SpotlightQuery/Concepts/QueryingMetadata.html)
* [File Metadata Query Expression Syntax](https://developer.apple.com/library/content/documentation/Carbon/Conceptual/SpotlightQuery/Concepts/QueryFormat.html)

Various excerpts from above documents;


> ### File Metadata Query Expression Syntax
>
> File metadata queries are constructed using a query language that is a
> subset of the predicate string format. The metadata search expression
> syntax allows an application to construct searches ‘on the fly’, allow
> advanced users to construct their own queries, or your application to
> store often used queries for easy use. The syntax is relatively
> straightforward, including comparisons, language agnostic options, and
> time and date variables.
>
> #### Comparison Syntax
> The file metadata query expression syntax is a simplified form of
> filename globbing familiar to shell users. Queries have the following
> format:
>
> ```
> attribute == value
> ```
>
> where `attribute` is a standard metadata attribute or a custom metadata
> attribute defined by an importer.
>
> For example, to query Spotlight for all the files authored by "Steve"
> the query would look like the following:
> ```
> kMDItemAuthors ==[c] "Steve"
> ```
>
> Comparison operators
>
> +--------------------------------------+--------------------------------------+
> | Operator                             | Description                          |
> +======================================+======================================+
> | `==`                                 | equal                                |
> +--------------------------------------+--------------------------------------+
> | `!=`                                 | not equal                            |
> +--------------------------------------+--------------------------------------+
> | `<`                                  | less than (available for numeric     |
> |                                      | values and dates only)               |
> +--------------------------------------+--------------------------------------+
> | `>`                                  | greater than (available for numeric  |
> |                                      | values and dates only)               |
> +--------------------------------------+--------------------------------------+
> | `<=`                                 | less than or equal (available for    |
> |                                      | numeric values and dates only)       |
> +--------------------------------------+--------------------------------------+
> | `>=`                                 | greater than or equal (available for |
> |                                      | numeric values and dates only)       |
> +--------------------------------------+--------------------------------------+
> | `InRange(attributeName,minValue,maxV | numeric values within the range of   |
> | alue)`                               | minValue through maxValue in the     |
> |                                      | specified attributeName              |
> +--------------------------------------+--------------------------------------+


> Using the $time variable you can restrict a search to find only files that have
> been changed in the last week using the following query:
>
> ```
> ((kMDItemAuthors ==[c] "Dave" || kMDItemAuthors[c] == "Steve") &&
>  (kMDItemContentType == "public.audio" || kMDItemContentType == "public.video")) &&
>  (kMDItemFSContentChangeDate == $time.this_week(-1))
> ```
