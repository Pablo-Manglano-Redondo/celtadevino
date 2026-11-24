#!/usr/bin/env python3
"""Descarga clasificación, calendario y goleadores de la 4ª División Guadalajara
(Liga A+7, ligamas7.com) y los guarda en data/liga.json.

Uso:  python3 -I tools/sync_liga.py
Solo usa la librería estándar. La web es ASP.NET: hace falta una sesión (cookie)
para que table/calendar/stats_scorers apunten a la competición correcta, y el
ranking de goleadores está paginado mediante postbacks.
"""
import html, http.cookiejar, json, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.ligamas7.com/mod/soccer/"
SITUATION = 15976          # 4ª DIVISION GUADALAJARA, temporada 2026
UA = {"User-Agent": "Mozilla/5.0 (compatible; celtadevino-sync)"}
OUT = Path(__file__).resolve().parent.parent / "data" / "liga.json"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def get(path, data=None):
    req = urllib.request.Request(BASE + path, data=data, headers=UA)
    with opener.open(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def text(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def nice(name):
    """'JEFERSON ANDREY espinal' -> 'Jeferson Andrey Espinal'."""
    small = {"de", "del", "la", "las", "los", "y"}
    words = re.sub(r"\s+", " ", name.strip()).lower().split(" ")
    return " ".join(w if (i and w in small) else w.capitalize() for i, w in enumerate(words))


def standings(h):
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, flags=re.S):
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
        cells = [c for c in cells if c != ""]
        if len(cells) >= 11 and cells[0].isdigit() and all(re.fullmatch(r"-?\d+", c) for c in cells[2:11]):
            n = list(map(int, cells[2:11]))
            rows.append(dict(pos=int(cells[0]), team=cells[1], pj=n[0], pg=n[1], pe=n[2], pp=n[3],
                             gf=n[4], gc=n[5], dg=n[6], sn=n[7], pts=n[8]))
    return rows


def calendar(h):
    out = []
    marks = list(re.finditer(r"rptCalendarioJornada_ctl(\d+)_dgrPartidos_ctl\d+_lblFecha\"", h))
    for i, mk in enumerate(marks):
        row = h[mk.start():(marks[i + 1].start() if i + 1 < len(marks) else len(h))]

        def f(idn):
            m = re.search(r'_%s"[^>]*>([^<]*)<' % idn, row)
            return html.unescape(m.group(1)).strip() if m else ""
        m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", f("lblMarcador") or "")
        out.append(dict(jornada=int(mk.group(1)) + 1,
                        date=datetime.strptime(f("lblFecha"), "%d.%m.%Y").date().isoformat(),
                        time=f("lblHora"), field=f("lblCampo"),
                        home=f("hlkLocal"), away=f("hlkVisitante"),
                        hg=int(m.group(1)) if m else None, ag=int(m.group(2)) if m else None))
    return out


def hidden(h):
    return {k: (re.search(r'id="%s" value="([^"]*)"' % k, h) or [None, ""])[1]
            for k in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")}


def scorers():
    h = get("stats_scorers.aspx")
    pages = [h]
    n = max(map(int, re.findall(r"Page\$(\d+)", h)), default=1)
    for p in range(2, n + 1):
        form = {"__EVENTTARGET": "ctl00$ContentPlaceHolder1$dgrListado", "__EVENTARGUMENT": f"Page${p}",
                **hidden(pages[-1])}
        pages.append(get("stats_scorers.aspx", urllib.parse.urlencode(form).encode()))
    res, seen = [], set()
    for h in pages:
        marks = [m.start() for m in re.finditer(r"dgrListado_ctl\d+_lblOrden", h)]
        for i, st in enumerate(marks):
            row = h[st:(marks[i + 1] if i + 1 < len(marks) else len(h))]

            def f(idn):
                m = re.search(r'_%s"[^>]*>([^<]*)<' % idn, row)
                return html.unescape(m.group(1)).strip() if m else ""
            name, team = f("hlkJugador") or f("lblToolTipNombre"), f("lblToolTipJugadorInfoEquipo")
            key = (name.lower(), team)
            if key in seen:
                continue
            seen.add(key)
            res.append(dict(rank=int(f("lblOrden")), name=nice(name), team=team, pj=int(f("lblPartidosJugados") or 0),
                            goals=int(f("lblTotalGoles"))))
    res.sort(key=lambda r: r["rank"])
    return res


def main():
    get(f"situation.aspx?itm={SITUATION}")  # fija la competición en la sesión
    data = dict(
        source="https://www.ligamas7.com/mod/soccer/situation.aspx?itm=%d" % SITUATION,
        competition="4ª División Guadalajara · Fútbol 7 · Liga A+7 · Temporada 2026",
        fetched=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        standings=standings(get("table.aspx")),
        matches=calendar(get("calendar.aspx")),
        scorers=scorers(),
    )
    names = [r["team"] for r in data["standings"]]
    for m in data["matches"]:
        for k in ("home", "away"):
            hit = [n for n in names if n.startswith(m[k])]
            assert len(hit) == 1, "equipo no reconocido: " + m[k]
            m[k] = hit[0]
    assert len(data["standings"]) == 10, "clasificación inesperada"
    assert len(data["matches"]) == 90, "calendario inesperado: %d" % len(data["matches"])
    assert data["scorers"], "sin goleadores"
    OUT.parent.mkdir(exist_ok=True)
    if OUT.exists():
        prev = json.loads(OUT.read_text(encoding="utf-8"))
        if {k: v for k, v in prev.items() if k != "fetched"} == {k: v for k, v in data.items() if k != "fetched"}:
            print("Sin cambios en la liga (fecha de datos:", prev["fetched"] + ")")
            return
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("OK ->", OUT, "|", len(data["standings"]), "equipos,", len(data["matches"]), "partidos,",
          len(data["scorers"]), "goleadores")


if __name__ == "__main__":
    sys.exit(main())
