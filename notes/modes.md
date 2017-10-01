Notes on "Operating Modes"
==========================
Jonas Sjöberg, 2017-10-01.

Unsorted notes on overall modes of program operation.


Current Plans
-------------
Help text from version `v0.4.7` (commit 870725bb6e17580d6dc4d0d3ded59c7d081):

> Operating mode:
>   --automagic           Enable AUTOMAGIC MODE. Try to perform renames without
>                         user interaction by matching the given paths against
>                         available rules. The information provided by the
>                         highest ranked rule is used when performing any
>                         actions on that path. The user might still be asked to
>                         resolve any uncertainties. Use the "--batch" option to
>                         force non-interactive mode and skip paths with
>                         unresolved queries.
>   --interactive         (DEFAULT) Enable INTERACTIVE MODE. User selects which
>                         of the analysis results is to make up the new
>                         filename.
>   --batch               Enable BATCH MODE. Ignores any and all queries, does
>                         not require any user interaction. Suitable for
>                         scripting, etc.


Due to the fact that both `--interactive` and `--batch` has been missing and
completely unimplemented until very recently, any differences between the modes
has not been at all obvious.

The plan has been the same for quite som time. High-level Goals:

* Let the user run the program in different *operating modes*
* Provide different means of controlling and accessing the program core.
* Provide a "hands-off" 
