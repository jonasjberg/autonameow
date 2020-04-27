`autonameow`
============
*Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------

Analyzing Filenames
===================
Notes on extracting metadata from filenames.

#### Revisions
* 2017-09-17 --- `jonasjberg` Initial.


Identify Fields in Strings
--------------------------
This is touched on in this TODO-list entry;

> * `[TD0019]` Rework the `FilenameAnalyzer`
>     * `[TD0020]` Identify data fields in file names.
>         ```
>         screencapture-github-jonasjberg-autonameow-1497964021919.png
>         ^___________^ ^__________________________^ ^___________^
>              tag            title/description        timestamp
>         ```
>         * Use some kind of iterative evaluation; split into parts at
>           separators, assign field types to the parts and find a "best fit".
>           Might have to try several times at different separators, re-evaluting
>           partials after assuming that some part is a given type, etc.
>         * __This is a non-trivial problem__, I would rather not re-implement
>           existing solutions poorly.
>         * Look into how `guessit` does it or possibility of modifying
>           `guessit` to identify custom fields.


### Ideas on Methods
Possible strategies for mapping fields to parts of strings.

#### Dates likely unique (date+time even more so)
Use the fact that probable dates, especially date+time; are likely to be
unique in a given context.

Given this example string, find fields `{datetime}` and `{whatever_}`:
```
2017-09-17 17092017
```

A fuzzy date-parser might identify two `YYYY-MM-DD` date-patterns in this
string, like so;

```
2017-09-17 17092017
YYYY-MM-DD DDMMYYYY
```
With only this information, we have two equally likely candidates for the
`{datetime}` field, and two equally unlikely candidates for the `{whatever_}`
field. Additional information is required ..

The context could be a common parent directory.
Lets say that there are multiple files in the same directory, we got two
example strings;
```
2017-09-17 17092017
2017-10-22 17092017
```

Now, if one were to apply the rule that date/time-strings are more likely
unique, the common substring `17092017` would be deemed less likely to be the
date/time-part.

#### Common "creator"/"artist"
Given a number of strings from a shared context, shared substrings are probably
often worth weighting.

__This should be done depending on context.__
*More stuff taken into account --> better accuracy.*

For example, trying to find fields `{artist}` and `{title}` given the strings;
```
Beatles, The - Paperback Writer.flac
Beatles, The - Getting Better.flac
```

Common substrings related to music files are probably more likely __artists__,
__albums__, etc.  And they are probably less likely to be song titles.

These assumptions will obviously prove incorrect a lot of times.

Applying the rule that `{artist}` is likely found in all/multiple files in a
given context;

```
Beatles The - Paperback Writer.flac
{ creator }   {    title     }


Beatles The - Getting Better.flac
{ creator }   {   title    }
```


### Programming by Wishful Thinking
Some yet non-existing system tries to identify specified fields in a given
string. Returns a list of substrings, sorted by score/ranking/weight.

```python
string = 'The Beatles - Paperback Writer.flac'

result = identify_fields(string, [field.Creator, field.Title])

assert result[fields.Creator] == ['The Beatles', 'Paperback Writer', 'flac',
                                  ' - ', '.']
assert result[fields.Title]   == ['Paperback Writer', 'The Beatles', 'flac',
                                  ' - ', '.']
```

Specifying __constraints__ or __rules__ --- require that both fields contain
at least one word character;
```python
string = 'The Beatles - Paperback Writer.flac'

add_constraint(field.Creator, matches=r'[\w]+')
add_constraint(field.Title, matches=r'[\w]+')
result = identify_fields(string, [field.Creator, field.Title])

assert result[fields.Creator] == ['The Beatles', 'Paperback Writer', 'flac']
assert result[fields.Title]   == ['Paperback Writer', 'The Beatles', 'flac']
```
