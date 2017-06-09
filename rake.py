#!/usr/bin/env python3

# Implementation of RAKE - Rapid Automatic Keyword Extraction algorithm
# as described in:
#
# Rose, S., D. Engel, N. Cramer, and W. Cowley (2010). 
#
# Automatic keyword extraction from individual documents. 
#
# In M. W. Berry and J. Kogan (Eds.),
#       Text Mining: Applications and Theory.unknown: John Wiley and Sons, Ltd.

import re
import operator
from pathlib import Path
import sys
import argparse

parser = argparse.ArgumentParser(description =
    "Simple example for RAKE: Rapid Automatic Keyword Extraction algorithm.",
    epilog = "File prefixes are present if more than one file is specified.")
parser.add_argument("filenames", nargs='*', help="Input file(s) to use")
parser.add_argument("--stopwords", "-s", nargs="?", metavar="STOPWORDS.TXT",
    default="~/.stopwords.txt", help="The stopword file to use. Defaults to ~/.stopwords.txt")
parser.add_argument("--debug", help="Enable additional debugging", action="store_true")
parser.add_argument("--test", help="Perform integrated testing", action="store_true")
parser.add_argument("--keywords", "-n", nargs="?", metavar="MAX_RETURNED", default="10",
    help="Number of keywords to return")
parser.add_argument("--soft-wrap", help="new-lines mark end-of-sentence", action="store_true",
    default=True, dest="softwrap")
parser.add_argument("--hard-wrap", help="new-lines do not mark end-of-sentence",
    action="store_false", dest="softwrap")
parser.add_argument("--flip", action="store_true",
    help="Flip the order so that the keyword is before the filename.")
parser.add_argument("--group", "-g", action="store_true",
    help="Prefer group-common keywords for the set of documents")
parser.add_argument("--tight-group", "-G", action="store_true", dest="tightgroup",
    help="Use a tight group with keyword: file1, file2, ...")

