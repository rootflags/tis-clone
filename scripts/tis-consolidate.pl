#!/usr/bin/perl 
#
# Merge docs into your local website
#

use Data::Dumper; 

my $VER = "18X0U";
my $WEBSITE_BASE = "/www/html/tis/";
my $BASE = "$WEBSITE_BASE/TOYOTA/LAND_CRUISER/em${VER}/PDFs";
my $GS = "gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dNOPAUSE -dBATCH";
chdir ($BASE) || die "$BASE does not exist.  Create it or update $0 with the correct location";

my $v = require "nav.html"; 

my $h;
foreach my $x (@{$v}) { 
	my $section = @{$x}[0]; 
	$section=~s/[_\/]//g;
	$section=~s/ //g;

	push(@sections, $section);
	foreach my $part (@{$x}) {
		foreach my $subpart (@{$part}) {
			foreach my $micropart (@{$subpart}) {
				if (ref($micropart) eq "ARRAY") {
					my $doc = @{$micropart}[1];
					$doc=~s/\.html.*$/.pdf/g;
					my (@folders) = split(/\//, $doc);
					my $pdf = pop(@folders);
					push(@{$h->{$section}}, $pdf);
				}
			}
		}
	}
}

chdir("$WEBSITE_BASE/t3Portal/document/rm/RM${VER}/xhtml");

foreach my $title (@sections) {
	my $CMD="$GS -sOutputFile=$BASE/RepairManual-$title.pdf ". join(" ", @{$h->{$title}});
	print "Running $CMD\n";
	`$CMD`;
}
