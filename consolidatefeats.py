#!/usr/bin/python

# The following file structure is assumed:
# output
# |-incorrect_feats
#   > oracle.out.feats
#   > parser.beam.out.chartfeats
# |-incorrect_feats_dev
#   > oracle.out.feats
#   > parser.beam.out.chartfeats
# |-incorrect_feats_test
#   > oracle.out.feats
#   > parser.beam.out.chartfeats
# scripts
# > consolidatefeats.py (this script)

# The following files will be created:
# output
# |-incorrect_feats
#   > feats_correct
#   > feats_incorrect
# |-incorrect_feats_dev
#   > feats_correct
#   > feats_incorrect
# |-incorrect_feats_test
#   > feats_correct
#   > feats_incorrect

import sys
import os
import re
import itertools

WORKING_DIR = "../output/incorrect_feats/"

if len(sys.argv) > 1:
    if sys.argv[1] == "dev":
        WORKING_DIR = "../output/incorrect_feats_dev/"
    elif sys.argv[1] == "test":
        WORKING_DIR = "../output/incorrect_feats_test/"

CORRECT_FEATS_FILE = WORKING_DIR + "/oracle.out.feats"
CHART_FEATS_FILE = WORKING_DIR + "/parser.beam.out.chartfeats"

CONVERT_MAX = 10
CONVERT_MIN = 3
UNCONVERT_MAX = (2 * CONVERT_MAX) - 2
UNCONVERT_MIN = (2 * CONVERT_MIN) - 2

# classified as correct if feat > CORRECT_THRESHOLD
CORRECT_THRESHOLD = 0

# classfied as incorrect if feat < INCORRECT_THRESHOLD
INCORRECT_THRESHOLD = 1

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
        if feat not in feats:
            feats[feat] = (0, 0)

        pos, neg = feats[feat]
        if inc == 1:
            feats[feat] = (pos+1, neg)
        else:
            feats[feat] = (pos, neg+1)

with open(WORKING_DIR + "feats_correct", "w") as output_correct_feats_file, \
     open(WORKING_DIR + "feats_incorrect", "w") as output_incorrect_feats_file, \
     open(CORRECT_FEATS_FILE, "r") as correct_feats_file, \
     open(CHART_FEATS_FILE, "r") as chart_feats_file:

    while correct_feats_file.readline().startswith("#"):
        pass

    while chart_feats_file.readline().startswith("#"):
        pass

    correct_feats_sents = convert_lines(correct_feats_file.read()).split("\n\n")[:-1]
    chart_feats_sents = convert_lines(chart_feats_file.read()).split("\n\n")[:-1]

    print("Number of sentences in correct_feats: " + str(len(correct_feats_sents)))
    print("Number of sentences in chart_feats: " + str(len(chart_feats_sents)))

    correct_feats_sent_ptr = 0

    for chart_feat_sent in chart_feats_sents:
        print("Processing sentence " + str(correct_feats_sent_ptr+1))

        chart_feats = chart_feat_sent.split("\n")
        correct_feats = correct_feats_sents[correct_feats_sent_ptr].split("\n")[:-1]

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
        pos, neg = value

        for _ in itertools.repeat(None, pos):
            output_correct_feats_file.write(feat + " 1 " + str(pos) + "\n")
        for _ in itertools.repeat(None, neg):
            output_incorrect_feats_file.write(feat + " 0 " + str(neg) + "\n")

        correct_count += pos
        incorrect_count += neg

    print "Correct feats: " + str(correct_count)
    print "Incorrect feats: " + str(incorrect_count)
    print "Tied feats: " + str(tie_count)