def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words
    @param stop_word_file Path and file name of a file containing stop words.
    @return list A list of stop words.
    """
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


def separate_words(text, min_word_return_size):
    """
    Utility function to return a list of all words that are have a length greater than a specified number of characters.
    @param text The text that must be split in to words.
    @param min_word_return_size The minimum no of characters a word must have to be included.
    """
    splitter = re.compile(r"[^a-zA-Z0-9_+/'-]")
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words


def split_sentences(text, softwrap=False):
    """
    Utility function to return a list of sentences.
    @param text The text that must be split in to sentences.
    """
    need_nl=""
    space_or_tab=r"\t"
    if softwrap:
        need_nl=r"\n"
        space_or_tab=r"\s\s\s+"
    sentence_delimiters = re.compile(r'''[\[\].!?,;:"()''' + need_nl + "\u2019\u2013" + r''']|'\s|\s-\s|--+|''' + space_or_tab)
    sentences = sentence_delimiters.split(text)
    return sentences


def build_stop_word_regex(stop_word_file_path):
    stop_word_list = load_stop_words(stop_word_file_path)
    stop_word_regex_list = []
    for word in stop_word_list:
        word_regex = r'\b' + word + r"(?![a-zA-Z0-9_+/'-])"
        stop_word_regex_list.append(word_regex)
    stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
    return stop_word_pattern


def generate_candidate_keywords(sentence_list, stopword_pattern):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "":
                phrase_list.append(phrase)
    return phrase_list


def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        #if word_list_degree > 3: word_list_degree = 3 #exp.
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  #orig.
            #word_degree[word] += 1/(word_list_length*1.0) #exp.
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    # Calculate Word scores = deg(w)/frew(w)
    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  #orig.
    #word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
    return word_score


def generate_candidate_keyword_scores(phrase_list, word_score):
    keyword_candidates = {}
    for phrase in phrase_list:
        keyword_candidates.setdefault(phrase, 0)
        word_list = separate_words(phrase, 0)
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates


class Rake(object):
    def __init__(self, stop_words_path, *, softwrap = False):
        self.stop_words_path = stop_words_path
        self._stop_words_pattern = build_stop_word_regex(stop_words_path)
        self.softwrap = softwrap

    def run(self, text):
        sentence_list = split_sentences(text, softwrap=self.softwrap) 
        phrase_list = generate_candidate_keywords(sentence_list, self._stop_words_pattern) 
        word_scores = calculate_word_scores(phrase_list) 
        keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores) 
        sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_keywords


def test_it(debug):
    text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types of systems and systems of mixed types."

    # Split text into sentences
    sentenceList = split_sentences(text, softwrap=True)
    #stoppath = "FoxStoplist.txt" #Fox stoplist contains "numbers", so it will not find "natural numbers" like in Table 1.1
    stoppath = "SmartStoplist.txt"  #SMART stoplist misses some of the lower-scoring keywords in Figure 1.5, which means that the top 1/3 cuts off one of the 4.0 score words in Table 1.1
    stopwordpattern = build_stop_word_regex(stoppath)

    # generate candidate keywords
    phraseList = generate_candidate_keywords(sentenceList, stopwordpattern)

    # calculate individual word scores
    wordscores = calculate_word_scores(phraseList)

    # generate candidate keyword scores
    keywordcandidates = generate_candidate_keyword_scores(phraseList, wordscores)
    if debug: print(keywordcandidates)

    sortedKeywords = sorted(keywordcandidates.items(), key=operator.itemgetter(1), reverse=True)
    if debug: print(sortedKeywords)

    totalKeywords = len(sortedKeywords)
    if debug: print(totalKeywords)
    print(sortedKeywords[0:(totalKeywords // 3)])

    rake = Rake("SmartStoplist.txt")
    keywords = rake.run(text)
    print(keywords)


def perform_once(stopwords, filename, *, softwrap=False):
    filepath = Path(filename)
    stopwords = Path(stopwords).expanduser()
    text = filepath.read_text()
    if not softwrap:
        text = text.replace("\n", " ")
    rake = Rake(str(stopwords), softwrap=softwrap)
    keywords = rake.run(text)
    return keywords


def main(args):
    prefix=""
    count = int(args.keywords)
    for filename in args.filenames:
        if len(args.filenames) > 1:
            prefix=filename + ":"
        keywords = perform_once(args.stopwords, filename, softwrap=args.softwrap) 
        for keyword in keywords[:count]:
            if not args.flip:
                print(prefix + keyword[0])
            else:
                print(keyword[0], ":", filename)

def toss(what):
    raise RuntimeError(what)

def prefer_group(args):
    count = int(args.keywords)
    values = {}
    keyword_map = {}
    output = {}
    for filename in args.filenames:
        for keyword in perform_once(args.stopwords, filename, softwrap=args.softwrap): 
            if filename not in output:
                output[filename] = [keyword[0]]
            if keyword[1] == 0:
                continue
            if keyword[0] not in keyword_map:
                keyword_map[keyword[0]] = [(keyword[1], filename)]
            else:
                keyword_map[keyword[0]].append((keyword[1], filename))
    keywords = sorted(keyword_map.items(), key=lambda x: len(x[1]) * sum(list(zip(*x[1]))[0]), reverse=True)
    for keyword in keywords[:min(len(keywords), count * len(args.filenames))]:
        keypairs = list(zip(*keyword[1]))
        buf = keyword[0] + " : "
        first = True
        if len(keypairs[1]) == 1:
            continue
        for fn in keypairs[1]:
            if not first:
                buf = buf + ", " + fn
            else:
                buf = buf + fn
                first = False
            if keyword[0] not in output[fn]:
                output[fn].append(keyword[0])
        if args.tightgroup:
            print(buf)
            buf = ""

    if args.tightgroup:
        pass
    else:
        for filename in sorted(output):
            prefix=filename + ":" 
            for keyword in output[filename]:
                if not args.flip:
                    print(prefix + keyword)
                else:
                    print(keyword, ":", filename)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.test:
        test_it(args.debug)
    elif args.group or args.tightgroup:
        prefer_group(args)
    else:
        main(args)

