#!/usr/bin/perl

$stagged_file = $ARGV[0];
$deps_file = $ARGV[1];

open(STAGGED, $stagged_file || die("can't open stagged file\n"));
open(DEPS, $deps_file) || die("can't open deps file\n");

$line = <STAGGED>;
$line = <STAGGED>;
$line = <STAGGED>;

$line2 = <DEPS>;
print("$line2");
$line2 = <DEPS>;
print("$line2");
$line2 = <DEPS>;
print("$line2");

while($line = <STAGGED>){
    @stags = split(' ',$line);
    $line2 = <DEPS>;
    while($line2 ne "\n"){
	($hi, $lc, $s, $fi) = split(' ',$line2);

	$index = $hi - 1;
	$item = $stags[$index];
	@items = split('\|',$item);
	$head = $items[0];

	$index = $fi - 1;
	$item = $stags[$index];
	@items = split('\|',$item);
	$filler = $items[0];

	print("$head\_$hi $lc $s $filler\_$fi\n");
	$line2 = <DEPS>;
    }
    print("\n");
}
