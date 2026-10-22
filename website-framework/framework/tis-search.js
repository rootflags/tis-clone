/*
 * tis-search.js - The search box below a manual's menu (toc.html, made by toc2html.py)
 *
 * The menu loads this the first time the search box is clicked.  It searches the index build-search.py made
 * in the manual's search/ folder, loading only the pieces it needs as you type: search/meta.js, the word
 * list for the first two letters of each word typed (search/w/P0.js) and the titles of the pages it shows
 * (search/p/N.js).  Every word typed must start a word on the page (P04 finds P0420).  For each result you
 * scroll to it fetches the page itself to show the text around the match.  Clicking a result also closes the
 * menu's open folders, opens it to that page and shows both in bold.  All of it is plain files, so it works
 * on any web server.
 */
(function () {
	"use strict";
	var box = document.getElementById("tis-search");
	var input = document.getElementById("tis-search-q");
	var results = document.getElementById("tis-search-results");
	var base = box.getAttribute("data-index");
	var SHOW = 50;                      // results listed at a time
	var meta = null, haveShard = {}, shards = {}, chunks = {}, scripts = {};
	var seq = 0, timer = null;
	var snippetQueue = [], snippetsRunning = 0, observer = null;

	// The index files call these when they load
	window.TISSearch = {
		meta: function (m) {
			meta = m;
			for (var i = 0; i < m.shards.length; i += 2) {
				haveShard[m.shards.substr(i, 2)] = true;
			}
		},
		words: function (key, w) { shards[key] = w; },
		pages: function (n, p) { chunks[n] = p; }
	};

	var style = document.createElement("style");
	style.textContent =
		"#tis-search-results { font-size: 0.85rem; padding: 0 0.5rem 1rem 0.5rem; }" +
		"#tis-search-results .tis-status { color: #666; margin: 0.25rem 0 0.5rem 0; }" +
		"#tis-search-results .tis-hit { margin-bottom: 0.6rem; }" +
		"#tis-search-results .tis-section { color: #777; font-size: 0.75rem; }" +
		"#tis-search-results .tis-snippet { color: #333; font-size: 0.8rem; }" +
		"#tis-search-results mark { background: #fff3a0; padding: 0; }" +
		"#tis-search-results button { font-size: 0.8rem; }" +
		"a.tis-current { font-weight: bold; }";
	document.head.appendChild(style);

	// Clicking a result (it opens in the manual's frame as usual) opens the menu to the same page, and both are
	// shown in bold.  Opening menu folders pushes the results down, so scroll back to the result clicked.
	results.addEventListener("click", function (e) {
		var a = e.target;
		while (a && a !== results && !(a.classList && a.classList.contains("tis-title"))) {
			a = a.parentNode;
		}
		if (!a || a === results) {
			return;
		}
		var before = a.getBoundingClientRect().top, href = a.getAttribute("href"), entry = null;
		Array.prototype.forEach.call(document.querySelectorAll("a.tis-current"), function (c) {
			c.classList.remove("tis-current");
		});
		a.classList.add("tis-current");
		Array.prototype.some.call(document.querySelectorAll("#tis-menu a[target=manual_frame]"), function (m) {
			return m.getAttribute("href") === href && (entry = m);
		});
		if (!entry) {
			return;
		}
		entry.classList.add("tis-current");
		// Close every open folder, then open the ones above the page (setting their toggles the way Bootstrap would)
		Array.prototype.forEach.call(document.querySelectorAll("#tis-menu .collapse.show"), function (f) {
			folder(f, false);
		});
		for (var n = entry.parentNode; n && n.id !== "tis-menu"; n = n.parentNode) {
			if (n.classList && n.classList.contains("collapse")) {
				folder(n, true);
			}
		}
		window.scrollBy(0, a.getBoundingClientRect().top - before);
	});

	// Open or close one of Bootstrap's collapsible menu folders, and its toggle link
	function folder(f, open) {
		f.classList.toggle("show", open);
		var toggle = document.querySelector("a[href='#" + f.id + "']");
		if (toggle) {
			toggle.classList.toggle("collapsed", !open);
			toggle.setAttribute("aria-expanded", open ? "true" : "false");
		}
	}

	// Load search/PATH with a <script> tag (once).  Resolves false if it couldn't, so a later search tries again.
	function load(path) {
		if (!scripts[path]) {
			scripts[path] = new Promise(function (resolve) {
				var s = document.createElement("script");
				s.src = base + path;
				s.onload = function () { resolve(true); };
				s.onerror = function () { delete scripts[path]; resolve(false); };
				document.head.appendChild(s);
			});
		}
		return scripts[path];
	}

	function tokens(q) {
		return (q.toUpperCase().match(/[A-Z0-9]+/g) || []).filter(function (t) { return t.length > 1; });
	}

	// "f7,8,1" (gaps between page numbers, in hex) -> [247, 255, 256]
	function pageList(gaps) {
		var out = [], n = 0;
		if (gaps) {
			gaps.split(",").forEach(function (g) { n += parseInt(g, 16); out.push(n); });
		}
		return out;
	}

	// {page: score} for the pages with a word starting with TOKEN; a whole word or a title scores higher
	function matches(token) {
		var found = {}, words = shards[token.substr(0, 2)] || {};
		Object.keys(words).forEach(function (w) {
			if (w.lastIndexOf(token, 0) !== 0) {
				return;
			}
			var exact = w === token ? 2 : 1;
			pageList(words[w][0]).forEach(function (p) { found[p] = Math.max(found[p] || 0, exact); });
			pageList(words[w][1]).forEach(function (p) { found[p] = Math.max(found[p] || 0, exact + 4); });
		});
		return found;
	}

	function escapeHtml(s) {
		return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; });
	}

	function wordRegex(toks, flags) {
		return new RegExp("\\b(" + toks.join("|") + ")[A-Za-z0-9]*", flags);
	}

	// TEXT as HTML with the words starting with a token marked (escaped piece by piece, so a token can't match
	// inside an entity like &amp;)
	function highlight(text, toks) {
		var re = wordRegex(toks, "gi"), out = "", last = 0, m;
		while ((m = re.exec(text)) !== null) {
			out += escapeHtml(text.slice(last, m.index)) + "<mark>" + escapeHtml(m[0]) + "</mark>";
			last = re.lastIndex;
		}
		return out + escapeHtml(text.slice(last));
	}

	// The menu stays; the results go below the search box
	function showResults(on) {
		results.style.display = on ? "" : "none";
	}

	function status(html) {
		results.innerHTML = "<div class='tis-status'>" + html + "</div>";
	}

	function search() {
		var q = input.value, toks = tokens(q), my = ++seq;
		if (!q.trim()) {
			showResults(false);
			return;
		}
		showResults(true);
		if (!toks.length) {
			status("Type at least 2 letters or digits");
			return;
		}
		status("Searching&hellip;");
		load("meta.js").then(function (ok) {
			if (!ok || !meta) {
				throw new Error("this manual's search index didn't load");
			}
			var needed = [];
			toks.forEach(function (t) {
				var key = t.substr(0, 2);
				if (haveShard[key] && needed.indexOf(key) < 0) {
					needed.push(key);
				}
			});
			return Promise.all(needed.map(function (k) { return load("w/" + k + ".js"); }));
		}).then(function () {
			if (my !== seq) {
				return;
			}
			// Pages with every word, best first, then in the manual's order
			var score = null;
			toks.forEach(function (t) {
				var m = matches(t), next = {};
				Object.keys(m).forEach(function (p) {
					if (score === null || p in score) {
						next[p] = (score === null ? 0 : score[p]) + m[p];
					}
				});
				score = next;
			});
			var hits = Object.keys(score).map(Number).sort(function (a, b) { return score[b] - score[a] || a - b; });
			results.innerHTML = "";
			if (!hits.length) {
				status("No pages match <b>" + escapeHtml(q) + "</b>");
				return;
			}
			results.innerHTML = "<div class='tis-status'>" + hits.length + " page" + (hits.length === 1 ? "" : "s") +
				(meta.text ? "" : " (titles only)") + "</div>";
			snippetQueue = [];
			if (observer) {
				observer.disconnect();
			}
			list(hits, 0, toks, my);
		}).catch(function (e) {
			if (my === seq) {
				status("Search isn't working: " + escapeHtml(e.message) + ".  Try again.");
			}
		});
	}

	// Show hits FROM to FROM + SHOW, with a button for the next lot
	function list(hits, from, toks, my) {
		var some = hits.slice(from, from + SHOW), needed = [];
		some.forEach(function (p) {
			var c = Math.floor(p / meta.chunk);
			if (needed.indexOf(c) < 0) {
				needed.push(c);
			}
		});
		Promise.all(needed.map(function (c) { return load("p/" + c + ".js"); })).then(function () {
			if (my !== seq) {
				return;
			}
			var more = results.querySelector("button");
			if (more) {
				more.parentNode.removeChild(more);
			}
			some.forEach(function (p) {
				var chunk = chunks[Math.floor(p / meta.chunk)];
				if (!chunk) {
					return;
				}
				var row = chunk.pages[p % meta.chunk], div = document.createElement("div");
				div.className = "tis-hit";
				div.innerHTML = "<a class='tis-title' target='manual_frame' href='" + escapeHtml(row[0]) + "'>" +
					highlight(row[1], toks) + "</a><div class='tis-section'>" + escapeHtml(chunk.sections[row[2]]) +
					"</div><div class='tis-snippet'></div>";
				results.appendChild(div);
				if (meta.text) {
					watch(div, row[0], toks, my);
				}
			});
			if (from + SHOW < hits.length) {
				var button = document.createElement("button");
				button.className = "btn btn-light btn-sm";
				button.textContent = "Show " + Math.min(SHOW, hits.length - from - SHOW) + " more";
				button.onclick = function () { list(hits, from + SHOW, toks, my); };
				results.appendChild(button);
			}
		});
	}

	// The text around the match, fetched once the result scrolls into view, 3 pages at a time
	function watch(div, href, toks, my) {
		var job = function () { return snippet(div, href, toks, my); };
		if (!window.IntersectionObserver) {
			queue(job);
			return;
		}
		if (!observer) {
			observer = new IntersectionObserver(function (entries) {
				entries.forEach(function (e) {
					if (e.isIntersecting && e.target.tisJob) {
						queue(e.target.tisJob);
						e.target.tisJob = null;
						observer.unobserve(e.target);
					}
				});
			});
		}
		div.tisJob = job;
		observer.observe(div);
	}

	function queue(job) {
		snippetQueue.push(job);
		run();
	}

	function run() {
		while (snippetsRunning < 3 && snippetQueue.length) {
			snippetsRunning++;
			snippetQueue.shift()().then(function () {
				snippetsRunning--;
				run();
			});
		}
	}

	function snippet(div, href, toks, my) {
		if (my !== seq) {
			return Promise.resolve();
		}
		return fetch(href.split("#")[0]).then(function (r) { return r.ok ? r.text() : ""; }).then(function (page) {
			var doc = new DOMParser().parseFromString(page, "text/html");
			// Not the page's header (Last Modified, Doc ID, Model, Title)
			Array.prototype.forEach.call(doc.querySelectorAll("script, style, table.side"), function (n) {
				n.parentNode.removeChild(n);
			});
			var text = (doc.body ? doc.body.textContent : "").replace(/\s+/g, " ").trim();
			var m = wordRegex(toks, "i").exec(text);
			if (!m) {
				return;
			}
			var start = Math.max(0, m.index - 60), end = Math.min(text.length, m.index + 120);
			while (start > 0 && text.charAt(start - 1) !== " ") {
				start++;
			}
			while (end < text.length && text.charAt(end) !== " ") {
				end++;
			}
			div.querySelector(".tis-snippet").innerHTML = (start > 0 ? "&hellip;" : "") +
				highlight(text.slice(start, end), toks) + (end < text.length ? "&hellip;" : "");
		}).catch(function () { /* no snippet, the result still works */ });
	}

	input.addEventListener("input", function () {
		clearTimeout(timer);
		timer = setTimeout(search, 250);
	});
	input.addEventListener("keydown", function (e) {
		if (e.key === "Escape") {
			input.value = "";
			search();
		} else if (e.key === "Enter") {
			clearTimeout(timer);
			search();
		}
	});
	// Typed before this finished loading
	if (input.value) {
		search();
	}
})();
