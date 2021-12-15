#!/usr/bin/perl

use Data::Dumper;

my $h;

chomp(my $FSM_URLBASE = `. /etc/tis-clone.cfg; echo \$FSM_URLBASE`);

#foreach my $TOC_HTML (`find $FSM_URLBASE -name toc.html | sed -e 's;^$FSM_URLBASE;;g`) {
foreach my $TOC_HTML (sort(`find $FSM_URLBASE -name toc.html`)) {
	chomp($TOC_HTML);
	chomp(my $TOC_URI = $TOC_HTML);
	chomp(my $TEST=$FSM_URLBASE);
	$TOC_URI=~s/$TEST\///g;
	chomp (my $DOCNAME = `head -2 $TOC_HTML | tail -1`);
	chomp (my $INDEX_HTML = `echo $TOC_URI|sed -e 's/toc.html\$/index.html/g'`);
	$h->{"$DOCNAME"} = $INDEX_HTML;
}

foreach my $k (sort(keys %{$h})) {
	print "<a href='/". $h->{$k} ."'>". $k ."</a><br>\n";
}
