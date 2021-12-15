#!/usr/bin/perl
#

my $nav_jsp = $ARGV[0];
my $new_nav = $ARGV[1];

for my $line (split(/\n/, `cat $nav_jsp`)) {
	if ($line =~ /var TREE_ITEMS/) { $line = `cat $new_nav`; }
	print $line ."\n";
}
