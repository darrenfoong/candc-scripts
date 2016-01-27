#!/usr/bin/perl

while($line = <>){
    if($line =~ /^$/){
#	print("# plus the extract_word_pos script\n\n");
	next;
    }
    if($line =~ /^\# /){
	#print "$line";
	next;
    }
    @items = split(' ', $line);
    $front = 1;
    foreach $item (@items){
#	print(" ") if(!$front); 
	$front = 0;
	$item =~ /(\S+)\|(\S+)\|\S+/;
	print "$1\n";
	print "$2\n";
    }
}
