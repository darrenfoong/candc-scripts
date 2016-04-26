#!/usr/bin/python

# The following file structure is assumed:
# data
# |-gold
#   > wsj00.stagged.reformat
#   > wsj02-21.stagged.reformat
#   > wsj23.stagged.reformat
# output
# |-incorrect_deps
#   > oracle.out
#  |-split1
#  ...
#  |-splitN
#    > parser.beam.out.chartdeps
# |-incorrect_deps_dev
#   > oracle.out
#  |-split1
#    > parser.beam.out.chartdeps
# |-incorrect_deps_test
#   > oracle.out
#  |-split1
#    > parser.beam.out.chartdeps
# scripts
# > consolidatedeps.py (this script)

# The following files will be created:
# output
# |-incorrect_deps_test
#   > deps_correct
#   > deps_incorrect
# |-incorrect_deps
#   > deps_correct
#   > deps_incorrect

import sys
import os
import re
import itertools

WORKING_DIR = "../output/incorrect_deps/"
CORRECT_DEPS_FILE = WORKING_DIR + "/oracle.out"
GOLD_SUPERTAGS_FILE = "../data/gold/wsj02-21.stagged.reformat"

NUM_CHUNKS = 10

CONVERT_MAX = 10
CONVERT_MIN = 3
UNCONVERT_MAX = (2 * CONVERT_MAX) - 2
UNCONVERT_MIN = (2 * CONVERT_MIN) - 2

# classified as correct if dep > CORRECT_THRESHOLD
CORRECT_THRESHOLD = 0

# classfied as incorrect if dep < INCORRECT_THRESHOLD
INCORRECT_THRESHOLD = 1

if len(sys.argv) > 1:
    if sys.argv[1] == "dev":
        NUM_CHUNKS = 1
        WORKING_DIR = "../output/incorrect_deps_dev/"
        CORRECT_DEPS_FILE = WORKING_DIR + "/oracle.out"
        GOLD_SUPERTAGS_FILE = "../data/gold/wsj00.stagged.reformat"
    elif sys.argv[1] == "test":
        NUM_CHUNKS = 1
        WORKING_DIR = "../output/incorrect_deps_test/"
        CORRECT_DEPS_FILE = WORKING_DIR + "/oracle.out"
        GOLD_SUPERTAGS_FILE = "../data/gold/wsj23.stagged.reformat"
    else:
        NUM_CHUNKS = int(sys.argv[1])

deps = dict()
categories = dict()
categories_strip = dict()

def convert_lines(f):
    # replaces empty entries with blank lines
    for i in range(CONVERT_MAX, CONVERT_MIN-1, -1):
        current = "\n" * i
        repl = "[CONVERT " + str(i) + "]"
        f = f.replace(current, repl)
    for i in range(CONVERT_MAX, CONVERT_MIN-1, -1):
        current = "[CONVERT " + str(i) + "]"
        repl = "\n" * ((2 * i) -2)
        f = f.replace(current, repl)
    return f

def unconvert_lines(f):
    # replaces blank lines with empty entries
    for i in range(UNCONVERT_MAX, UNCONVERT_MIN-1, -2):
        current = "\n" * i
        repl = "[UNCONVERT " + str(i) + "]"
        f = f.replace(current, repl)
    for i in range(UNCONVERT_MAX, UNCONVERT_MIN-1, -2):
        current = "[UNCONVERT " + str(i) + "]"
        repl = "\n" * ((i/2) + 1)
        f = f.replace(current, repl)
    return f

def get_pos_tag(pos_tags, index):
    if index < 0:
        return "START"
    elif index >= len(pos_tags):
        return "END"
    else:
        return pos_tags[index]

