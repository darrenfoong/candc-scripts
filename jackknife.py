#!/usr/bin/python

# The following file structure is assumed:
# data
# |-auto-stagged
#   > wsj02-21.stagged.0.01.100.all
# |-gold
#   > wsj02-21.gold_deps
#   > wsj02-21.roots
# |-oracle-gold
#   > wsj02-21.oracle_deps.0.01.100.all
#   > wsj02-21.oracle_deps.0.01.100.all.per_cell
# |-incorrect_deps -|
#  |-split1         |-- will be created by this script
#  ...              |
#  |-splitN        -|
# scripts
# > jackknife.py (this script)

# In each incorrect_deps/splitN, the following files will be created:
# splitN
# > wsj02-21.oracle_deps.0.01.100.all.splitN
# > wsj02-21.oracle_deps.0.01.100.all.splitN.per_cell
# > wsj02-21.stagged.0.01.100.all.splitN
# > wsj02-21.stagged.0.01.100.all.splitN.parse
# > wsj02-21.roots.splitN
# > wsj02-21.gold_deps.splitN

# This program accepts four optional arguments:
# jackknife.py [<num_chunks> <num_sentences> [<input_file> <deps_file> <roots_file>]]

import sys
import os
import math
import re

WORKING_DIR = "../data/"
OUTPUT_DIR = "../data/incorrect_deps/"
input_file_base = "wsj02-21.stagged.0.01.100.all"
deps_file_base = "wsj02-21.oracle_deps.0.01.100.all"
roots_file_base = "wsj02-21.roots"
gold_deps_file_base = "wsj02-21.gold_deps"

input_file_path = WORKING_DIR + "auto-stagged/" + input_file_base
deps_file_path = WORKING_DIR + "oracle-gold/" + deps_file_base
deps_per_cell_file_path = WORKING_DIR + "oracle-gold/" + deps_file_base + ".per_cell"
roots_file_path = WORKING_DIR + "gold/" + roots_file_base
gold_deps_file_path = WORKING_DIR + "gold/" + gold_deps_file_base

NUM_CHUNKS = 10
NUM_SENTENCES = 39604

CONVERT_MAX = 10
CONVERT_MIN = 3
UNCONVERT_MAX = (2 * CONVERT_MAX) - 2
UNCONVERT_MIN = (2 * CONVERT_MIN) - 2

if len(sys.argv) > 2:
    NUM_CHUNKS = int(sys.argv[1])
    NUM_SENTENCES = int(sys.argv[2])

if len(sys.argv) == 8:
    input_file_path = sys.argv[3]
    deps_file_path = sys.argv[4]
    deps_per_cell_file_path = sys.argv[5]
    roots_file_path = sys.argv[6]
    gold_deps_file_path = sys.argv[7]
    input_file_base = os.path.basename(input_file_path)
    deps_file_base = os.path.basename(deps_file_path)
    deps_per_cell_file_base = os.path.basename(deps_per_cell_file_path)
    roots_file_base = os.path.basename(roots_file_path)
    gold_deps_file_base = os.path.basename(gold_deps_file_path)

sentences_per_chunk = int(math.ceil(NUM_SENTENCES/float(NUM_CHUNKS)))

with open(input_file_path, "r") as input_file, \
     open(deps_file_path, "r") as deps_file, \
     open(deps_per_cell_file_path, "r") as deps_per_cell_file, \
     open(roots_file_path, "r") as roots_file, \
     open(gold_deps_file_path, "r") as gold_deps_file:

    print "Reading prefaces"

    while input_file.readline().startswith("#"):
        pass
    while deps_file.readline().startswith("#"):
        pass
    while deps_per_cell_file.readline().startswith("#"):
        pass
    while roots_file.readline().startswith("#"):
        pass
    while gold_deps_file.readline().startswith("#"):
        pass

    print "Splitting files"

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

    inputs = convert_lines(input_file.read()).split("\n\n")[:-1]
    deps = convert_lines(deps_file.read()).split("\n\n")[:-1]
    deps_per_cell = convert_lines(deps_per_cell_file.read()).split("\n\n")[:-1]
    roots = roots_file.read().splitlines();
    gold_deps = convert_lines(gold_deps_file.read()).split("\n\n")[:-1]

    if len(inputs) != NUM_SENTENCES:
        raise InputError("Number of sentences read: " + str(len(inputs)))
    if len(deps) != NUM_SENTENCES:
        raise InputError("Number of deps read: " + str(len(deps)))
    if len(deps_per_cell) != NUM_SENTENCES:
        raise InputError("Number of deps per cell read: " + str(len(deps_per_cell)))
    if len(roots) != NUM_SENTENCES:
        raise InputError("Number of roots read: " + str(len(roots)))
    if len(gold_deps) != NUM_SENTENCES:
        raise InputError("Number of gold deps read: " + str(len(roots)))

    print "Making " + OUTPUT_DIR

    os.mkdir(OUTPUT_DIR)

    for i in range(1, NUM_CHUNKS+1):
        print "Processing split " + str(i) + "; ",
        os.mkdir(OUTPUT_DIR + "split" + str(i))

        start = (i-1) * sentences_per_chunk
        end = start + sentences_per_chunk

        left_start = 0
        left_end = start

        right_start = end
        right_end = NUM_SENTENCES

        preface = ["#"]
	empty_line = [""]
        input_outer = preface + inputs[left_start:left_end] + inputs[right_start:right_end] + empty_line
        input_inner = preface + inputs[start:end] + empty_line
        deps_outer = preface + deps[left_start:left_end] + deps[right_start:right_end] + empty_line
        deps_per_cell_outer = preface + deps_per_cell[left_start:left_end] + deps_per_cell[right_start:right_end] + empty_line
        roots_outer = ["#\n"] + roots[left_start:left_end] + roots[right_start:right_end] + empty_line
        gold_deps_outer = preface + gold_deps[left_start:left_end] + gold_deps[right_start:right_end] + empty_line

        print(str(len(input_outer)-2) + ", " + str(len(input_inner)-2) + ", " + str(len(input_outer)+len(input_inner)-4))

        with open(OUTPUT_DIR + "split" + str(i) + "/" + input_file_base + ".split" + str(i), "w") as output_input_file, \
             open(OUTPUT_DIR + "split" + str(i) + "/" + input_file_base + ".split" + str(i) + ".parse", "w") as output_input_parse_file, \
             open(OUTPUT_DIR + "split" + str(i) + "/" + deps_file_base + ".split" + str(i), "w") as output_deps_file, \
             open(OUTPUT_DIR + "split" + str(i) + "/" + deps_file_base + ".split" + str(i) + ".per_cell", "w") as output_deps_per_cell_file, \
             open(OUTPUT_DIR + "split" + str(i) + "/" + roots_file_base + ".split" + str(i), "w") as output_roots_file, \
             open(OUTPUT_DIR + "split" + str(i) + "/" + gold_deps_file_base + ".split" + str(i), "w") as output_gold_deps_file:

            output_input_file.write(unconvert_lines("\n\n".join(input_outer)))
            output_input_parse_file.write(unconvert_lines("\n\n".join(input_inner)))
            output_deps_file.write(unconvert_lines("\n\n".join(deps_outer)))
            output_deps_per_cell_file.write(unconvert_lines("\n\n".join(deps_per_cell_outer)))
            output_roots_file.write("\n".join(roots_outer))
            output_gold_deps_file.write(unconvert_lines("\n\n".join(gold_deps_outer)))
