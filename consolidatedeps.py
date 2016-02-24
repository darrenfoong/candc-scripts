#!/usr/bin/python

# The following file structure is assumed:
# data
# |-gold
#   > wsj02-21.ccgbank_deps
# output
# |-incorrect_deps
#  |-split1
#  ...
#  |-splitN
#    > parser.beam.out (optional)
#    > parser.beam.out.chartdeps
# scripts
# > consolidatedeps.py (this script)

# The following files will be created:
# output
# |-incorrect_deps
#   > deps_correct
#   > deps_incorrect

import sys
import os
import re

WORKING_DIR = "../output/incorrect_deps/"

NUM_CHUNKS = 10

CONVERT_MAX = 10
CONVERT_MIN = 3
UNCONVERT_MAX = (2 * CONVERT_MAX) - 2
UNCONVERT_MIN = (2 * CONVERT_MIN) - 2

if len(sys.argv) > 1:
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

def canonize(dep, pos_tags):
    # need to strip indices and possibly add additional dep info
    dep_values = dep.split(" ")
    head = dep_values[0].split("_")
    dependent = dep_values[3].split("_")
    dep_values[0] = "_".join(head[:-1])
    dep_values[3] = "_".join(dependent[:-1])
    dep_values[4] = abs(dependent - head)
    dep_values[5] = pos_tags[head]
    dep_values[6] = pos_tags[dependent]
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
     open("../data/gold/wsj02-21.ccgbank_deps", "r") as correct_deps_file, \
     open("../data/gold/wsj02-21.stagged.reformat", "r") as gold_supertags_file:

    while correct_deps_file.readline().startswith("#"):
        pass

    while gold_supertags_file.readline().startswith("#"):
        pass

    correct_deps_sents = convert_lines(correct_deps_file.read()).split("\n\n")[:-1]
    gold_supertags_sents = convert_lines(gold_supertags_file.read()).split("\n\n")[:-1]

    print("Number of sentences in correct_deps: " + str(len(correct_deps_sents)))

    correct_deps_sent_ptr = 0

    for i in range(1, NUM_CHUNKS+1):
        with open(WORKING_DIR + "split" + str(i) + "/parser.beam.out.chartdeps", "r") as incorrect_deps_file:

            while incorrect_deps_file.readline().startswith("#"):
                pass

            incorrect_deps_sents = incorrect_deps_file.read().split("\n\n")[:-1]

            print("Number of sentences in incorrect deps (split " + str(i) + "): " + str(len(incorrect_deps_sents)))

            for incorrect_dep_sent in incorrect_deps_sents:
                incorrect_deps = incorrect_dep_sent.split("\n")
                correct_deps = correct_deps_sents[correct_deps_sent_ptr].split("\n")
                gold_supertags = gold_supertags_sents[correct_deps_sent_ptr].split("\n")

                pos_tags = map((lambda e: e.split(" ")[1]), gold_supertags)

                for incorrect_dep in set(incorrect_deps):
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
        if value > 0:
            correct_count += 1
            output_correct_deps_file.write(dep + " 1 " + str(value) + "\n")
        else:
            if value == 0:
                tie_count += 1
            incorrect_count += 1
            output_incorrect_deps_file.write(dep + " 0 " + str(value) + "\n")

    print "Correct deps: " + str(correct_count)
    print "Incorrect deps: " + str(incorrect_count)
    print "Tied deps: " + str(tie_count)
