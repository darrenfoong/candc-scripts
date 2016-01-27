#!/usr/bin/python

# The following file structure is assumed:
# output
# |-incorrect_deps
#   > deps_correct
#   > deps_incorrect

# The following files will be created:
# data
# |-deps
#  |-split1
#  ...
#  |-splitN
#   |-train
#     > deps_correct.train.splitN
#     > deps_incorrect.train.splitN
#   |-test
#     > deps_correct.test.splitN
#     > deps_incorrect.test.splitN

import sys
import os
import math
import re

WORKING_DIR = "../output/incorrect_deps/"
OUTPUT_DIR = "../data/deps/"

NUM_CHUNKS = 10

if len(sys.argv) > 1:
    NUM_CHUNKS = int(sys.argv[1])

input_file_paths = ["deps_correct", "deps_incorrect"]

os.mkdir(OUTPUT_DIR)

for i in range(1, NUM_CHUNKS+1):
    os.mkdir(OUTPUT_DIR + "split" + str(i))
    os.mkdir(OUTPUT_DIR + "split" + str(i) + "/train")
    os.mkdir(OUTPUT_DIR + "split" + str(i) + "/test")

for input_file_path in input_file_paths:
    with open(WORKING_DIR + input_file_path, "r") as input_file:
        print "Reading preface"

        while input_file.readline().startswith("#"):
            pass

        inputs = input_file.readlines()

        deps_per_chunk = int(math.ceil(len(inputs)/float(NUM_CHUNKS)))

        print "Splitting file"

        for i in range(1, NUM_CHUNKS+1):
            print "Processing split " + str(i) + "; ",

            start = (i-1) * deps_per_chunk
            end = start + deps_per_chunk

            left_start = 0
            left_end = start

            right_start = end
            right_end = len(inputs)

            preface = ["#\n\n"]
            input_outer = preface + inputs[left_start:left_end] + inputs[right_start:right_end]
            input_inner = preface + inputs[start:end]

            print(str(len(input_outer)-1) + ", " + str(len(input_inner)-1))

            with open(OUTPUT_DIR + "split" + str(i) + "/train/" + input_file_path + ".train.split" + str(i), "w") as output_train_file, \
                 open(OUTPUT_DIR + "split" + str(i) + "/test/" + input_file_path + ".test.split" + str(i), "w") as output_test_file:

                output_train_file.write("".join(input_outer))
                output_test_file.write("".join(input_inner))
