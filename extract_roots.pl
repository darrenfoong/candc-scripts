#!/usr/bin/perl


$pipe_file = $ARGV[0];
open(PIPE, $pipe_file) || die("can't open pipe file\n");

print "# obtained by running extract_roots.pl on $pipe_file\n\n";

$c = 1;
while(<PIPE>){
    if(/^\#\#\#/){
        $line = <PIPE>;
        $line =~ /^\S+ \*\*\* (\S+) /;
        die "$c EMPTY!\n" if ($1 eq "");

        $cat = $1;
        if($cat =~ /[\/\\]/){
            $cat = "($cat)";
        }
        print "$cat\n";

        $c++;
    }
}
