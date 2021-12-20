#!/usr/bin/perl

use Data::Dumper;

my $h;

chomp(my $FSM_URLBASE = `. /etc/tis-clone.cfg; echo \$FSM_URLBASE`);

# Generate indexes for all the toc.html files
foreach my $TOC_HTML (sort(`find $FSM_URLBASE -name toc.html`)) {
	chomp($TOC_HTML);
	chomp(my $TOC_URI = $TOC_HTML);
	chomp(my $TEST=$FSM_URLBASE);
	$TOC_URI=~s/$TEST\///g;
	chomp (my $DOCNAME = `head -2 $TOC_HTML | tail -1`);
	chomp (my $INDEX_HTML = `echo $TOC_URI|sed -e 's/toc.html\$/index.html/g'`);
	$h->{"$DOCNAME"} = $INDEX_HTML;
}

# Add indexes for the wiring diagrams
foreach my $DOC (sort(`find $FSM_URLBASE/t3Portal/external/en/ewdappu -name termdata.xml`)) {
	my $TITLE;
	chomp($DOC);
	open (FH, "<", $DOC) or next;
	while (<FH>) {
		if ($_ =~ /pubtitle/) {
			chomp($TITLE = $_);
			$TITLE=~s/<pubtitle>//g;
			$TITLE=~s/<\/pubtitle>//g;
			chop($TITLE);
			last;
		}
	}
	my $FULLPATH = $DOC;
	$FULLPATH=~s/\/xhtml\/termdata.xml//g;
	my (@bits) = split(/\//, $FULLPATH);
	my $EWDNUM = $bits[$#bits];
	chomp($EWDNUM);
	$h->{$TITLE} = "t3Portal/ewdappu/index.jsp?ewdNo=". $EWDNUM ."&locale=en&t3id=". $EWDNUM ."_INTRO01";
}

# Then print the sorted list
print '<head><link rel="stylesheet" href="/framework/bootstrap.min.css"></head>
<body style="padding:0px; margin:0px;">
<img src="t3Portal/resources/images/globals/header/headerbar.bg.blu.gif" style="width:100%; height:40px; margin:0px; border:0px; padding:0px">
<div class="nav-link">
';
foreach my $k (sort(keys %{$h})) {
	print "<a href='/". $h->{$k} ."'>". $k ."</a><br>\n";
}
print '</div></body>';
