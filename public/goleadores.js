// Broma de la tabla de goleadores: Diego y Mario son pulsables. La primera pulsación les suma un
// gol a los dos y se lo quita a Pablo (nunca por debajo de 0), y la tabla se reordena. Solo
// funciona una vez: después dejan de ser pulsables y no se suma ni se resta nada más.
// Todo pasa en el navegador de quien la visita: no se guarda nada y se reinicia al recargar.
// Los datos los escribe tools/build.py en <script type="application/json" id="goles-data">.
(function () {
  "use strict";
  var el = document.getElementById("goles-data");
  var sec = document.getElementById("goleadores");
  if (!el || !sec) return;
  var data;
  try { data = JSON.parse(el.textContent); } catch (e) { return; }
  var players = data.players, broma = data.broma;
  var byName = {};
  players.forEach(function (p) { byName[p.name] = p; });
  var suman = broma.suman.filter(function (n) { return byName[n]; });
  var pablo = byName[broma.resta];
  if (suman.length !== broma.suman.length || !pablo) return;

  var usada = false; // la broma solo se puede hacer una vez por visita
  var tables = {};
  [].forEach.call(sec.querySelectorAll("table[data-goles]"), function (t) { tables[t.getAttribute("data-goles")] = t; });
  if (!tables.top || !tables.celta) return;

  // Mismo criterio que la web de la liga: más goles, luego menos partidos y, si no, el orden original.
  function ordenar() {
    players.sort(function (a, b) { return b.goals - a.goals || a.pj - b.pj || a.rank - b.rank; });
    players.forEach(function (p, i) { p.pos = i + 1; });
  }

  function td(cls, text) {
    var c = document.createElement("td");
    if (cls) c.className = cls;
    c.textContent = text;
    return c;
  }

  function fila(p, cls) {
    var tr = document.createElement("tr");
    if (cls) tr.className = cls;
    tr.appendChild(td("n", p.pos));
    var th = document.createElement("th");
    th.scope = "row";
    if (!usada && suman.indexOf(p.name) >= 0) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "broma";
      b.setAttribute("data-jugador", p.name);
      b.title = "Dale un gol a Diego y a Mario";
      b.textContent = p.name;
      th.appendChild(b);
    } else {
      th.appendChild(document.createTextNode(p.name));
    }
    var eq = document.createElement("span");
    eq.className = "eq";
    eq.textContent = p.team;
    th.appendChild(eq);
    tr.appendChild(th);
    tr.appendChild(td("team", p.team));
    tr.appendChild(td("hm", p.pj));
    tr.appendChild(td("hm", p.pj ? (p.goals / p.pj).toFixed(2).replace(".", ",") : "–"));
    tr.appendChild(td("pt", p.goals));
    return tr;
  }

  function cuerpo(table, rows) {
    var tb = document.createElement("tbody");
    rows.forEach(function (r) { tb.appendChild(r); });
    table.replaceChild(tb, table.tBodies[0]);
  }

  function total(key, n) {
    var s = sec.querySelector('[data-total="' + key + '"]');
    if (s) s.textContent = n;
  }

  function pintar() {
    ordenar();
    cuerpo(tables.top, players.slice(0, data.top).map(function (p) { return fila(p, p.me ? "me" : ""); }));
    var celta = players.filter(function (p) { return p.me; });
    cuerpo(tables.celta, celta.map(function (p) { return fila(p, ""); }));
    var sum = function (list) { return list.reduce(function (a, p) { return a + p.goals; }, 0); };
    total("jugadores", players.filter(function (p) { return p.goals > 0; }).length);
    total("liga", sum(players));
    total("celta", sum(celta));
  }

  // Aviso visible y anunciado a los lectores de pantalla.
  var toast = document.createElement("div");
  toast.className = "toast";
  toast.setAttribute("role", "status");
  document.body.appendChild(toast);
  var timer;
  function avisar(msg) {
    toast.textContent = "";
    toast.classList.remove("on");
    void toast.offsetWidth; // reinicia la animación en pulsaciones seguidas
    toast.textContent = msg;
    toast.classList.add("on");
    clearTimeout(timer);
    timer = setTimeout(function () { toast.classList.remove("on"); }, 2200);
  }

  sec.addEventListener("click", function (e) {
    var b = e.target.closest("button.broma");
    if (!b) return;
    if (usada) return;
    usada = true;
    var tabla = b.closest("table").getAttribute("data-goles"), quien = b.getAttribute("data-jugador");
    suman.forEach(function (n) { byName[n].goals += 1; });
    if (pablo.goals > 0) pablo.goals -= 1;
    pintar(); // ya sin botones: los nombres vuelven a ser texto normal
    // El botón ha desaparecido: deja el foco en la misma celda para no perder el sitio con el teclado.
    var celda = [].filter.call(tables[tabla].querySelectorAll("th[scope=row]"), function (x) {
      return x.firstChild && x.firstChild.nodeValue === quien;
    })[0];
    if (celda) { celda.tabIndex = -1; celda.focus({ preventScroll: true }); }
    avisar("¡Pablo ladrón!");
  });

  pintar();
})();
