#!/usr/bin/perl

# puts each word|pos|supertag triple on a separate line

while($line = <>){
    if($line =~ /^$/){
	print("# plus the reformat_stagged script\n\n");
	next;
    }
    if($line =~ /^\# /){
	print "$line";
	next;
    }
    @items = split(' ', $line);
    foreach $item (@items){
	$item =~ /(\S+)\|(\S+)\|(\S+)/;
	print "$1 $2 $3\n";
    }
    print "\n";
}
