#!/usr/bin/env python3
#
# tis-fetch.py - Resumable TIS downloader
#
# Downloads a list of TIS URLs plus the images, stylesheets and scripts each page needs, checking
# every response for signs that the session has died.  TIS ends a session after ~5 hours (or when
# the account logs in elsewhere) and then answers 403 with the login page as the body, or redirects
# to the login page.  When that happens nothing is saved and the download pauses until you press Enter
# (so the 2FA code isn't sent while you're away); then tis-fetch runs tis-login.sh, you type the code
# and it carries on with the same URL.  Without a terminal, with --no-relogin, or if you type q at the
# prompt, it exits 75 and rerunning the same command resumes where it stopped.
#
# Progress is kept in a plain-text MANIFEST (default: $DOWNLOAD_TO/MANIFEST), one line per URL path:
#     STATUS <tab> /t3Portal/path <tab> bytes <tab> time <tab> note
# STATUS is OK, MISSING (404), FORBIDDEN (403 while the session was fine) or FAILED.  The last line
# for a path wins.  OK, MISSING and FORBIDDEN paths are skipped on later runs; FAILED ones are retried,
# unless TIS_SKIP_FAILED=1 is set (tis-clone --continue sets it, to get past files TIS can't send).
# Delete a path's lines (or the whole file) to force a refetch.
#
# Usage:
#   tis-fetch.py URL_OR_PATH ...           ie: tis-fetch.py /t3Portal/external/en/rm/RM30B0U/toc.xml
#   tis-fetch.py -i FILE                   one URL or /t3Portal/... path per line ("-" for stdin)
#   tis-fetch.py --check                   only check that the saved session works (exit 0 or 75)
#
# Exit status: 0 all done, 1 some URLs FAILED, 75 session expired and could not log in again.
#
# Requirements: python3, python3-requests

import argparse
import collections
import html.parser
import os
import re
import subprocess
import sys
import time
import urllib.parse

import requests

from tislog import tee_to_log

TESTPAGE = "/t3Portal/staticcontent/en/techinfo/docs/glossary.pdf"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
EXIT_SESSION = 75

# Signs that TIS sent us to its login page instead of the document we asked for
LOGIN_URL_RE = re.compile(r"concurrentLoginFailure|techInfoPortal/login|/openam/|prelogin", re.I)
LOGIN_BODY_RE = re.compile(rb"Techinfo prelogin|openam/json/realms|concurrentLoginFailure", re.I)

# What a file of each type must start with, to catch an HTML error page saved as an image or PDF
MAGIC = {
    ".pdf": (b"%PDF",),
    ".png": (b"\x89PNG",),
    ".gif": (b"GIF8",),
    ".jpg": (b"\xff\xd8",),
    ".jpeg": (b"\xff\xd8",),
    ".svgz": (b"\x1f\x8b",),
    ".mp4": (b"\x00\x00\x00",),
}
# TIS serves some PNGs as .gif or .jpg (browsers sniff the real type), so any image will do for those
IMAGE_MAGIC = MAGIC[".png"] + MAGIC[".gif"] + MAGIC[".jpg"]
for _ext in (".png", ".gif", ".jpg", ".jpeg"):
    MAGIC[_ext] = IMAGE_MAGIC
HTML_EXT = (".html", ".htm", ".xhtml", ".jsp")
STUB_RE = re.compile(rb"""<script>.*?location\s*=\s*'([^']+)'""", re.S)
DONE = ("OK", "MISSING", "FORBIDDEN")


class SessionDead(Exception):
    pass


def load_cfg():
    """Read settings from ~/.tis/tis-clone.cfg the same way the shell scripts do"""
    names = ["COOKIES", "DOWNLOAD_TO", "FSM_URLBASE", "WEBSITE", "SCRIPT_BASE", "TIS_LOG"]
    script = '. "$HOME/.tis/tis-clone.cfg" && printf "%s\\0" ' + " ".join('"$%s"' % n for n in names)
    out = subprocess.run(["sh", "-c", script], capture_output=True, check=True).stdout
    return dict(zip(names, out.decode().split("\0")))


