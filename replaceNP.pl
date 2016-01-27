#!/usr/bin/perl

while($line = <>){
    print $line;
    if($line =~ /^NP (.*)/){
	print "NP[nb] $1\n";
    }
    if($line =~ /^(.*) NP$/){
	print "$1 NP[nb]\n";
    }
    if($line =~ /^N\[num\] (.*)/){
	print "N $1\n";
    }
    if($line =~ /^(.*) N\[num\]$/){
	print "$1 N\n";
    }
}
