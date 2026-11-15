/* Agent Signal — render data/trends.json ra dashboard. Vanilla JS, không dependency. */
(function () {
  "use strict";

  var fmt = function (n) { return n == null ? "—" : Number(n).toLocaleString("vi-VN"); };

  function scoreClass(s) {
    if (s == null) return "low";
    return s >= 70 ? "hi" : s >= 50 ? "mid" : "low";
  }

  function deltaChip(r) {
    if (r.delta_7d == null) return '<span class="chip new">MỚI</span>';
    var v = r.delta_7d;
    var sign = v > 0 ? "+" : "";
    return '<span class="chip ' + (v > 0 ? "delta" : "delta neg") + '">' +
      sign + fmt(v) + " / 7 ngày</span>";
  }

  function card(r) {
    var tags = (r.topics || []).slice(0, 3)
      .map(function (t) { return '<span class="tag">' + t.replace(/</g, "&lt;") + "</span>"; }).join("");
    var fit = r.fit_curated
      ? '<p class="fit"><span class="fit-label">Vì sao phù hợp</span>' + esc(r.fit_note) + "</p>"
      : "";
    var lic = r.license && r.license !== "NOASSERTION" ? '<span class="chip">' + r.license + "</span>" : "";
    return '' +
      '<article class="card">' +
        '<div class="card-top">' +
          '<h3 class="card-name"><a href="' + r.url + '" rel="noopener" target="_blank">' + esc(r.full_name) + "</a></h3>" +
          '<span class="badge ' + scoreClass(r.score) + '" title="Điểm tự động · xem phương pháp">' +
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
        ? (r.delta_7d >= 0 ? "+" : "") + fmt(r.delta_7d) + "★ / 7 ngày"
        : "mới vào radar";
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
        "<li>Chưa tải được dữ liệu (" + esc(err.message) + "). Có thể job đêm trước chưa chạy xong.</li>";
    });
})();

/* Inbox — gửi lệnh cho Hermes qua GitHub Issue hoặc clipboard. */
(function () {
  "use strict";
  var form = document.getElementById("cmd-form");
  if (!form) return;
  var repoEl = document.getElementById("cmd-repo");
  var actionEl = document.getElementById("cmd-action");
  var noteEl = document.getElementById("cmd-note");
  var out = document.getElementById("cmd-out");

  try {
    repoEl.value = localStorage.getItem("as_cmd_repo") || "";
    actionEl.value = localStorage.getItem("as_cmd_action") || actionEl.value;
    noteEl.value = localStorage.getItem("as_cmd_note") || "";
  } catch (e) { /* storage unavailable */ }

  function text() {
    return "[HERMES] Repo/tool: " + repoEl.value.trim() +
      " · Hành động: " + actionEl.value +
      " · Chi tiết: " + (noteEl.value.trim() || "(không có)");
  }
  function save() {
    try {
      localStorage.setItem("as_cmd_repo", repoEl.value);
      localStorage.setItem("as_cmd_action", actionEl.value);
      localStorage.setItem("as_cmd_note", noteEl.value);
    } catch (e) { /* ignore */ }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    save();
    var url = "https://github.com/vaicauchuyentreninternet-crypto/agent-signal/issues/new" +
      "?labels=hermes-command" +
      "&title=" + encodeURIComponent("[hermes-command] " + repoEl.value.trim()) +
      "&body=" + encodeURIComponent(text());
    window.open(url, "_blank", "noopener");
    out.textContent = "Đã mở form GitHub Issue (nhãn hermes-command). Gửi issue xong Hermes sẽ tự quét và thực thi.";
  });

  document.getElementById("btn-copy").addEventListener("click", function () {
    save();
    var t = text();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () {
        out.textContent = "Đã copy lệnh. Dán vào chat Discord cho Hermes.";
      }, function () { out.textContent = t; });
    } else {
      out.textContent = t;
    }
  });
})();
