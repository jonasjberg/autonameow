# `autonameow`

--------------------------------------------------------------------------------


TODO-list
=========
List of things that need to be done.

### Architecture
- [ ] Decide on how to "bundle" all information (date, title, etc.) relating 
      to a file. Probably a dictionary. Maybe a class or "enum-like" type?
- [ ] Decide on a data format for extracted pieces of metadata.
      Example: One piece of extracted date/time-information would store the
               date/time itself as a datetime-object. It should probably also
               keep track of the source -- who found this piece of information?
               As well as a "weight" or some kind of metric that approximates
               how reliable the information is, I.E. how probable is it that it
               is correct? Note that the "correctness" is entirely context-specific; 
               datetime for a pdf-document would be correct if it matches the
               time of the document release.

    ```python
    file_info = { 'title': 'The Cats Mjaowuw', 
                  'author': 'Gibson',
                  'publisher': None,
                  'edition': None,
                  'dateandtime': [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                                     'source': pdf_metadata,
                                     'comment': "Create date",
                                     'weight': 1 },
                                   { 'datetime': datetime.datetime(2010, 1, 2, 34, ..),
                                     'source': pdf_metadata,
                                     'comment': "Modify date",
                                     'weight': 0.8 } ],
                  'tags': ['cat', 'best'] }
    ```


### Bugs
- [x] Some of the date/time-information gets lost on the way to the new pretty
      output from `print_all_datetime_info(self)`.
- [x] Duplicate date/time from pdf metadata printed out by 
      `print_all_datetime_info(self)`. Not sure if the problem is in the data
      or inte the presentation ..
      

### Wishlist
- [ ] Use configuration file(s) for settings program options.
    - [ ] Define file name templates.
    - [ ] Customized pattern matching.
    - [ ] Allow tweaking parser results sorting and ranking.
- [ ] GUI. Use the CLI base code as an API.

