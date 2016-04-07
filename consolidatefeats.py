#!/usr/bin/python

# The following file structure is assumed:
# output
# |-incorrect_deps_test
#   > oracle.out.feats
#  |-split1
#    > parser.beam.out.chartfeats
# |-incorrect_deps
#   > oracle.out.feats
#  |-split1
#  ...
#  |-splitN
#    > parser.beam.out.chartfeats
# scripts
# > consolidatefeats.py (this script)

# The following files will be created:
# output
# |-incorrect_deps_test
#   > feats_correct
#   > feats_incorrect
# |-incorrect_deps
#   > feats_correct
#   > feats_incorrect

import sys
import os
import re

WORKING_DIR = "../output/incorrect_deps/"
CORRECT_FEATS_FILE = "../output/incorrect_deps/oracle.out.feats"

NUM_CHUNKS = 10

CONVERT_MAX = 10
CONVERT_MIN = 3
UNCONVERT_MAX = (2 * CONVERT_MAX) - 2
UNCONVERT_MIN = (2 * CONVERT_MIN) - 2

# classified as correct if feat > CORRECT_THRESHOLD
CORRECT_THRESHOLD = 0

# classfied as incorrect if feat < INCORRECT_THRESHOLD
INCORRECT_THRESHOLD = 1

if len(sys.argv) > 1:
    if sys.argv[1] == "test":
        NUM_CHUNKS = 1
        WORKING_DIR = "../output/incorrect_deps_test/"
        CORRECT_FEATS_FILE = "../output/incorrect_deps_test/oracle.out.feats"
    else:
        NUM_CHUNKS = int(sys.argv[1])

feats = dict()

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

def add(feat, inc):
    if feat != "":
        if feat in feats:
            feats[feat] += inc
        else:
            feats[feat] = inc

with open(WORKING_DIR + "feats_correct", "w") as output_correct_feats_file, \
     open(WORKING_DIR + "feats_incorrect", "w") as output_incorrect_feats_file, \
     open(CORRECT_FEATS_FILE, "r") as correct_feats_file:

    while correct_feats_file.readline().startswith("#"):
        pass

    correct_feats_sents = convert_lines(correct_feats_file.read()).split("\n\n")[:-1]

    print("Number of sentences in correct_feats: " + str(len(correct_feats_sents)))

    correct_feats_sent_ptr = 0

    for i in range(1, NUM_CHUNKS+1):
        with open(WORKING_DIR + "split" + str(i) + "/oracle.out.chartfeats", "r") as chart_feats_file:

            while chart_feats_file.readline().startswith("#"):
                pass

            chart_feats_sents = convert_lines(chart_feats_file.read()).split("\n\n")[:-1]

            print("Number of sentences in chart feats (split " + str(i) + "): " + str(len(chart_feats_sents)))

            for chart_feat_sent in chart_feats_sents:
                print("Processing sentence " + str(correct_feats_sent_ptr+1))
                chart_feats = chart_feat_sent.split("\n")

                correct_feats = correct_feats_sents[correct_feats_sent_ptr].split("\n")

                for incorrect_feat in set(chart_feats) - set(correct_feats):
                    add(incorrect_feat, -1)

                for correct_feat in set(correct_feats):
                    add(correct_feat, 1)

                correct_feats_sent_ptr += 1

    output_correct_feats_file.write("#\n\n")
    output_incorrect_feats_file.write("#\n\n")

    print "Writing out feats"

    correct_count = 0
    incorrect_count = 0
    tie_count = 0

    for feat, value in sorted(feats.iteritems(), key=lambda x: x[1]):
        if value > CORRECT_THRESHOLD:
            correct_count += 1
            output_correct_feats_file.write(feat + " 1 " + str(value) + "\n")
        else if value < INCORRECT_THRESHOLD:
            if value == 0:
                tie_count += 1
            incorrect_count += 1
            output_incorrect_feats_file.write(feat + " 0 " + str(value) + "\n")

    print "Correct feats: " + str(correct_count)
    print "Incorrect feats: " + str(incorrect_count)
    print "Tied feats: " + str(tie_count)