IGNORE = set(map(lambda x: tuple(x.split()), filter(lambda x: not x.startswith("#"), r"""
rule_id 7
rule_id 11
rule_id 12
rule_id 14
rule_id 15
rule_id 16
rule_id 17
rule_id 51
rule_id 52
rule_id 56
rule_id 91
rule_id 92
rule_id 95
rule_id 96
rule_id 98
conj 1 0
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 0
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 2
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 3
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 6
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 9
((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 6
((S[b]{_}\NP{Y}<1>){_}/PP{Z}<2>){_} 1 6
(((S[b]{_}\NP{Y}<1>){_}/PP{Z}<2>){_}/NP{W}<3>){_} 1 6
(S[X]{Y}/S[X]{Y}<1>){_} 1 13
(S[X]{Y}/S[X]{Y}<1>){_} 1 5
(S[X]{Y}/S[X]{Y}<1>){_} 1 55
((S[X]{Y}/S[X]{Y}){Z}\(S[X]{Y}/S[X]{Y}){Z}<1>){_} 2 97
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 4
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 93
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 8
((S[X]{Y}\NP{Z}){Y}/(S[X]{Y}<1>\NP{Z}){Y}){_} 2 94
((S[X]{Y}\NP{Z}){Y}/(S[X]{Y}<1>\NP{Z}){Y}){_} 2 18
been ((S[pt]{_}\NP{Y}<1>){_}/(S[ng]{Z}<2>\NP{Y}){Z}){_} 1 0
been ((S[pt]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 there 0
been ((S[pt]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 There 0
be ((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 there 0
be ((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 There 0
been ((S[pt]{_}\NP{Y}<1>){_}/(S[pss]{Z}\NP{Y}){Z}<2>){_} 1 0
been ((S[pt]{_}\NP{Y}<1>){_}/(S[adj]{Z}\NP{Y}){Z}<2>){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[pss]{Z}\NP{Y}){Z}<2>){_} 1 0
have ((S[b]{_}\NP{Y}<1>){_}/(S[pt]{Z}\NP{Y}){Z}<2>){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[adj]{Z}\NP{Y}){Z}<2>){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[ng]{Z}\NP{Y}){Z}<2>){_} 1 0
# be ((S[b]{_}\NP{Y}<1>){_}/(S[pss]{Z}<2>\NP{Y}){Z}){_} 1 0
going ((S[ng]{_}\NP{Y}<1>){_}/(S[to]{Z}<2>\NP{Y}){Z}){_} 1 0
have ((S[b]{_}\NP{Y}<1>){_}/(S[to]{Z}\NP{Y}){Z}<2>){_} 1 0
Here (S[adj]{_}\NP{Y}<1>){_} 1 0
# this is a dependency Julia doesn't have but looks okay
from (((NP{Y}\NP{Y}<1>){_}/(NP{Z}\NP{Z}){W}<3>){_}/NP{V}<2>){_} 1 0
""".strip().split("\n"))))

def ignore(dep):
    (head, category, slot, dependent, rule_id) = dep.split(" ")
    res = ('rule_id', rule_id) in IGNORE or \
          (category, slot, rule_id) in IGNORE or \
          (head, category, slot, rule_id) in IGNORE or \
          (head, category, slot, dependent, rule_id) in IGNORE
    return res

MARKUP = re.compile(r'<[0-9]>|\{[A-Z_]\*?\}|\[X\]')
MARKUP_CAT = re.compile(r'\[.*?\]')

def canonize(dep, pos_tags):
    dep_values = dep.split(" ")[:-1]
    head = dep_values[0].split("_")
    dependent = dep_values[3].split("_")
    head_index = int(head[-1]) - 1
    dependent_index = int(dependent[-1]) - 1

    category = MARKUP.sub("", dep_values[1])
    if category[0] == "(":
        category = category[1:-1]

    if category not in categories:
        categories[category] = 0
    categories[category] += 1

    category_strip = MARKUP_CAT.sub("", category)

    if category_strip not in categories_strip:
       categories_strip[category_strip] = 0
    categories_strip[category_strip] += 1

    dep_values[0] = "_".join(head[:-1])
    # not category_strip because stripping is done in program
    dep_values[1] = category
    dep_values[3] = "_".join(dependent[:-1])
    dep_values.append(str(abs(head_index - dependent_index)))
    dep_values.append(get_pos_tag(pos_tags, head_index))
    dep_values.append(get_pos_tag(pos_tags, dependent_index))

    dep_values.append(get_pos_tag(pos_tags, head_index-1))
    dep_values.append(get_pos_tag(pos_tags, head_index+1))
    dep_values.append(get_pos_tag(pos_tags, dependent_index-1))
    dep_values.append(get_pos_tag(pos_tags, dependent_index+1))

    dep = " ".join(dep_values)
    return dep

