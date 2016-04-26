#!/usr/bin/perl
#
# Java C&C Parser
# Copyright (c) Stephen Clark, James R. Curran and Darren Foong
#
# This software is covered by a BSD 2-Clause License.
# See LICENCE for the full text of the licence.

# takes a ccgbank_deps file and replaces each word_index element with
# just the index

$deps_file = $ARGV[0];
open(DEPS, $deps_file) || die("can't open deps file\n");

print "# generated by remove_words.pl script\n";

while($line = <DEPS>){
    if ($line =~ /^\# / || $line =~ /^$/){
	print "$line";
	next;
    }
    @items = split(' ',$line);

    $word_id = $items[0];
    $word_id =~ /\S+\_(\d+)/;
    print "$1 ";

    print "$items[1] $items[2] ";

    $word_id = $items[3];
    $word_id =~ /\S+\_(\d+)/;
    print "$1\n";
}
