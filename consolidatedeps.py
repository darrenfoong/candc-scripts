#!/usr/bin/python

# The following file structure is assumed:
# data
# > wsj02-21.ccgbank_deps
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

if len(sys.argv) > 1:
    NUM_CHUNKS = int(sys.argv[1])

deps = dict()

def canonize(dep):
    # need to strip indices and possibly add additional dep info
    return dep

def add(dep, inc):
    dep = dep[:-1]
    if dep != "":
        dep = canonize(dep)
        if dep in deps:
            deps[dep] += inc
        else:
            deps[dep] = inc

with open(WORKING_DIR + "deps_correct", "w") as output_correct_deps_file, \
     open(WORKING_DIR + "deps_incorrect", "w") as output_incorrect_deps_file
     open("../data/wsj02-21.ccgbank_deps", "r") as correct_deps_file:

    while correct_deps_file.readline().startswith("#"):
        pass

    correct_deps_sents = correct_deps_file.read().split("\n\n")[:-1]

    print("Number of sentences in correct_deps:" + str(len(correct_deps)))

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

                for incorrect_dep in incorrect_deps:
                    add(incorrect_dep, -1)

                for correct_dep in correct_deps:
                    add(correct_dep, 1)

                correct_deps_ptr += 1

    output_correct_deps_file.write("#\n\n")
    output_incorrect_deps_file.write("#\n\n")

    print "Writing out deps"

    correct_count = 0
    incorrect_count = 0
    tie_count = 0

    for dep, value in deps.iteritems():
        if value > 0:
            correct_count += 1
            output_correct_deps_file.write(dep + " 1\n")
        else:
            if value == 0:
                tie_count += 1
            incorrect_count += 1
            output_incorrect_deps_file.write(dep + " 0\n")

    print "Correct deps: " + str(correct_count)
    print "Incorrect deps: " + str(incorrect_count)
    print "Tied deps: " + str(tie_count)