def add(dep, inc, pos_tags):
    if dep != "":
        #if ignore(dep):
        #    print "Ignored: " + dep
        #    return

        dep = canonize(dep, pos_tags)
        if dep not in deps:
            deps[dep] = (0, 0)

        pos, neg = deps[dep]
        if inc == 1:
            deps[dep] = (pos+1, neg)
        else:
            deps[dep] = (pos, neg+1)

with open(WORKING_DIR + "deps_correct", "w") as output_correct_deps_file, \
     open(WORKING_DIR + "deps_incorrect", "w") as output_incorrect_deps_file, \
     open(WORKING_DIR + "cats_hist", "w") as cats_hist_file, \
     open(WORKING_DIR + "cats_strip_hist", "w") as cats_strip_hist_file, \
     open(CORRECT_DEPS_FILE, "r") as correct_deps_file, \
     open(GOLD_SUPERTAGS_FILE, "r") as gold_supertags_file:

    while correct_deps_file.readline().startswith("#"):
        pass

    while gold_supertags_file.readline().startswith("#"):
        pass

    correct_deps_sents = convert_lines(correct_deps_file.read()).split("\n\n")[:-1]
    gold_supertags_sents = convert_lines(gold_supertags_file.read()).split("\n\n")[:-1]

    print("Number of sentences in correct_deps: " + str(len(correct_deps_sents)))

    correct_deps_sent_ptr = 0

    for i in range(1, NUM_CHUNKS+1):
        with open(WORKING_DIR + "split" + str(i) + "/parser.beam.out.chartdeps", "r") as chart_deps_file:

            while chart_deps_file.readline().startswith("#"):
                pass

            chart_deps_sents = convert_lines(chart_deps_file.read()).split("\n\n")[:-1]

            print("Number of sentences in chart deps (split " + str(i) + "): " + str(len(chart_deps_sents)))

            for chart_dep_sent in chart_deps_sents:
                print("Processing sentence " + str(correct_deps_sent_ptr+1))
                chart_deps = chart_dep_sent.split("\n")
                correct_deps = correct_deps_sents[correct_deps_sent_ptr].split("\n")[:-1]

                gold_supertags = gold_supertags_sents[correct_deps_sent_ptr].split("\n")
                pos_tags = map((lambda e: e.split(" ")[1]), gold_supertags)

                for incorrect_dep in set(chart_deps) - set(correct_deps):
                    add(incorrect_dep, -1, pos_tags)

                for correct_dep in set(correct_deps):
                    add(correct_dep, 1, pos_tags)

                correct_deps_sent_ptr += 1

    output_correct_deps_file.write("#\n\n")
    output_incorrect_deps_file.write("#\n\n")

    print "Writing out deps"

    correct_count = 0
    incorrect_count = 0
    tie_count = 0

    for dep, value in sorted(deps.iteritems(), key=lambda x: x[1]):
        pos, neg = value
        #if pos > 0:
        #    final_value = pos
        #else:
        #    final_value = pos - neg

        #if final_value > CORRECT_THRESHOLD:
        #    correct_count += 1
        #    output_correct_deps_file.write(dep + " 1 " + str(final_value) + "\n")
        #elif final_value < INCORRECT_THRESHOLD:
        #    if final_value == 0:
        #        tie_count += 1
        #    incorrect_count += 1
        #    output_incorrect_deps_file.write(dep + " 0 " + str(final_value) + "\n")

        for _ in itertools.repeat(None, pos):
            output_correct_deps_file.write(dep + " 1 " + str(pos) + "\n")
        for _ in itertools.repeat(None, neg):
            output_incorrect_deps_file.write(dep + " 0 " + str(neg) + "\n")

        correct_count += pos
        incorrect_count += neg

    print "Correct deps: " + str(correct_count)
    print "Incorrect deps: " + str(incorrect_count)
    print "Tied deps: " + str(tie_count)

    for category, count in sorted(categories.iteritems(), key=lambda x: x[1]):
        cats_hist_file.write(category + " " + str(count) + "\n")

    print "Categories: " + str(len(categories))

    for category_strip, count in sorted(categories_strip.iteritems(), key=lambda x: x[1]):
        cats_strip_hist_file.write(category_strip + " " + str(count) + "\n")

    print "Categories strip: " + str(len(categories_strip))
