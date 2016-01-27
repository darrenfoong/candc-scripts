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
#    > parser.beam.out.incorrect
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
CCG = False

if len(sys.argv) > 1:
    NUM_CHUNKS = int(sys.argv[1])

if len(sys.argv) > 2 and sys.argv[2] == "ccg":
    CCG = True

deps = dict()

with open(WORKING_DIR + "deps_correct", "w") as output_correct_deps_file, \
     open(WORKING_DIR + "deps_incorrect", "w") as output_incorrect_deps_file:

    def correct_deps_file_path(i):
        if CCG:
            return "../data/wsj02-21.ccgbank_deps"
        else:
            return WORKING_DIR + "split" + str(i) + "/parser.beam.out"

    for i in range(1, NUM_CHUNKS+1):
        with open(correct_deps_file_path(i), "r") as correct_deps_file, \
             open(WORKING_DIR + "split" + str(i) + "/parser.beam.out.incorrect", "r") as incorrect_deps_file:

            if (CCG and i == 1) or (not CCG):
                print "Reading correct deps"

                while correct_deps_file.readline().startswith("#"):
                    pass

                for line in correct_deps_file:
                    # need to check that preface has been read
                    line = line[:-1]
                    if line != "":
                        if line in deps:
                            deps[line] += 1
                        else:
                            deps[line] = 1

            print "Reading incorrect deps"

            while incorrect_deps_file.readline().startswith("#"):
                pass

            for line in incorrect_deps_file:
                # need to check that preface has been read
                line = line[:-1]
                if line != "":
                    if line in deps:
                        deps[line] -= 1
                    else:
                        deps[line] = -1

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
