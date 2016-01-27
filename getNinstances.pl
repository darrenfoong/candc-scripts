#!/usr/bin/perl

$NUM_INSTANCES = 100;
$i = 0;
while($line = <>){
    if($line =~ /^\# /){
	print "$line";
    }elsif($i <= $NUM_INSTANCES){
    	print "$line";
    }
    $i++ if($line =~ /^$/);
}
