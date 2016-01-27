#!/usr/bin/perl

$NUM_INSTANCES = 1000;
$i = 0;
while($line = <>){
    if($line =~ /^\# / || $line =~ /^$/){
	print "$line";
    }elsif($i < $NUM_INSTANCES){
    	print "$line";
	$i++;
    }
}
