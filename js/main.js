/* Agent Signal — renders data/trends.json into the dashboard. Vanilla JS, no deps. */
(function () {
  "use strict";

  var fmt = function (n) { return n == null ? "—" : Number(n).toLocaleString("en-US"); };

  function scoreClass(s) {
    if (s == null) return "low";
    return s >= 70 ? "hi" : s >= 50 ? "mid" : "low";
  }

  function deltaChip(r) {
    if (r.delta_7d == null) return '<span class="chip new">NEW</span>';
    var v = r.delta_7d;
    var sign = v > 0 ? "+" : "";
    var cls = v > 0 ? "delta" : v < 0 ? "delta neg" : "delta";
    return '<span class="chip ' + cls + '">' + sign + fmt(v) + " / 7d</span>";
  }

  function card(r) {
    var tags = (r.topics || []).slice(0, 3)
      .map(function (t) { return '<span class="tag">' + t.replace(/</g, "&lt;") + "</span>"; }).join("");
    var fit = r.fit_curated
      ? '<p class="fit"><span class="fit-label">Why here</span>' + esc(r.fit_note) + "</p>"
      : "";
    var lic = r.license && r.license !== "NOASSERTION" ? '<span class="chip">' + r.license + "</span>" : "";
    return '' +
      '<article class="card">' +
        '<div class="card-top">' +
          '<h3 class="card-name"><a href="' + r.url + '" rel="noopener" target="_blank">' + esc(r.full_name) + "</a></h3>" +
          '<span class="badge ' + scoreClass(r.score) + '" title="Auto-score · see methodology">' +
            (r.score == null ? "—" : r.score) + "</span>" +
        "</div>" +
        '<div class="meta">' +
          '<span class="chip">★ ' + fmt(r.stars) + "</span>" + deltaChip(r) +
          (r.lang ? '<span class="chip">' + esc(r.lang) + "</span>" : "") + lic +
        "</div>" +
        '<p class="blurb-sm">' + esc(r.blurb) + "</p>" +
        fit +
        (tags ? '<div class="tags">' + tags + "</div>" : "") +
      "</article>";
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function renderBrief(data) {
    var all = [];
    data.categories.forEach(function (c) {
      c.repos.forEach(function (r) { all.push({ cat: c.title, r: r }); });
    });
    all.sort(function (a, b) {
      var da = a.r.delta_7d == null ? -Infinity : a.r.delta_7d;
      var db = b.r.delta_7d == null ? -Infinity : b.r.delta_7d;
      if (da !== db) return db - da;
      return (b.r.score || 0) - (a.r.score || 0);
    });
    var top = all.slice(0, 5);
    var html = top.map(function (x) {
      var r = x.r;
      var move = r.delta_7d != null
        ? (r.delta_7d >= 0 ? "+" : "") + fmt(r.delta_7d) + "★ / 7d"
        : "new to radar";
      return "<li><strong>" + esc(r.full_name) + "</strong> (" + esc(x.cat) + ") — " +
        move + " · ★ " + fmt(r.stars) + " · " + esc(r.blurb) + "</li>";
    }).join("");
    document.getElementById("brief-list").innerHTML = html;
  }

  function renderSections(data) {
    var host = document.getElementById("sections");
    host.innerHTML = data.categories.map(function (c) {
      var cards = c.repos.map(card).join("");
      return '' +
        '<section class="block" aria-labelledby="sec-' + c.key + '">' +
          '<h2 id="sec-' + c.key + '">' + esc(c.title) + "</h2>" +
          '<p class="blurb">' + esc(c.blurb) + "</p>" +
          '<div class="grid">' + cards + "</div>" +
        "</section>";
    }).join("");
  }

  fetch("data/trends.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function (data) {
      var t = document.getElementById("updated");
      var d = new Date(data.generated_at);
      t.textContent = isNaN(d.getTime()) ? data.generated_at : d.toUTCString().replace("GMT", "UTC");
      t.setAttribute("datetime", data.generated_at || "");
      renderBrief(data);
      renderSections(data);
    })
    .catch(function (err) {
      document.getElementById("brief-list").innerHTML =
        "<li>Could not load trend data (" + esc(err.message) + "). The nightly job may still be running.</li>";
    });
})();
