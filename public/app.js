(function () {
  "use strict";
  var root = document.documentElement;

  // Fecha de portada
  var f = document.getElementById("fecha");
  if (f) {
    f.textContent = new Date().toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  }

  // Tema claro/oscuro
  var tt = document.getElementById("tema");
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  function isDark() {
    var t = root.dataset.theme;
    return t ? t === "dark" : mq.matches;
  }
  function paint() {
    if (!tt) return;
    tt.textContent = isDark() ? "☀ Claro" : "☾ Oscuro";
    tt.setAttribute("aria-label", isDark() ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
  }
  if (tt) {
    tt.hidden = false;
    tt.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) {}
      paint();
    });
    mq.addEventListener && mq.addEventListener("change", paint);
    paint();
  }


  // Calendario: solo el Celta / toda la liga
  var vista = document.getElementById("vista"), cal = document.getElementById("cal");
  if (vista && cal) {
    vista.hidden = false;
    var setView = function (v) {
      cal.setAttribute("data-view", v);
      [].forEach.call(vista.querySelectorAll("button"), function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-v") === v));
      });
    };
    vista.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (b) setView(b.getAttribute("data-v"));
    });
    setView("celta");
  }

  // Sección actual en el menú
  var links = [].slice.call(document.querySelectorAll(".nav a[href^='#']"));
  if ("IntersectionObserver" in window && links.length) {
    var map = {};
    links.forEach(function (a) { var s = document.getElementById(a.hash.slice(1)); if (s) map[s.id] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (a) { a.removeAttribute("aria-current"); });
          map[e.target.id].setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { io.observe(document.getElementById(id)); });
  }

  // Visor de fotos
  var dlg = document.getElementById("visor");
  if (!dlg || !dlg.showModal) return;
  var img = dlg.querySelector("img"), cap = dlg.querySelector("p");
  var set = [], i = 0;

  function show(n) {
    i = (n + set.length) % set.length;
    var src = set[i];
    img.src = src.currentSrc || src.src;
    img.alt = src.alt;
    var fc = src.closest("figure").querySelector("figcaption");
    cap.textContent = (fc ? fc.textContent : src.alt) + "  (" + (i + 1) + "/" + set.length + ")";
  }
  function open(el) {
    set = [].slice.call(el.closest("article").querySelectorAll("figure img.zoomable"));
    show(set.indexOf(el));
    dlg.showModal();
  }

  [].forEach.call(document.querySelectorAll("figure img.zoomable"), function (el) {
    el.tabIndex = 0;
    el.setAttribute("role", "button");
    el.addEventListener("click", function () { open(el); });
    el.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(el); }
    });
  });
  dlg.querySelector(".x").addEventListener("click", function () { dlg.close(); });
  dlg.querySelector(".pv").addEventListener("click", function () { show(i - 1); });
  dlg.querySelector(".nx").addEventListener("click", function () { show(i + 1); });
  dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target.classList.contains("lb")) dlg.close(); });
  dlg.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") show(i - 1);
    else if (e.key === "ArrowRight") show(i + 1);
  });
})();
