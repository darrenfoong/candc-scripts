#!/usr/bin/perl

use POSIX;

$out_dir = $ARGV[0];
$in_file = $ARGV[1];
$total_sents = $ARGV[2];
$NUM_CHUNKS = $ARGV[3];

open(IN_FILE, $in_file || die("can't open in file\n"));

$nsents = ceil($total_sents / $NUM_CHUNKS);
$chunk = 1;

# strip preface
$line = <IN_FILE>;

die("no preface!") if ($line !~ /^#/);
while($line = <IN_FILE>){
    last if($line !~ /^#/);
}

$line = <IN_FILE>;

while($chunk <= $NUM_CHUNKS){
    $in_file =~ /\S+\/(\S+)$/;
    $out_file = $out_dir . "/" . $1 . ".$chunk";
    open(OUT_FILE, '>', $out_file || die("can't open out file\n"));

    print OUT_FILE "$line";

    $line_num = 1;
    while($line = <IN_FILE>){
	if ($line_num < $nsents){
	    print OUT_FILE "$line";
	}else{
	    last;
	}
	$line_num++;
    }
    close(OUT_FILE);
    $chunk++;
}

