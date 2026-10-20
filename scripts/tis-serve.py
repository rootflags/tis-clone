#!/usr/bin/env python3
#
# tis-serve.py - Serve the downloaded FSM locally for browsing
#
# Output (including each request) is also logged, see tis-log.sh.
#
# Like "python3 -m http.server", but serves the .jsp pages saved from TIS as HTML (they are plain HTML,
# with nothing to run on the server) and sends .svgz with Content-Encoding: gzip so browsers unpack it.
#
# Usage:
#   tis-serve.py [-p PORT] [-b ADDRESS] [FOLDER]      FOLDER defaults to $FSM_URLBASE, PORT to 8080
#                                                     (or the next free port if it's in use)
#

import argparse, errno, functools, http.server, os, subprocess, sys

from tislog import tee_to_log

PORT_TRIES = 100


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map, **{
        ".jsp": "text/html", ".do": "text/html", ".xsl": "text/xml", ".svg": "image/svg+xml",
        ".svgz": "image/svg+xml", ".js": "text/javascript", ".xml": "text/xml",
    })

    def end_headers(self):
        if self.path.split("?")[0].lower().endswith(".svgz"):
            self.send_header("Content-Encoding", "gzip")
        super().end_headers()


def start_server(folder, bind="", port=8080, handler=Handler):
    """An HTTP server for folder on port, or the next free port above it.  tis-pdfbook.py uses this too"""
    for p in range(port, port + PORT_TRIES):
        try:
            return http.server.ThreadingHTTPServer((bind, p), functools.partial(handler, directory=folder))
        except OSError as e:
            if e.errno != errno.EADDRINUSE:
                raise
    sys.exit("Ports %d to %d are all in use" % (port, port + PORT_TRIES - 1))


def main():
    ap = argparse.ArgumentParser(description="Serve the downloaded FSM over HTTP")
    ap.add_argument("folder", nargs="?", help="folder to serve (default: $FSM_URLBASE from ~/.tis/tis-clone.cfg)")
    ap.add_argument("-p", "--port", type=int, default=8080)
    ap.add_argument("-b", "--bind", default="", help="address to listen on (default: all)")
    args = ap.parse_args()

    names = ["FSM_URLBASE", "DOWNLOAD_TO", "TIS_LOG"]
    out = subprocess.run(["sh", "-c", '. "$1"; printf "%s\\0" "$FSM_URLBASE" "$DOWNLOAD_TO" "$TIS_LOG"', "sh",
                          os.path.expanduser("~/.tis/tis-clone.cfg")], capture_output=True, text=True).stdout
    cfg = dict(zip(names, out.split("\0")))
    if cfg.get("DOWNLOAD_TO"):
        tee_to_log(cfg)                 # requests show up in the log too
    folder = args.folder or cfg.get("FSM_URLBASE")
    if not folder or not os.path.isdir(folder):
        sys.exit("No folder to serve (%r)" % folder)

    server = start_server(folder, args.bind, args.port)
    port = server.server_address[1]
    if port != args.port:
        print("Port %d is in use, using %d" % (args.port, port))
    print("Serving %s at http://%s:%d/  (Ctrl-C to stop)" % (folder, args.bind or "localhost", port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
