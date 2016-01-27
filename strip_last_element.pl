#!/usr/bin/perl

while($line = <>){
    $line =~ /^(.*) \S+/;
    print "$1\n";
}
