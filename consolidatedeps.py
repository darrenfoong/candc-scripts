#!/usr/bin/python

# The following file structure is assumed:
# data
# |-gold
#   > wsj00.ccgbank_deps
#   > wsj00.stagged.reformat
#   > wsj02-21.ccgbank_deps
#   > wsj02-21.stagged.reformat
# output
# |-incorrect_deps_test
#  |-split1
#    > parser.beam.out.chartdeps
# |-incorrect_deps
#  |-split1
#  ...
#  |-splitN
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

WORKING_DIR = "../output/incorrect_deps/"
CORRECT_DEPS_FILE = "../data/gold/wsj02-21.ccgbank_deps"
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
    if sys.argv[1] == "test":
        NUM_CHUNKS = 1
        WORKING_DIR = "../output/incorrect_deps_test/"
        CORRECT_DEPS_FILE = "../data/gold/wsj00.ccgbank_deps"
        GOLD_SUPERTAGS_FILE = "../data/gold/wsj00.stagged.reformat"
    else:
        NUM_CHUNKS = int(sys.argv[1])

deps = dict()

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

MARKUP = re.compile(r'<[0-9]>|\{[A-Z_]\*?\}|\[X\]')

def strip_markup(dep):
    if dep != "":
        dep_values = dep.split(" ")[:-1]
        category = MARKUP.sub("", dep_values[1])
        if category[0] == "(":
            category = category[1:-1]
        dep_values[1] = category
        return " ".join(dep_values)
    else:
        return dep

def canonize(dep, pos_tags):
    dep_values = dep.split(" ")
    head = dep_values[0].split("_")
    dependent = dep_values[3].split("_")
    head_index = int(head[-1]) - 1
    dependent_index = int(dependent[-1]) - 1

    dep_values[0] = "_".join(head[:-1])
    dep_values[3] = "_".join(dependent[:-1])
    dep_values.append(str(abs(head_index - dependent_index)))
    dep_values.append(pos_tags[head_index])
    dep_values.append(pos_tags[dependent_index])

    dep = " ".join(dep_values)
    return dep

def add(dep, inc, pos_tags):
    if dep != "":
        dep = canonize(dep, pos_tags)
        if dep in deps:
            deps[dep] += inc
        else:
            deps[dep] = inc

with open(WORKING_DIR + "deps_correct", "w") as output_correct_deps_file, \
     open(WORKING_DIR + "deps_incorrect", "w") as output_incorrect_deps_file, \
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
                chart_deps = map((lambda e: strip_markup(e)), chart_deps)

                correct_deps = correct_deps_sents[correct_deps_sent_ptr].split("\n")
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
        if value > CORRECT_THRESHOLD:
            correct_count += 1
            output_correct_deps_file.write(dep + " 1 " + str(value) + "\n")
        else if value < INCORRECT_THRESHOLD:
            if value == 0:
                tie_count += 1
            incorrect_count += 1
            output_incorrect_deps_file.write(dep + " 0 " + str(value) + "\n")

    print "Correct deps: " + str(correct_count)
    print "Incorrect deps: " + str(incorrect_count)
    print "Tied deps: " + str(tie_count)
