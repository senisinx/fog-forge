/* fogforge.app: the shared script. The texts it shows come from `var S` in each page (translated by tools/build.py). */
(function () {
  var doc = document, S = window.S || {}, calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function all(sel) { return Array.prototype.slice.call(doc.querySelectorAll(sel)); }

  /* inside the app: one picture, buttons to switch it */
  var pic = doc.getElementById("appImg");
  all("#tabs button").forEach(function (b, _, list) {
    b.addEventListener("click", function () {
      list.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
      pic.src = b.getAttribute("data-src");
      pic.alt = b.getAttribute("data-alt");
    });
  });

  /* in-page navigation: mark the section that is on screen */
  var marks = all(".subnav a");
  if (marks.length && "IntersectionObserver" in window) {
    var byId = {};
    marks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var watch = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) marks.forEach(function (a) { a.classList.toggle("on", a === byId[e.target.id]); });
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    Object.keys(byId).forEach(function (id) { var sec = doc.getElementById(id); if (sec) watch.observe(sec); });
  }

  /* chat replay of Fog Translate: the prepared lines are in the page, so they are translated with it */
  var chat = doc.getElementById("chat"), out = doc.getElementById("out");
  if (chat && out) {
    var LINES = all("#lines li").map(function (li) {
      return [li.getAttribute("data-lang"), li.getAttribute("data-name"), li.getAttribute("data-orig"), li.textContent];
    }), at = 0;
    function el(tag, txt) { var n = doc.createElement(tag); if (txt != null) n.textContent = txt; return n; }
    function say() {
      var l = LINES[at++ % LINES.length];
      var p = el("p"); p.appendChild(el("b", l[1] + ": ")); p.appendChild(doc.createTextNode(l[2]));
      chat.appendChild(p);
      while (chat.children.length > 4) chat.removeChild(chat.firstChild);
      setTimeout(function () {
        var li = el("li"), s = el("small");
        s.appendChild(el("b", l[0])); s.appendChild(doc.createTextNode(l[1]));
        li.appendChild(s); li.appendChild(el("strong", l[3])); li.appendChild(el("em", l[2]));
        out.appendChild(li);
        while (out.children.length > 4) out.removeChild(out.firstChild);
      }, calm ? 0 : 900);
    }
    if (LINES.length) {
      say(); say(); say();
      if (!calm && "IntersectionObserver" in window) {
        var run = null, seen = false, held = false, hold = doc.getElementById("hold");
        function go() {
          if (seen && !held && !run) run = setInterval(say, 3000);
          else if ((!seen || held) && run) { clearInterval(run); run = null; }
        }
        new IntersectionObserver(function (es) { seen = es[0].isIntersecting; go(); }).observe(chat.closest(".replay"));
        hold.hidden = false;
        hold.addEventListener("click", function () { held = !held; hold.textContent = held ? S.play : S.pause; go(); });
      }
    }
  }

  /* newest release of each tool: the download buttons go straight to the setup, the line below names version, date and size */
  var KEEP_MS = 10 * 60 * 1000;
  function latest(repo) {
    var key = "ff-rel-" + repo, now = Date.now();
    try { var hit = JSON.parse(sessionStorage.getItem(key)); if (hit && now - hit.t < KEEP_MS && hit.rel) return Promise.resolve(hit.rel); } catch (e) {}
    return fetch("https://api.github.com/repos/senisinx/" + repo + "/releases/latest", { headers: { Accept: "application/vnd.github+json" } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (rel) {
        var keep = { tag_name: rel.tag_name, published_at: rel.published_at, assets: (rel.assets || []).map(function (a) {
          return { name: a.name, size: a.size, browser_download_url: a.browser_download_url }; }) };
        try { sessionStorage.setItem(key, JSON.stringify({ t: now, rel: keep })); } catch (e) {}
        return keep;
      });
  }
  function fmtDate(s) { try { return new Date(s).toLocaleDateString(S.locale, { day: "numeric", month: "short", year: "numeric" }); } catch (e) { return ""; } }
  if (S.version && window.fetch && window.Promise) ["fog-scout", "fog-translate"].forEach(function (repo) {
    var as = all('a[data-dl="' + repo + '"]'), metas = all('[data-meta="' + repo + '"]');
    if (!as.length && !metas.length) return;
    latest(repo)
      .then(function (rel) {
        var asset = (rel.assets || []).filter(function (x) { return /setup.*\.exe$/i.test(x.name); })[0]; if (!asset) return;
        as.forEach(function (a) { a.href = asset.browser_download_url; });
        var line = S.version.replace("%s", String(rel.tag_name).replace(/^v/i, "")) + " · " + fmtDate(rel.published_at) + " · " + (asset.size / 1048576).toFixed(0) + " MB · " + S.installer;
        metas.forEach(function (m) { m.textContent = line; });
      })
      .catch(function () { /* keep the release-page link */ });
  });
})();
