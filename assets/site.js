// Renders the game list (index.html) and a game's page (game.html?g=<slug>) from games.json.
// Everything about a game - text, versions, which build is newest - lives in games.json, which
// tools/add_build.py keeps up to date; these pages never need editing to add a game or version.

(function () {
  "use strict";

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === "text") node.textContent = attrs[k];
        else if (k === "class") node.className = attrs[k];
        else node.setAttribute(k, attrs[k]);
      }
    }
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  // The newest proper version lives at a fixed games/<slug>/play/ (games.json "play"): the web
  // player keeps its save per build folder URL, so a fixed folder carries progress to the next one.
  function playUrl(game, version) {
    return "games/" + game.slug + "/" + (version.id === game.play ? "play" : version.id) + "/";
  }

  function tags(game, version) {
    var list = [el("span", { class: "tag solid", text: game.status })];
    (game.platforms || []).forEach(function (p) { list.push(el("span", { class: "tag", text: p })); });
    if (version && version.temporary) list.push(el("span", { class: "tag temp", text: "임시 버전" }));
    return el("div", { class: "meta" }, list);
  }

  function renderIndex(data, root) {
    var games = data.games || [];
    if (!games.length) {
      root.appendChild(el("p", { class: "note", text: "아직 올라온 게임이 없습니다." }));
      return;
    }
    games.forEach(function (game) {
      var latest = (game.versions || [])[0];
      var actions = [];
      if (latest) actions.push(el("a", { class: "btn primary", href: playUrl(game, latest), text: "플레이" }, [el("span", { text: "→" })]));
      actions.push(el("a", { class: "btn secondary", href: "game.html?g=" + encodeURIComponent(game.slug), text: "자세히" }));
      var card = el("article", { class: "card" }, [
        game.cover ? el("img", { class: "cover", src: game.cover, alt: game.title + " 표지", loading: "lazy" }) : null,
        el("div", { class: "body" }, [
          el("h2", { text: game.title }),
          el("p", { text: game.tagline || "" }),
          tags(game, latest),
          latest ? el("p", { class: "note" }, [
            document.createTextNode("최신: " + latest.label + " · "),
            el("span", { class: "nowrap", text: latest.date }),
          ]) : null,
          el("div", { class: "actions" }, actions),
        ]),
      ]);
      root.appendChild(card);
    });
  }

  function renderGame(data, root) {
    var slug = new URLSearchParams(location.search).get("g");
    var game = (data.games || []).filter(function (g) { return g.slug === slug; })[0];
    if (!game) {
      root.appendChild(el("p", { text: "게임을 찾을 수 없습니다." }));
      return;
    }
    document.title = game.title + " · QuestionMark";
    var versions = game.versions || [];
    var latest = versions[0];

    root.appendChild(el("div", { class: "game-head" }, [
      game.cover ? el("img", { class: "cover", src: game.cover, alt: game.title + " 표지" }) : el("div"),
      el("div", null, [
        el("h1", { text: game.title }),
        el("p", { class: "lead", text: game.tagline || "" }),
        tags(game, latest),
        el("p", { class: "desc", text: game.description || "" }),
        latest ? el("a", { class: "btn primary", href: playUrl(game, latest), text: "최신 버전 플레이 · " + latest.label }, [el("span", { text: "→" })]) : null,
      ]),
    ]));

    if (game.controls && game.controls.length) {
      root.appendChild(el("h3", { class: "block", text: "조작" }));
      var rows = game.controls.map(function (c) { return el("tr", null, [el("th", { text: c[0] }), el("td", { text: c[1] })]); });
      root.appendChild(el("table", { class: "controls" }, [el("tbody", null, rows)]));
    }

    root.appendChild(el("h3", { class: "block", text: "버전" }));
    var list = el("ul", { class: "versions" });
    versions.forEach(function (v, i) {
      var badges = [];
      if (i === 0) badges.push(el("span", { class: "tag solid", text: "최신" }));
      if (v.temporary) badges.push(el("span", { class: "tag temp", text: "임시" }));
      list.appendChild(el("li", null, [
        el("div", { class: "v-main" }, [
          el("div", { class: "v-title", text: v.label + " · " + v.date }),
          v.notes ? el("p", { class: "v-notes", text: v.notes }) : null,
        ]),
        el("div", { class: "meta" }, badges),
        el("a", { class: "btn secondary", href: playUrl(game, v), text: "플레이" }),
      ]));
    });
    root.appendChild(list);
    root.appendChild(el("p", { class: "note", text: "임시 버전은 개발 중인 빌드라 버그가 있거나 저장 데이터가 초기화될 수 있습니다." }));
    if (game.play) root.appendChild(el("p", { class: "note", text: "진행 상황은 이 브라우저에 저장됩니다. 최신 정식 버전은 늘 같은 주소라 다음 버전에서도 이어지고, 목록의 이전 버전은 저장이 따로입니다." }));

    if (game.screenshots && game.screenshots.length) {
      root.appendChild(el("h3", { class: "block", text: "스크린샷" }));
      root.appendChild(el("div", { class: "shots" }, game.screenshots.map(function (s) {
        return el("img", { src: s, alt: game.title + " 스크린샷", loading: "lazy" });
      })));
    }
  }

  var root = document.getElementById("app");
  fetch("games.json", { cache: "no-cache" })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (root.dataset.page === "game") renderGame(data, root);
      else renderIndex(data, root);
    })
    .catch(function () {
      root.appendChild(el("p", { class: "note", text: "목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요." }));
    });
})();
