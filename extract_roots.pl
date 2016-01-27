#!/usr/bin/perl

$c = 1;
while(<>){
    if(/^\#\#\#/){
	$line = <>;
	$line =~ /^\S+ \*\*\* (\S+) /;
	print "$1\n";

	print "$c EMPTY!\n" if ($1 eq "");
	$c++;
    }
}