class LinkParser(html.parser.HTMLParser):
    """Collect the files a page needs to display: images, scripts, stylesheets, backgrounds, and files it
    links to or sends the browser to (Reference Information pages are a script that opens their PDF)"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.in_style = False
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("img", "script", "input", "embed", "source", "frame", "iframe") and a.get("src"):
            self.links.append(a["src"])
        elif tag == "link" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "object" and a.get("data"):
            self.links.append(a["data"])
        elif tag == "a" and a.get("href") and is_file(a["href"]):
            # Follow links to files (PDFs, images, videos) but not to other documents, which are all in toc.xml
            self.links.append(a["href"])
        if a.get("background"):
            self.links.append(a["background"])
        if a.get("style"):
            self.links += css_links(a["style"])
        self.in_style = tag == "style"
        self.in_script = tag == "script"

    def handle_endtag(self, tag):
        self.in_style = self.in_script = False

    def handle_data(self, data):
        if self.in_style:
            self.links += css_links(data)
        elif self.in_script:
            # location="/t3Portal/document/om-s/OM60V70U/pdf/OM60V70U.pdf";
            self.links += [u for u in re.findall(r"""location\s*=\s*["']([^"']+)["']""", data) if is_file(u)]


def is_file(link):
    """A link to a file (PDF, image, video, ...) rather than to another page"""
    ext = os.path.splitext(urllib.parse.urlsplit(link).path.lower())[1]
    return bool(ext) and ext not in HTML_EXT and ext != ".xml"


def css_links(text):
    return re.findall(r"""url\(\s*['"]?([^'")\s]+)""", text) + re.findall(r"""@import\s+['"]([^'"]+)""", text)


class Fetcher:
    def __init__(self, cfg, args):
        self.cfg = cfg
        self.args = args
        self.site = urllib.parse.urlsplit(cfg["WEBSITE"])
        self.root = os.path.realpath(cfg["FSM_URLBASE"])
        self.manifest_path = args.manifest or os.path.join(cfg["DOWNLOAD_TO"], "MANIFEST")
        self.status = self.read_manifest()
        self.manifest = open(self.manifest_path, "a", encoding="utf-8")
        self.http = None
        self.new_session()
        self.counts = collections.Counter()
        self.skip_failed = os.environ.get("TIS_SKIP_FAILED") == "1"
        self.failed = []
        self.since_cookie_save = 0

    # ---- manifest -------------------------------------------------------------------------------

    def read_manifest(self):
        status = {}
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("#") or "\t" not in line:
                        continue
                    f = line.rstrip("\n").split("\t")
                    status[f[1]] = f[0]
        else:
            with open(self.manifest_path, "w", encoding="utf-8") as fh:
                fh.write("# tis-fetch.py manifest: STATUS<tab>PATH<tab>BYTES<tab>TIME<tab>NOTE.  Last line per path wins.\n")
        return status

    def record(self, path, status, size=0, note=""):
        self.status[path] = status
        self.counts[status] += 1
        self.manifest.write("%s\t%s\t%d\t%s\t%s\n" % (status, path, size, time.strftime("%Y-%m-%d %H:%M:%S"), note))
        self.manifest.flush()
        os.fsync(self.manifest.fileno())
        if status == "FAILED":
            self.failed.append(path)
        if not self.args.quiet or status != "OK":
            print("[%-9s] %s%s" % (status, path, " (%s)" % note if note else ""), flush=True)

    # ---- cookies / login ------------------------------------------------------------------------

    def new_session(self):
        """Start an HTTP session with the cookies tis-login.sh saved"""
        self.http = requests.Session()
        self.http.headers["User-Agent"] = USER_AGENT
        self.http.verify = not self.args.insecure
        # Netscape cookie file as written by curl, wget or save_cookies(): seven tab separated fields
        try:
            with open(self.cfg["COOKIES"]) as fh:
                lines = fh.read().splitlines()
        except OSError as e:
            print("Could not read %s: %s" % (self.cfg["COOKIES"], e))
            lines = []
        for line in lines:
            if line.startswith("#HttpOnly_"):
                line = line[len("#HttpOnly_"):]
            f = line.split("\t")
            if line.startswith("#") or len(f) != 7:
                continue
            domain, _, path, secure, expires, name, value = f
            self.http.cookies.set_cookie(requests.cookies.create_cookie(
                name, value, domain=domain, path=path, secure=secure == "TRUE",
                expires=int(expires) if expires not in ("", "0") else None))

    def save_cookies(self):
        """TIS rotates session cookies; write them back so the next tool (or run) doesn't present stale ones"""
        # Netscape format with 0 for session cookies, as curl and wget write it
        lines = ["# Netscape HTTP Cookie File\n"]
        for c in self.http.cookies:
            lines.append("\t".join([c.domain, "TRUE" if c.domain.startswith(".") else "FALSE", c.path,
                                    "TRUE" if c.secure else "FALSE", str(c.expires or 0), c.name, c.value or ""]) + "\n")
        tmp = self.cfg["COOKIES"] + ".tmp"
        old = os.umask(0o077)
        try:
            with open(tmp, "w") as fh:
                fh.writelines(lines)
        finally:
            os.umask(old)
        os.replace(tmp, self.cfg["COOKIES"])
        self.since_cookie_save = 0

    def session_problem(self):
        """Fetch a small subscriber-only PDF.  Returns None if the session works, else what went wrong"""
        try:
            r = self.http.get(self.cfg["WEBSITE"] + TESTPAGE, timeout=(20, 60))
        except requests.RequestException as e:
            return "could not reach TIS (%s)" % type(e).__name__
        if self.login_redirect(r) or LOGIN_BODY_RE.search(r.content[:200000]):
            return "TIS sent its login page: the session expired, or the account is logged in somewhere else"
        if r.status_code != 200:
            return "TIS answered HTTP %d" % r.status_code
        if not r.content.startswith(b"%PDF"):
            return "not logged in (TIS sent a %s page instead of the test PDF)" % r.headers.get("Content-Type", "different")
        return None

    def session_ok(self):
        return self.session_problem() is None

    def relogin(self):
        if self.args.no_relogin:
            return False
        try:
            tty = open("/dev/tty", "rb", buffering=0)
        except OSError:
            print("No terminal to type the 2FA code into.")
            return False
        login = os.path.join(self.cfg["SCRIPT_BASE"], "tis-login.sh")
        # Downloads run for hours and nobody may be watching, and a 2FA code is only good for a few minutes,
        # so wait for the user before asking TIS to send one.  Nothing is sent until they press Enter.
        print("\a\n*** %s  The TIS session has expired, so the download is paused. ***\n"
              "*** Press Enter when you're ready to receive the 2FA code (or type q and Enter to stop; ***\n"
              "*** rerunning the same command later resumes where it stopped). ***"
              % time.strftime("%Y-%m-%d %H:%M"), flush=True)
        with tty:
            while True:
                answer = tty.readline()
                if not answer or answer.strip().lower() in (b"q", b"quit"):
                    return False
                problem = self.portal_problem()
                if problem:
                    print("*** TIS isn't answering right now (%s), so no code was sent.  Press Enter to try again"
                          " (or q to stop). ***" % problem, flush=True)
                    continue
                print("*** Logging in again ***", flush=True)
                subprocess.call([login], stdin=tty)
                self.new_session()
                if self.session_ok():
                    self.counts["relogin"] += 1
                    print("*** Logged in, resuming ***\n", flush=True)
                    return True
                print("\a*** That login didn't work.  Press Enter to try again with a new code (or q to stop). ***",
                      flush=True)

    def portal_problem(self):
        """None if the TIS portal answers at all (no login needed), else what's wrong"""
        try:
            r = requests.get(self.cfg["WEBSITE"] + "/t3Portal/", timeout=(20, 60), allow_redirects=False,
                             headers={"User-Agent": USER_AGENT}, verify=not self.args.insecure)
        except requests.RequestException as e:
            return type(e).__name__
        return "HTTP %d" % r.status_code if r.status_code >= 500 else None

    # ---- URLs and files -------------------------------------------------------------------------

    def url_for(self, item):
        """Turn a /t3Portal/... path or full URL into (url, path), or None if it isn't on the TIS site"""
        u = urllib.parse.urlsplit(urllib.parse.urljoin(self.cfg["WEBSITE"] + "/", item.strip()))
        if u.netloc != self.site.netloc or not u.path.startswith(self.args.scope):
            return None
        path = re.sub("/{2,}", "/", u.path)
        return urllib.parse.urlunsplit((self.site.scheme, self.site.netloc, path, u.query, "")), path

    def local_file(self, path):
        f = os.path.realpath(os.path.join(self.root, urllib.parse.unquote(path).lstrip("/")))
        if path.endswith("/"):
            f = os.path.join(f, "index.html")
        if not f.startswith(self.root + os.sep):
            raise ValueError("path escapes download folder: " + path)
        return f

    def write_file(self, path, data):
        f = self.local_file(path)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        # On disk before the MANIFEST says OK, so even a power cut can't leave an OK file that's empty or cut short
        with open(f + ".part", "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(f + ".part", f)

    def children(self, url, path, data, content_type=""):
        """Files a page or stylesheet refers to, as (url, path) pairs"""
        low = path.lower()
        if low.endswith(".css") or "text/css" in content_type:
            links = css_links(data.decode("utf-8", "replace"))
        elif low.endswith(HTML_EXT) or "html" in content_type:
            p = LinkParser()
            try:
                p.feed(data.decode("utf-8", "replace"))
            except Exception:
                pass
            links = p.links
            url = self.args.base or url
        else:
            return []
        out = []
        for link in links:
            if link.startswith(("data:", "javascript:", "mailto:", "#")):
                continue
            target = self.url_for(urllib.parse.urljoin(url, link))
            if target:
                out.append(target)
        return out

    # ---- downloading ----------------------------------------------------------------------------

    def login_redirect(self, r):
        return any(LOGIN_URL_RE.search(x.headers.get("Location", "")) for x in r.history) or \
            urllib.parse.urlsplit(r.url).netloc != self.site.netloc or LOGIN_URL_RE.search(r.url)

    def get(self, url):
        """GET with retries for network trouble and server errors.  Returns the response or an error string"""
        for delay in (5, 15, 45, None):
            try:
                r = self.http.get(url, timeout=(20, 300), stream=True)
                # TIS serves .svgz with Content-Encoding: gzip.  Keep the gzip bytes (as wget did) rather
                # than letting requests unpack them, since the file on disk has to be a real .svgz.
                if "gzip" in r.headers.get("Content-Encoding", "") and \
                        urllib.parse.urlsplit(r.url).path.lower().endswith(".svgz"):
                    r._content = r.raw.read(decode_content=False)
                r.content
                if r.status_code < 500 and r.status_code != 429:
                    return r
                err = "HTTP %d" % r.status_code
            except requests.RequestException as e:
                err = type(e).__name__
            if delay is None:
                return err
            print("    %s on %s, retrying in %ds" % (err, url, delay), flush=True)
            time.sleep(delay)

    def fetch(self, url, path):
        """Download one URL.  Returns its children on success, raises SessionDead if logged out"""
        r = self.get(url)
        self.since_cookie_save += 1
        if isinstance(r, str):
            self.record(path, "FAILED", note=r)
            return []

        ext = os.path.splitext(path.lower())[1]
        ctype = r.headers.get("Content-Type", "")
        # Some "PDFs" are a script that reloads the same file with ?locale=, and some of those answer with
        # another script that adds ?sisuffix=ff&locale=en&siid=; fetch what they point at
        for _ in range(3):
            stub = STUB_RE.search(r.content[:2000]) if ext in MAGIC and r.status_code == 200 else None
            if not stub or r.content.startswith(MAGIC[ext]):
                break
            target = self.url_for(urllib.parse.urljoin(url, stub.group(1).decode() + ("en" if stub.group(1).endswith(b"=") else "")))
            if not target:
                break
            time.sleep(self.args.wait)
            r = self.get(target[0])
            if isinstance(r, str):
                self.record(path, "FAILED", note=r)
                return []
        suspect = None
        if r.status_code in (401, 403):
            suspect = ("FORBIDDEN", "HTTP %d" % r.status_code)
        elif self.login_redirect(r):
            suspect = ("FAILED", "redirected to " + r.url)
        elif "html" in ctype and LOGIN_BODY_RE.search(r.content[:200000]):
            suspect = ("FAILED", "got the login page")
        elif r.status_code == 200 and ext in MAGIC and not r.content.startswith(MAGIC[ext]):
            suspect = ("FAILED", "not a %s file (%s)" % (ext, ctype))
        if suspect:
            # Usually a dead session, but could be a file that really is off limits (or a page that just
            # mentions the login page).  The test page tells us which.  Nothing gets saved either way.
            if not self.session_ok():
                raise SessionDead(path)
            self.record(path, suspect[0], note=suspect[1])
            return []
        if r.status_code in (404, 410):
            self.record(path, "MISSING", note="HTTP %d" % r.status_code)
            return []
        if r.status_code != 200:
            self.record(path, "FAILED", note="HTTP %d" % r.status_code)
            return []

        self.write_file(path, r.content)
        self.record(path, "OK", len(r.content))
        return self.children(url, path, r.content, r.headers.get("Content-Type", ""))

    def local_children(self, url, path):
        """Children of a page fetched on an earlier run, so a resumed run picks up its missing images"""
        try:
            with open(self.local_file(path), "rb") as fh:
                return self.children(url, path, fh.read())
        except (OSError, ValueError):
            return []

    def run(self, items):
        queue = collections.deque()
        seen = set()
        for item in items:
            t = self.url_for(item)
            if t is None:
                print("Skipping %s: not a %s%s URL" % (item, self.cfg["WEBSITE"], self.args.scope))
            elif t[1] not in seen:
                seen.add(t[1])
                queue.append(t)

        checked = False
        while queue:
            url, path = queue.popleft()
            if self.status.get(path) in DONE or (self.skip_failed and self.status.get(path) == "FAILED"):
                self.counts["skipped"] += 1
                if self.status.get(path) == "FAILED":
                    self.counts["not retried"] += 1
                kids = self.local_children(url, path) if self.args.requisites else []
            else:
                # Check the session before the first download (not before skipping files already done, so a
                # finished list needs no login)
                if not checked:
                    checked = True
                    if not self.session_ok() and not self.relogin():
                        print("Not logged in to TIS.  Run %s/tis-login.sh and try again." % self.cfg["SCRIPT_BASE"])
                        return EXIT_SESSION
                try:
                    kids = self.fetch(url, path)
                except SessionDead:
                    print("TIS rejected the session at %s." % path, flush=True)
                    if not self.relogin():
                        print("Session expired.  Run %s/tis-login.sh, then rerun this command to resume." % self.cfg["SCRIPT_BASE"])
                        return EXIT_SESSION
                    queue.appendleft((url, path))
                    continue
                if self.since_cookie_save >= 100:
                    self.save_cookies()
                time.sleep(self.args.wait)
                if not self.args.requisites:
                    kids = []
            # Fetch a page's images right after the page, so an interrupted run leaves whole pages
            for kid in reversed(kids):
                if kid[1] not in seen:
                    seen.add(kid[1])
                    queue.appendleft(kid)

        self.save_cookies()
        return 1 if self.failed else 0

    def summary(self):
        print("\nDone: %d OK, %d MISSING, %d FORBIDDEN, %d FAILED, %d already done, %d re-logins.  Manifest: %s" % (
            self.counts["OK"], self.counts["MISSING"], self.counts["FORBIDDEN"], self.counts["FAILED"],
            self.counts["skipped"], self.counts["relogin"], self.manifest_path))
        for path in self.failed:
            print("  FAILED " + path)
        if self.counts["not retried"]:
            print("  (%d that FAILED before not retried, as asked by TIS_SKIP_FAILED=1)" % self.counts["not retried"])


def main():
    ap = argparse.ArgumentParser(description="Resumable TIS downloader")
    ap.add_argument("urls", nargs="*", help="URLs or /t3Portal/... paths")
    ap.add_argument("-i", "--input", help='file with one URL or path per line ("-" for stdin)')
    ap.add_argument("--manifest", help="manifest file (default $DOWNLOAD_TO/MANIFEST)")
    ap.add_argument("--wait", type=float, default=0.5, help="seconds between requests (default 0.5)")
    ap.add_argument("--no-requisites", dest="requisites", action="store_false",
                    help="don't fetch the images, stylesheets and scripts pages refer to")
    ap.add_argument("--base", help="resolve links in HTML pages against this URL instead of the page's own "
                    "(wiring diagram pages are shown inside ewd/ewd_index.html, so their links are relative to ewd/)")
    ap.add_argument("--scope", default="/t3Portal/", help="only fetch paths under this prefix (default /t3Portal/)")
    ap.add_argument("--no-relogin", action="store_true", help="exit 75 on session expiry instead of logging in again")
    ap.add_argument("--insecure", action="store_true", help="don't verify the TLS certificate")
    ap.add_argument("-q", "--quiet", action="store_true", help="only print problems and the summary")
    ap.add_argument("--check", action="store_true",
                    help="only check that the saved session works: exit 0 if it does, 75 if not")
    args = ap.parse_args()

    cfg = load_cfg()
    tee_to_log(cfg)                     # before reading -i -, so the logged run gets stdin
    if args.check:
        os.makedirs(cfg["DOWNLOAD_TO"], exist_ok=True)
        f = Fetcher(cfg, args)
        problem = f.session_problem()
        if problem:
            print("TIS session check failed: %s.\nRun %s/tis-login.sh and try again." % (problem, cfg["SCRIPT_BASE"]))
            sys.exit(EXIT_SESSION)
        f.save_cookies()
        if not args.quiet:
            print("TIS session OK")
        sys.exit(0)

    items = list(args.urls)
    if args.input:
        fh = sys.stdin if args.input == "-" else open(args.input)
        items += [line for line in fh.read().splitlines() if line.strip() and not line.startswith("#")]
    if not items:
        ap.error("no URLs given")

    if args.base:
        args.base = urllib.parse.urljoin(cfg["WEBSITE"] + "/", args.base)
    os.makedirs(cfg["FSM_URLBASE"], exist_ok=True)
    f = Fetcher(cfg, args)
    try:
        rc = f.run(items)
    except KeyboardInterrupt:
        print("\nInterrupted.  Rerun the same command to resume.")
        f.save_cookies()
        rc = 130
    f.summary()
    sys.exit(rc)


if __name__ == "__main__":
    main()
