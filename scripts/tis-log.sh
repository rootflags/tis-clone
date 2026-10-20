#!/bin/sh
#
# Log everything a script prints.  Sourced by the tis-clone scripts right after tis-clone.cfg:
#
#     . ${SCRIPT_BASE}/tis-log.sh
#
# The first script of a run starts itself again with its output (stdout and stderr) going both to the
# terminal and to the end of $TIS_LOG (default: $DOWNLOAD_TO/tis-clone.log), between a start line and an
# exit status line.  Scripts it runs see TIS_LOGGING and don't log a second time.  tis-fetch.py and
# tis-serve.py do the same through tislog.py.
#
# Scripts whose output is data (build-index.pl, build-pdfidx.sh, toc2html, ...) don't use this.
#

if [ -z "${TIS_LOGGING}" ]; then
	TIS_LOGGING=1
	PYTHONUNBUFFERED=1
	export TIS_LOGGING PYTHONUNBUFFERED
	TIS_LOG=${TIS_LOG:-${DOWNLOAD_TO}/tis-clone.log}
	mkdir -p `dirname "${TIS_LOG}"`
	# The log can mention your account (masked) and login responses, so keep it private
	( umask 077; touch "${TIS_LOG}" )
	TIS_RC=`mktemp "${TISTMPDIR:-/tmp}/tis-log.XXXXXX"`
	echo "===== `date '+%Y-%m-%d %H:%M:%S'` start: $0 $*" >> "${TIS_LOG}"
	# Ctrl-C reaches the script itself; wait for it to finish (a trap, unlike ignoring the signal, isn't
	# passed on to the script).  tee -i keeps logging the script's last words.
	trap ':' INT
	{ trap ':' INT; "$0" "$@" 2>&1; echo $? > "${TIS_RC}"; } | tee -ia "${TIS_LOG}"
	RC=`cat "${TIS_RC}" 2>/dev/null`
	rm -f "${TIS_RC}"
	echo "===== `date '+%Y-%m-%d %H:%M:%S'` exit ${RC:-?}: $0 $*" >> "${TIS_LOG}"
	exit ${RC:-1}
fi
