`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Modes of Operation
==================
Unsorted notes on overall program operation and usability.

#### Revisions
* 2017-10-01 --- `jonasjberg` Initial
* 2017-11-10 --- `jonasjberg` Redefine `automagic` vs. "default"
* 2017-11-15 --- `jonasjberg` Add additional options


Current Plans
=============
Help text from version `v0.4.7` (commit 870725bb6e17580d6dc4d0d3ded59c7d081):

> Operating mode:
>
>   --automagic           Enable AUTOMAGIC MODE. Try to perform renames without
>                         user interaction by matching the given paths against
>                         available rules. The information provided by the
>                         highest ranked rule is used when performing any
>                         actions on that path. The user might still be asked to
>                         resolve any uncertainties. Use the "--batch" option to
>                         force non-interactive mode and skip paths with
>                         unresolved queries.
>
>   --interactive         (DEFAULT) Enable INTERACTIVE MODE. User selects which
>                         of the analysis results is to make up the new
>                         filename.
>
>   --batch               Enable BATCH MODE. Ignores any and all queries, does
>                         not require any user interaction. Suitable for
>                         scripting, etc.


Due to the fact that both `--interactive` and `--batch` has been missing and
completely unimplemented until very recently, any differences between the modes
has not been at all obvious.

The plan has been the same for quite som time. High-level Goals:

* __Try to do "the right" thing__

    * Primarily through configuration rules but also hopefully other heuristics
      for finding most suitable candidates, implemented in the "analyzers".

* __Let the user run the program in different *operating modes*__

    * __Non-interactive/"batch"__ --- For scripting and executing as an
      external program from E.G.  file managers, etc.
    * __Interactive__ --- Some kind of user control, primarily a command-line
      interface. *Maybe allow adding on other GUI wrappers in the future?*


Operating Modes
===============
Initial draft on options and intended interactions.


### `(default)`
Try to rename by using the highest ranked configuration rule.

Ask the user about any uncertainties, warnings, unresolved data, etc.

* __Name Template__ --- If the rule matching does not result in a valid name
  template: __ask the user__.

* __Template Fields__ --- If any name templates fields are not mapped to data
  sources, or the mapped sources are missing or incompatible: __ask the user__.

### `--batch`
Try to rename by using the highest ranked configuration rule.

Do not interact with the user at all.

* __Name Template__ --- If the rule matching does not result in a valid name
  template: __skip the file__.

* __Template Fields__ --- If any name templates fields are not mapped to data
  sources, or the mapped sources are missing or incompatible: __skip the file__.

### `--interactive`
Try to rename by using the highest ranked configuration rule.

Leave all choices to the user.

* __Name Template__ --- Ask the user which rule (containing a name template) or
  name template to use.

* __Template Fields__ --- Ask the user which data sources (or rule containing
  data sources) to use.

### `--automagic`
Try to rename by using the highest ranked configuration rule or any other
available means; "heuristics", etc.

Ask the user about any uncertainties, warnings, unresolved data, etc.

* __Name Template__ --- If the rule matching does not result in a valid name
  template: __ask the user__.

* __Template Fields__ --- If any name templates fields are not mapped to data
  sources, or the mapped sources are missing or incompatible: __ask the user__.

### `--automagic` and `--batch`
Try to rename by using the highest ranked configuration rule or any other
available means; "heuristics", etc.

Do not interact with the user at all.

* __Name Template__ --- If the rule matching does not result in a valid name
  template: __skip the file__.

* __Template Fields__ --- If any name templates fields are not mapped to data
  sources, or the mapped sources are missing or incompatible: __skip the file__.

### `--automagic` and `--interactive`
Try to rename by using the highest ranked configuration rule or any other
available means; "heuristics", etc.

Have the user confirm everything and make all choices.

* __Name Template__ --- Like `--automagic` but have the user confirm everything.
* __Template Fields__ --- Like `--automagic` but have the user confirm everything.


Breakdown of the Operating Modes
================================
Going with the above operating modes, the program modes control two aspects of
program operation; `method` and `user interaction`.


"Method"
--------
Rule-matching is is currently always enabled.
The "automagic" mode essentially means "try harder" --- enables using all
available means to come up with *something*.

* `--rulematch` --- (Default: ENABLED) Use rule-matching.
* `--automagic` --- Try everything to come up with *something*.  
  First do rule-matching, then do whatever else.
  Given at least one piece of candidate data per name template field,
  this should not fail.

### Examples

| Started with command-line                | Rule-matching | Automagic Mode |
|:-----------------------------------------|---------------|----------------|
| `autonameow`                             | ENABLED       | Disabled       |
| `autonameow --rulematch`                 | ENABLED       | Disabled       |
| `autonameow --automagic`                 | ENABLED       | ENABLED        |
| `autonameow --rulematch --automagic`     | ENABLED       | ENABLED        |


"User Interaction"
------------------
The amount of (required) user interaction can be one of three levels;

0. `--batch` --- No user interaction. For scripting, etc.
1. `--timid` --- (Default: ENABLED) Ask the user if something cannot be
   resolved, to confirm uncertainties, warnings, etc.
2. `--interactive` --- Ask the user about just about everything.

### Examples
The following table uses `P=N%` to indicate how probable it is that an
automatic choice would be correct or that sufficient data is available to make
a choice. For instance; choosing from a single possible option would be
`P=100%`, while a choice without any possible options would be `P=0%`.
The point here is about user interaction, NOT to describe workings of
probabilities, heuristics, analysis, etc..

Choice could be any judgement call related to how files are renamed.


| Started with command-line  | Warnings       | Choice (`P=0%`) | Choice (`P=100%`) |
|:---------------------------|----------------|-------------------------------------|
| `autonameow`               | Ask the user   | Ask the user    | Use most likely   |
| `autonameow --timid`       | Ask the user   | Ask the user    | Use most likely   |
| `autonameow --batch`       | ABORT          | ABORT           | Use most likely   |
| `autonameow --interactive` | Ask the user   | Ask the user    | Ask the user      |


Interaction of "Method" and "User Interaction"
----------------------------------------------
The following table uses "Rule-matching" with percentages where `P=0%` refers
cases where none of the rules apply or the highest ranked rule scored below the
threshold (0?) and `P=100%` cases where a "best matched" rule is found.

Automagic with `P=0%` are cases where the automagic routines failed to come up
with required information and `P=100%` cases where the automagic mode came up
with unambiguous candidate data.


### Examples

| Started with command-line                              | Rule-matching (`P=0%`) | Rule-matching (`P=100%`) | Automagic (`P=0%`) | Automagic (`P=100%`) |
|:-------------------------------------------------------|------------------------|--------------------------|--------------------|----------------------|
| `autonameow`                                           | Ask the user           | Use best matched rule    | *N/A*              | *N/A*                |
| `autonameow --rulematch`                               | Ask the user           | Use best matched rule    | *N/A*              | *N/A*                |
| `autonameow --automagic`                               | Try to resolve missing | Use best matched rule    | Ask the user       | Use most likely      |
| `autonameow --rulematch --automagic`                   | Try to resolve missing | Use best matched rule    | Ask the user       | Use most likely      |
| `autonameow --timid --rulematch`                       | Ask the user           | Use best matched rule    | *N/A*              | *N/A*                |
| `autonameow --timid --automagic`                       | Try to resolve missing | Use best matched rule    | Ask the user       | Use most likely      |
| `autonameow --timid --rulematch --automagic`           | Try to resolve missing | Use best matched rule    | Ask the user       | Use most likely      |
| `autonameow --batch --rulematch`                       | ABORT                  | Use best matched rule    | *N/A*              | *N/A*                |
| `autonameow --batch --automagic`                       | Try to resolve missing | Use best matched rule    | ABORT              | Use most likely      |
| `autonameow --batch --rulematch --automagic`           | Try to resolve missing | Use best matched rule    | ABORT              | Use most likely      |
| `autonameow --interactive --rulematch`                 | Ask the user           | Ask the user             | *N/A*              | *N/A*                |
| `autonameow --interactive --automagic`                 | Ask the user           | Ask the user             | Ask the user       | Ask the user         |
| `autonameow --interactive --rulematch --automagic`     | Ask the user           | Ask the user             | Ask the user       | Ask the user         |

