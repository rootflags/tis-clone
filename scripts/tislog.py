#
# tislog.py - Log everything a Python script prints, like tis-log.sh does for the shell scripts
#
# tee_to_log(cfg) runs the calling script again with its output going both to the terminal and to the end
# of $TIS_LOG (default: $DOWNLOAD_TO/tis-clone.log), then exits with its exit status.  It does nothing if a
# calling script is already logging (TIS_LOGGING is set).
#

import os
import signal
import subprocess
import sys
import time


def tee_to_log(cfg):
    if os.environ.get("TIS_LOGGING"):
        return
    log = cfg.get("TIS_LOG") or os.path.join(cfg["DOWNLOAD_TO"], "tis-clone.log")
    os.makedirs(os.path.dirname(os.path.abspath(log)), exist_ok=True)
    old = os.umask(0o077)               # the log can mention your account, so keep it private
    open(log, "a").close()
    os.umask(old)

    def mark(what):
        with open(log, "a") as fh:
            fh.write("===== %s %s: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), what, " ".join(sys.argv)))

    env = dict(os.environ, TIS_LOGGING="1", PYTHONUNBUFFERED="1")
    mark("start")
    # Ctrl-C reaches the script itself; wait for it to finish.  A handler (unlike SIG_IGN) isn't inherited.
    signal.signal(signal.SIGINT, lambda *a: None)
    child = subprocess.Popen([sys.executable] + sys.argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    tee = subprocess.Popen(["tee", "-ia", log], stdin=child.stdout)
    child.stdout.close()
    rc = child.wait()
    tee.wait()
    if rc < 0:                          # killed by a signal, report it the way the shell does
        rc = 128 - rc
    mark("exit %d" % rc)
    sys.exit(rc)
