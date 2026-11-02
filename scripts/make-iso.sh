#!/bin/sh
#
# Make an ISO image (ie: for a DVD or USB stick) of the downloaded website
#
# The image holds everything in FSM_URLBASE (the website, and the PDFs if made), and is written to
# $DOWNLOAD_TO/NAME.iso with spaces as _.  NAME is also the disc's label (cut to the 32 characters a label
# can have).  Without NAME, it's the vehicle the manuals are for (ie: "TOYOTA 2013-2018 RAV4"), or
# "Toyota FSM" if the folder has more than one vehicle.  Needs mkisofs, genisoimage or xorriso.
#
# Usage:
#   make-iso.sh [NAME]
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if which mkisofs > /dev/null 2>&1; then
	MKISOFS=mkisofs
elif which genisoimage > /dev/null 2>&1; then
	MKISOFS=genisoimage
elif which xorriso > /dev/null 2>&1; then
	MKISOFS="xorriso -as mkisofs"
else
	echo "$0 needs mkisofs, genisoimage or xorriso; install one (ie: apt install genisoimage)"
	exit 1
fi

cd ${FSM_URLBASE} || exit 1

NAME="$*"
if [ "x${NAME}" = x ]; then
	# The vehicle(s) of the repair, body/collision and new car features manuals and the wiring diagrams
	VEHICLES=`find t3Portal/external/en/rm t3Portal/external/en/cr t3Portal/external/en/ncf -mindepth 2 \
		-maxdepth 2 -name toc.xml 2>/dev/null; ls t3Portal/external/en/ewdappu/*/xhtml/termdata.xml 2>/dev/null`
	NAME=`for F in ${VEHICLES}; do ${SCRIPT_BASE}/toc2topic.py ${F}; done | sort -u`
	case "${NAME}" in
		"") echo "No manuals found in ${FSM_URLBASE}; give a NAME"; exit 1 ;;
		*"
"*) echo "This folder has more than one vehicle, so it's labelled \"Toyota FSM\" (give a NAME to change it)"
			NAME="Toyota FSM" ;;
	esac
fi
LABEL=`printf '%s' "${NAME}" | cut -c1-32`
ISO=${DOWNLOAD_TO}/`printf '%s' "${NAME}" | tr -c 'A-Za-z0-9._-' _`.iso

echo "Making ${ISO} (label \"${LABEL}\") from ${FSM_URLBASE}"
# Rock Ridge and Joliet (long names), and ISO level 3 for files over 4 GB
${MKISOFS} -o "${ISO}.part" -R -J -joliet-long -iso-level 3 -V "${LABEL}" -m '*.part' . &&
	mv -f "${ISO}.part" "${ISO}" && echo "Done: ${ISO}" && exit 0
rm -f "${ISO}.part"
echo "Making the ISO failed (see above)"
exit 1
