RAKE
====

A Python implementation of the Rapid Automatic Keyword Extraction (RAKE)
algorithm as described in: Rose, S., Engel, D., Cramer, N., & Cowley, W.
(2010). Automatic Keyword Extraction from Individual Documents. In M. W.
Berry & J. Kogan (Eds.), Text Mining: Theory and Applications: John
Wiley & Sons.

The source code is released under the MIT License.

Arguments
~~~~~~~~~

The arguments are as follows::

    usage: rake.py [-h] [--stopwords [STOPWORDS.TXT]] [--debug] [--test]
                   [--keywords [MAX_RETURNED]] [--soft-wrap] [--hard-wrap]
                   [--flip] [--group] [--tight-group]
                   [filenames [filenames ...]]

    Simple example for RAKE: Rapid Automatic Keyword Extraction algorithm.

    positional arguments:
      filenames             Input file(s) to use

    optional arguments:
      -h, --help            show this help message and exit
      --stopwords [STOPWORDS.TXT], -s [STOPWORDS.TXT]
                            The stopword file to use. Defaults to ~/.stopwords.txt
      --debug               Enable additional debugging
      --test                Perform integrated testing
      --keywords [MAX_RETURNED], -n [MAX_RETURNED]
                            Number of keywords to return
      --soft-wrap           new-lines mark end-of-sentence
      --hard-wrap           new-lines do not mark end-of-sentence
      --flip                Flip the order so that the keyword is before the
                            filename.
      --group, -g           Prefer group-common keywords for the set of documents
      --tight-group, -G     Use a tight group with keyword: file1, file2, ...

    File prefixes are present if more than one file is specified.

Notes on this version
~~~~~~~~~~~~~~~~~~~~~

This version needs Python 3+. I have tested it with 3.5.3.
It probably no longer works with Python 2. Folks should upgrade.

The previous version fell apart when it came to contractions.
I'm not sure that the current version is perfect, but for my
initial test data it seems to function.

Original file didn't support arguments, and didn't do anything
useful when it was run. (Same as `--test`.)

Proper hard-wrap support (where new-lines don't implicitly mark the end of
a paragraph) is tricky. This script never did it properly. The `--hard-wrap`
functionality remains broken, though that was the previous-default behavior.
(To do it properly, you need to an initial level of Markdown or reStructuredText
style conversion to meaningfully break it up.)

I extended this because I wanted an automatic way to pull useful topic
information for lyrics.

Example output
~~~~~~~~~~~~~~

When provided one argument::

    $ ./rake.py MIT-License.txt
    documentation files
    permit persons
    person obtaining
    substantial portions
    copyright holders
    copyright notice
    permission notice
    sell copies
    copyright
    copies

When provided more than one argument, it returns `--keywords` responses for
each file and prefixes each with the filename (like `grep`)::

    $ rake.py -n 1 *_lyrics.txt
    01-Thats-the-way_lyrics.txt:future
    02-Eccentric_lyrics.txt:personality disorder
    03-Space-Travel_lyrics.txt:miss fried rice
    04-Rise-and-Fall_lyrics.txt:landing
    05-Theres-a-Dragon-Sleeping_lyrics.txt:roast duck
    .
    .
    .

There's a `--flip` option that will allow you to take a batch of files and
sort them to find keywords in common::

    $ rake.py --flip *_lyrics.txt | sort
    .
    .
    .
    care : 01-Thats-the-way_lyrics.txt
    care : 11-Im-Sorry_lyrics.txt
    care : 29-That-Pickle_lyrics.txt
    .
    .
    . 
    concerned : 41-Mixed-Emotions_lyrics.txt
    considered : 26-Dialog_lyrics.txt
    considered : 48-Purpose-Of-You_lyrics.txt
    continue : 25-Bacon_lyrics.txt
    .
    .
    .

There's a `--group` / `-g` option that tries to find common keywords within a group.
It keeps the top-most keyword for a file, but the others favor the group::

    $ rake.py -g --flip *_lyrics.txt | sort
    afraid overfishing destroys : 12-Mysterious-Things_lyrics.txt
    air : 21-My-Neighbor-Errols-Neighborhood_lyrics.txt
    air : 26-Dialog_lyrics.txt
    alternate pasts : 32-Fate_lyrics.txt
    anymore : 22-Vile_lyrics.txt
    anymore : 46-Conversation_lyrics.txt
    .
    .
    .

There's also a `--tight-group` / `-G` option that returns the results in a more
compact form, and skips the most popular for the file::

    $ rake.py -G *_lyrics.txt | sort
    air : 21-My-Neighbor-Errols-Neighborhood_lyrics.txt, 26-Dialog_lyrics.txt
    anymore : 22-Vile_lyrics.txt, 46-Conversation_lyrics.txt
    ate : 39-Palindrome_lyrics.txt, 44-Lost-In-The-Rain_lyrics.txt
    avoid : 07-Vegetable-Domination_lyrics.txt, 12-Mysterious-Things_lyrics.txt
    back : 03-Space-Travel_lyrics.txt, 37-Surf-Rules_lyrics.txt, 44-Lost-In-The-Rain_lyrics.txt
    bear : 23-Misunderstanding_lyrics.txt, 45-Grandparents_lyrics.txt
    .
    .
    .

