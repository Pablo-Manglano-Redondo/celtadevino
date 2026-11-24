import html, json, sys
from datetime import date
from pathlib import Path
SITE = sys.argv[1] if len(sys.argv) > 1 else "https://celtadevino.pages.dev"
ROOT = Path(__file__).resolve().parent.parent
PUB = str(ROOT / "public")
L = json.loads((ROOT / "data" / "liga.json").read_text(encoding="utf-8"))
e = html.escape

NAMES = {"TALENTO DE BARRIO FC": "Talento de Barrio FC", "SIENAGA": "Siénaga", "PIAR FC": "Piar FC",
         "LEGION LATINA F.C.": "Legión Latina F.C.", "CELTA DE VINO": "Celta de Vino",
         "NOTTINGHAM MIEDO FC": "Nottingham Miedo FC", "VILLANUEVA DE ALCORON": "Villanueva de Alcorón",
         "F.FUTBOL": "Folla Fútbol", "LOS AVISPILLAS DE LA ALCARRIA": "Los Avispillas de la Alcarria",
         "LA PONFENTANILA": "La Ponfentanila"}
nm = lambda k: NAMES.get(k, k.title())

def dims(name):
    """Ancho y alto de un WebP leyendo su cabecera (sin dependencias)."""
    b = (Path(PUB) / "img" / f"{name}.webp").read_bytes()[:32]
    assert b[:4] == b"RIFF" and b[8:12] == b"WEBP", name
    t = b[12:16]
    if t == b"VP8 ":
        w, h = int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
    elif t == b"VP8L":
        bits = int.from_bytes(b[21:25], "little"); w, h = (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    elif t == b"VP8X":
        w, h = int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    else:
        raise ValueError(f"WebP no reconocido: {name}")
    return [str(w), str(h)]

def im(name, alt, cap=None, lazy=True, zoom=True):
    w, h = dims(name)
    cls = ' class="zoomable"' if zoom else ""
    ld = ' loading="lazy"' if lazy else ""
    fc = f"<figcaption>{cap}</figcaption>" if cap else ""
    return f'<figure><img src="/img/{name}.webp" width="{w}" height="{h}" alt="{e(alt)}"{ld} decoding="async"{cls}>{fc}</figure>'

# --- datos de los partidos (cronológico) ---
M = [
    dict(n=1, id="j1", date="2026-10-18", dl="18 de octubre", home="Celta de Vino", away="Folla Fútbol", gh=2, ga=4),
    dict(n=2, id="j2", date="2026-10-24", dl="24 de octubre · Salesianos", home="Celta de Vino", away="Talento de Barrio", gh=1, ga=1),
    dict(n=3, id="j3", date="2026-11-08", dl="8 de noviembre", home="Celta de Vino", away="Piar FC", gh=1, ga=2),
    dict(n=4, id="j4", date="2026-11-15", dl="15 de noviembre · Salesianos", home="Siénaga", away="Celta de Vino", gh=1, ga=2),
    dict(n=5, id="j5", date="2026-11-22", dl="22 de noviembre", home="Celta de Vino", away="La Ponfentanila", gh=7, ga=0),
]
for m in M:
    cf, ca = (m["gh"], m["ga"]) if m["home"] == "Celta de Vino" else (m["ga"], m["gh"])
    m["cf"], m["ca"] = cf, ca
    m["rival"] = m["away"] if m["home"] == "Celta de Vino" else m["home"]
    m["res"] = "win" if cf > ca else "draw" if cf == ca else "loss"
    m["resl"] = {"win": "Victoria", "draw": "Empate", "loss": "Derrota"}[m["res"]]
LM = {m["jornada"]: m for m in L["matches"] if "CELTA DE VINO" in (m["home"], m["away"])}
for m in M:
    lm = LM[m["n"]]
    mine_home = lm["home"] == "CELTA DE VINO"
    lcf, lca = (lm["hg"], lm["ag"]) if mine_home else (lm["ag"], lm["hg"])
    assert (lcf, lca) == (m["cf"], m["ca"]), (
        f'La crónica de la jornada {m["n"]} ({m["cf"]}-{m["ca"]}) no coincide con la liga ({lcf}-{lca})')
    m["kit"] = "h" if mine_home else "a"
    m["lm"] = lm
by = {m["id"]: m for m in M}

KITS = {"h": "Equipación local: azul y blanco", "a": "Equipación visitante: negro y azul"}
def kit(k):
    return f'<span class="kit k{k}" role="img" aria-label="{KITS[k]}" title="{KITS[k]}"></span>'

def marc(m):
    return (f'<p class="marc w-{m["res"]} k{m["kit"]}"><span class="tag">{m["resl"]}</span>{kit(m["kit"])}'
            f'<span>{nm(m["lm"]["home"])} <b>{m["lm"]["hg"]} - {m["lm"]["ag"]}</b> {nm(m["lm"]["away"])}</span></p>')

def kick(m, extra=""):
    return f'<div class="kick">Jornada {m["n"]} · <time datetime="{m["date"]}">{m["dl"]}</time>{extra}</div>'

# --- crónicas ---
j5 = f'''<article class="chron lead" id="j5" aria-labelledby="t5">
{kick(by["j5"]).replace("Jornada 5 · ", "Jornada 5 · Crónica del ")}
<h3 class="hl" id="t5">Goleada histórica: el Celta de Vino arrolla a La Ponfentanila por 7-0</h3>
<p class="dek">Portería a cero, siete goles repartidos entre cinco goleadores y soles eclipsaos.</p>
{marc(by["j5"])}
{im("j5-plantilla", "Foto de la plantilla del Celta de Vino al completo, con dos jugadores boca abajo", "La plantilla al completo, con dos miembros que prefirieron ver el partido desde otra perspectiva.", lazy=False)}
<div class="cols dc"><p>Contundente victoria de nuestro equipo dejando la portería a cero, con una gran defensa y una gran actuación de cara a portería. Buen partido, buenos goles y, sobre todo, muy buen fútbol. ¡A por los siguientes!</p></div>
<h4 class="sub2">La crónica del vestuario</h4>
<div class="cols"><p>Tomo las riendas de este perfil. Partidito como para no verlo, 7 goles como 7 soles, pero soles eclipsaos. Abre el marcador Iván con un gol que es para que pida el cambio y se vaya a echar la lotería (viendo las que ha fallado, la semana que viene sale Nicolás de titular).</p>
<p>El segundo gol no se lo van a dar a Pablo, pero es para que se lo den al portero y Diego siga sin goles en la web. Mario Pacheco, ni de delantero ni de medio: hoy no le metía gol al arcoíris ni aunque le dejaran. Completan la lista de goleadores Adrián y Mario.</p>
<p>Aitor afirma haber venido, pero vete tú a saber. La semana que viene, más, pero no mejor, porque es imposible e inviable. Este peluche se va a su estuche.</p></div>
<h4 class="sub2">Goleadores</h4>
<dl class="gol"><div><dt><b>Diego</b></dt><dd>2 goles</dd></div><div><dt><b>Mario</b></dt><dd>2 goles</dd></div><div><dt><b>Adrián</b></dt><dd>1 gol</dd></div><div><dt><b>Nicoforlán</b></dt><dd>1 gol</dd></div><div><dt><b>Iván</b></dt><dd>el gol de su vida</dd></div></dl>
<div class="mos">{"".join([
 im("j5-01", "Jugadores del Celta de Vino en marcha hacia el centro del campo tras un gol", "Marcha triunfal hacia el centro del campo, con gol incluido."),
 im("j5-02", "Jugadores del Celta de Vino abrazados celebrando un gol", "Abrazo de gol, o eso parece. Hubo siete ocasiones para repetirlo."),
 im("j5-03", "Adrián (12) disputando el balón con un rival", "Adrián (12) acabaría anotando. Su rival, no."),
 im("j5-04", "Jugador del Celta de Vino con aire tranquilo durante el partido", "Portería a cero y la calma de quien ha venido de paseo."),
 im("j5-05", "Pacheco (8) avanzando hacia la portería", "Pacheco (8) rumbo a portería. Según el vestuario, el arcoíris no corría peligro."),
 im("j5-06", "Jugador con brazalete verde y las manos en la cadera", "Brazalete verde, manos en la cadera y cara de pedir el octavo."),
 im("j5-07", "Jugador del Celta de Vino durante un disparo lejano", "Disparo lejano. No consta si fue gol, pero todo suma en un 7-0."),
 im("j5-08", "Duelo individual con un rival de camiseta negra y dorada", "Duelo individual con un rival de negro y dorado. Marcador final: 7-0."),
 im("j5-09", "Jugador del Celta de Vino pensativo", "El futbolista pensativo: ¿cómo explicar siete goles sin parecer arrogante?"),
 im("j5-10", "Jugador del Celta de Vino en el campo", "La semana que viene, más; pero no mejor."),
])}</div>
<p class="conv">Fotografías: @fotografias_likesarts.</p></article>'''

j4 = f'''<article class="chron lead" id="j4" aria-labelledby="t4">
{kick(by["j4"])}
<h3 class="hl" id="t4">¡Partidazo del Celta de Vino! Primera victoria: Siénaga 1 - 2 Celta de Vino</h3>
<p class="dek">Diego abrió el marcador, Mario anotó el segundo y Aitor se echó el partido a la espalda.</p>
{marc(by["j4"])}
{im("j4-plantilla", "Foto de la plantilla del Celta de Vino posando con una bandera", "La plantilla posa con la bandera. Por fin, una foto con motivos para sonreír.")}
<div class="cols dc"><p>¡Partidazo del equipo! Diego abrió el marcador y Mario anotó el segundo. En el último segundo encajamos un gol, pero nada empaña el gran encuentro realizado.</p>
<p>Mención especial para nuestro portero Aitor, que ha hecho un auténtico partidazo, sacando de quicio a los rivales con sus intervenciones y llevándose incluso la enhorabuena del árbitro. ¡Y qué decir de nuestros defensas, que han estado espectaculares!</p>
<p>Gracias también a toda la afición que ha venido a animarnos. Hemos sentido vuestro cariño y apoyo durante todo el partido.</p>
<p>Tras tres jornadas sin ganar, llegó la primera alegría del año. Fotografías: @fotografias_likesarts.</p></div>
<div class="mos">{"".join([
 im("j4-01", "Adrián (12) protegiendo el balón", "Adrián (12) protege el balón. El balón no había pedido ayuda."),
 im("j4-02", "Aitor, el portero, recibiendo la enhorabuena del árbitro", "Aitor, visto por última vez recibiendo la enhorabuena del árbitro."),
 im("j4-03", "Ivani (10), con el brazalete de capitán", "Ivani (10), con el brazalete bien visible por si alguien dudaba."),
 im("j4-04", "Kimbo (3) de espaldas durante una jugada", "Kimbo (3), en su posición favorita: de espaldas al peligro."),
 im("j4-05", "Duelo por el balón en la frontal del área", "Duelo en la frontal. El balón, mientras tanto, de vacaciones."),
 im("j4-06", "Jugador del Celta de Vino corriendo por la banda", "Carrera por la banda. Destino: desconocido."),
])}</div></article>'''

j3 = f'''<article class="chron" id="j3" aria-labelledby="t3">
{kick(by["j3"])}
<h3 class="hl" id="t3">Piar FC se lleva un duelo de puntería: 1-2</h3>
{marc(by["j3"])}
{im("j3-plantilla", "Foto de equipo del Celta de Vino tras el partido", "Los ciegos, afortunados, no pudieron ver esta foto de equipo.")}
<div class="cols dc"><p>Bueno, no hay un resumen muy currado esta vez: jugando como nunca, perdiendo como siempre. Qué suerte tienen los ciegos de no vernos.</p><p>Tiramos mucho a puerta, pero nuestros jugadores no la meten ni dentro ni fuera del campo. Derrota, 1-2.</p></div></article>'''

j2 = f'''<article class="chron" id="j2" aria-labelledby="t2">
{kick(by["j2"])}
<h3 class="hl" id="t2">Empate que sabe a poco ante Talento de Barrio</h3>
{marc(by["j2"])}
{im("j2-plantilla", "Foto de equipo del Celta de Vino tras el empate", "Tras el empate: caras de haber merecido más.")}
<div class="cols dc"><p>Nos vamos con un empate que nos sabe a poco, cualquiera de los dos equipos se podía haber llevado los 3 puntos. 0-1 hasta mediados de la segunda parte, donde un penalti clarísimo nos favoreció para poder marcar el empate (Iván) y luchar hasta el final.</p><p>Buenas sensaciones y a por el siguiente partido.</p></div>
<figure class="vid"><video controls playsinline preload="none" width="360" height="640" poster="/img/j2-gol-poster.webp" src="/img/j2-gol.mp4"></video><figcaption>Gol importantísimo de nuestro capitán Ivani: el penalti del empate.</figcaption></figure>
<p class="conv"><b>Convocados (17:15 h):</b> Mario, Pablo, Nicolás, Iván, Diego, David, Johan, Aitor, Zequi, Álvaro y Adrián.</p></article>'''

j1 = f'''<article class="chron" id="j1" aria-labelledby="t1">
{kick(by["j1"])}
<h3 class="hl" id="t1">Debut con derrota ante Folla Fútbol</h3>
{marc(by["j1"])}
{im("j1-plantilla", "Foto de la plantilla fundacional del Celta de Vino", "Plantilla fundacional, posando sin sospechar el gol en propia puerta que le esperaba.")}
<div class="cols dc"><p>Primer partido con un resultado desfavorable, 4-2 y a casa. Un partido tenso hasta los minutos finales en los cuales una jugada desafortunada ha provocado un gol en propia puerta que nos ponía con un 2-3 en contra, y un penalti muy claro en contra en el cual los rivales aprovechaban la oportunidad para finiquitar el resultado.</p><p><b>Conclusión: bebiendo como nunca, perdiendo como siempre.</b></p></div></article>'''


# --- datos de la liga (data/liga.json, generado por tools/sync_liga.py) ---
ME = "CELTA DE VINO"
FIELDS = {"HO1": "Horche 1", "HO2": "Horche 2", "DIO": "Diocesano", "DI2": "Diocesano 2", "SA1": "Salesianos 1", "SA2": "Salesianos 2"}
DOW = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
MONTHS = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MONTHS_L = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DOW_L = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
FETCHED = date.fromisoformat(L["fetched"])
FETCHED_ES = f'{FETCHED.day} de {MONTHS_L[FETCHED.month]} de {FETCHED.year}'
SRC = L["source"]

ST = L["standings"]
me = next(r for r in ST if r["team"] == ME)
G, E, P, GF, GC = me["pg"], me["pe"], me["pp"], me["gf"], me["gc"]
played = {}
for m in L["matches"]:
    played.setdefault(m["jornada"], []).append(m["hg"] is not None)
done = max([j for j, v in played.items() if all(v)] or [0])

def th(label, full, cls=""):
    return f'<th scope="col" class="{cls}" title="{full}">{label}</th>' if cls else f'<th scope="col" title="{full}">{label}</th>'

rows = []
for r in ST:
    c = ' class="me"' if r["team"] == ME else ""
    dg = f'{r["dg"]:+d}' if r["dg"] else "0"
    rows.append(f'<tr{c}><td class="n">{r["pos"]}</td><th scope="row">{nm(r["team"])}</th><td>{r["pj"]}</td><td class="hm">{r["pg"]}</td><td class="hm">{r["pe"]}</td><td class="hm">{r["pp"]}</td>'
                f'<td class="hm">{r["gf"]}</td><td class="hm">{r["gc"]}</td><td>{dg}</td><td class="pt">{r["pts"]}</td></tr>')
tabla = (f'<div class="tw"><table class="tabla"><caption>4ª División Guadalajara · tras la jornada {done}</caption><thead><tr>'
         + th("#", "Posición", "n") + '<th scope="col">Equipo</th>' + th("PJ", "Partidos jugados") + th("G", "Ganados", "hm") + th("E", "Empatados", "hm")
         + th("P", "Perdidos", "hm") + th("GF", "Goles a favor", "hm") + th("GC", "Goles en contra", "hm") + th("DG", "Diferencia de goles")
         + th("Pts", "Puntos") + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')

def fdate(iso):
    d = date.fromisoformat(iso)
    return d, f'{DOW[d.weekday()]} {d.day} {MONTHS[d.month]}'

nxt = next((m for m in L["matches"] if ME in (m["home"], m["away"]) and m["hg"] is None), None)
cal = []
for j in sorted(played):
    ms = [m for m in L["matches"] if m["jornada"] == j]
    d0, d1 = min(m["date"] for m in ms), max(m["date"] for m in ms)
    a, b = date.fromisoformat(d0), date.fromisoformat(d1)
    rango = f'{a.day} {MONTHS[a.month]}' if a == b else (f'{a.day}–{b.day} {MONTHS[b.month]}' if a.month == b.month else f'{a.day} {MONTHS[a.month]} – {b.day} {MONTHS[b.month]}')
    items = []
    for m in sorted(ms, key=lambda m: (m["date"], m["time"] or "99")):
        mine = ME in (m["home"], m["away"])
        d, ds = fdate(m["date"])
        cls = ["m"]
        res = ""
        if mine:
            cls.append("me")
            if m["hg"] is not None:
                cf, ca = (m["hg"], m["ag"]) if m["home"] == ME else (m["ag"], m["hg"])
                cls.append("w-" + ("win" if cf > ca else "draw" if cf == ca else "loss"))
            elif m is nxt:
                cls.append("next")
        score = f'<b>{m["hg"]} - {m["ag"]}</b>' if m["hg"] is not None else '<b class="pend">vs</b>'
        when = f'<time datetime="{m["date"]}">{ds}</time>' + (f' · {m["time"]}' if m["time"] else "")
        campo = FIELDS.get(m["field"], m["field"]) or ("campo por confirmar" if m["time"] else "")
        fld = f'<span class="fld">{campo}</span>' if campo else '<span class="fld"></span>' 
        tag = '<span class="nx">Próximo</span>' if m is nxt else ""
        ks = kit("h" if m["home"] == ME else "a") + " " if mine else ""
        items.append(f'<li class="{" ".join(cls)}"><span class="when">{ks}{when}</span>'
                     f'<span class="tm h">{nm(m["home"])}</span>{score}<span class="tm a">{nm(m["away"])}</span>{fld}{tag}</li>')
    cal.append(f'<section class="jor" aria-labelledby="cj{j}"><h3 id="cj{j}">Jornada {j} <small>{rango}{"" if any(m["time"] for m in ms) else " · horarios por confirmar"}</small></h3><ol class="mt">{"".join(items)}</ol></section>')

if nxt:
    d, ds = fdate(nxt["date"])
    casa = nxt["home"] == ME
    proximo = (f'<p class="proximo"><span class="kick">Próximo partido · Jornada {nxt["jornada"]}</span><br>'
               f'<b>{nm(nxt["home"])} - {nm(nxt["away"])}</b><br>'
               f'{DOW_L[d.weekday()]} {d.day} de {MONTHS_L[d.month]}'
               + (f' · {nxt["time"]} h' if nxt["time"] else '') + ' · '
               + (FIELDS.get(nxt["field"], nxt["field"]) or "campo por confirmar") + f' · {"en casa" if casa else "fuera"}</p>')
else:
    proximo = ""

sc = L["scorers"]
TOTAL_G = sum(s["goals"] for s in sc)
def srow(s, cls=""):
    c = f' class="{cls}"' if cls else ""
    avg = f'{s["goals"] / s["pj"]:.2f}'.replace(".", ",") if s["pj"] else "–"
    return (f'<tr{c}><td class="n">{s["rank"]}</td><th scope="row">{s["name"]}<span class="eq">{nm(s["team"])}</span></th><td class="team">{nm(s["team"])}</td>'
            f'<td class="hm">{s["pj"]}</td><td class="hm">{avg}</td><td class="pt">{s["goals"]}</td></tr>')
def stable(rows_html, caption):
    return ('<div class="tw"><table class="tabla gt"><caption>' + caption + '</caption><thead><tr>' + th("#", "Posición en el ranking", "n")
            + '<th scope="col">Jugador</th><th scope="col" class="team">Equipo</th>' + th("PJ", "Partidos jugados", "hm") + th("Media", "Goles por partido jugado", "hm")
            + th("Goles", "Goles") + '</tr></thead><tbody>' + rows_html + '</tbody></table></div>')
top = stable("".join(srow(s, "me" if s["team"] == ME else "") for s in sc[:10]), f"Máximos goleadores de la liga · {len(sc)} jugadores han marcado ({TOTAL_G} goles)")
mine = [s for s in sc if s["team"] == ME]
mine_tbl = stable("".join(srow(s) for s in mine), f'Goleadores del Celta de Vino · {sum(s["goals"] for s in mine)} goles')
if sum(s["goals"] for s in mine) != GF:
    print(f"AVISO: los goleadores del Celta suman {sum(s['goals'] for s in mine)} y el equipo lleva {GF} goles", file=sys.stderr)

def srcnote(extra=""):
    return f'<p class="src">Datos de la <a href="{SRC}" target="_blank" rel="noopener">web oficial de la liga</a> · actualizado el {FETCHED_ES}.{extra}</p>'

SEC_LIGA = f"""
<section class="sec" id="clasificacion" aria-labelledby="h-clas"><h2 id="h-clas">Clasificación</h2>
{tabla}
{srcnote(" Los puntos son 3 por victoria, 1 por empate.")}
</section>

<section class="sec" id="calendario" aria-labelledby="h-cal"><h2 id="h-cal">Calendario</h2>
<div class="vista" id="vista" hidden><button type="button" data-v="celta" aria-pressed="true">Solo el Celta</button><button type="button" data-v="all" aria-pressed="false">Toda la liga</button></div>
<div class="cal" id="cal" data-view="all">
{"".join(cal)}
</div>
{srcnote(" Las horas y los campos pueden cambiar: consulta siempre la web de la liga.")}
</section>

<section class="sec" id="goleadores" aria-labelledby="h-gol"><h2 id="h-gol">Goleadores</h2>
{top}
{mine_tbl}
{srcnote()}
</section>
"""


# --- himno ---
HIMNO = ROOT / "data" / "himno-letra.txt"
letra = ""
if HIMNO.exists():
    stanzas = [t.strip() for t in HIMNO.read_text(encoding="utf-8").split("\n\n") if t.strip()]
    letra = ('<details class="letra"><summary>Ver la letra</summary><div class="estrofas">'
             + "".join("<p>" + "<br>".join(html.escape(l) for l in st.splitlines()) + "</p>" for st in stanzas)
             + '</div><p class="aviso">Letra transcrita automáticamente a partir del audio; los [?] son pasajes que no se entienden bien.</p></details>')
w, h = dims("himno-portada")
SEC_HIMNO = f"""
<section class="sec" id="himno" aria-labelledby="h-himno"><h2 id="h-himno">El himno</h2>
<div class="himno">
<figure class="disco"><img src="/img/himno-portada.webp" width="{w}" height="{h}" alt="Portada del himno «Domingos en el barro»: una bota de fútbol entre salpicaduras de vino tinto" loading="lazy" decoding="async"></figure>
<div class="himno-txt">
<div class="kick">Himno oficial · 2:43 · 17 de noviembre</div>
<h3 class="hl">Domingos en el barro</h3>
<p>El himno oficial del Celta de Vino, publicado en nuestro Instagram. Creado con Gemini, la inteligencia artificial de Google. Dale al play, sube el volumen y brinda.</p>
<audio controls preload="none" src="/img/himno.m4a">Tu navegador no puede reproducir audio. <a href="/img/himno.m4a">Descarga el himno</a>.</audio>
{letra}
</div></div>
</section>
"""

# --- forma / cifras ---
CH = {m["n"] for m in M}  # jornadas con crónica
form = ""
for j in sorted(LM):
    lm = LM[j]
    if lm["hg"] is None:
        continue
    mine_home = lm["home"] == ME
    cf, ca = (lm["hg"], lm["ag"]) if mine_home else (lm["ag"], lm["hg"])
    res = "win" if cf > ca else "draw" if cf == ca else "loss"
    rival = nm(lm["away"] if mine_home else lm["home"])
    form += (f'<li><a class="w-{res}" href="#{"j%d" % j if j in CH else "calendario"}"><em>{ {"win": "Victoria", "draw": "Empate", "loss": "Derrota"}[res] }</em>'
             f'<b>{cf} - {ca}</b>J{j} · {rival}</a></li>')
stats = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in
                [("Puesto", f'{me["pos"]}º'), ("Puntos", me["pts"]), ("Jugados", me["pj"]), ("Ganados", G), ("Empates", E), ("Perdidos", P), ("Goles a favor", GF), ("Goles en contra", GC)])

TITLE = "El Celta de Vino · Diario de un equipo de fútbol 7"
DESC = "Diario oficial del Celta de Vino, equipo de fútbol 7 en la Liga +7: crónicas, clasificación, calendario, goleadores y fotos de cada jornada de la temporada 2026."
ld = {
    "@context": "https://schema.org", "@type": "SportsTeam", "name": "Celta de Vino", "sport": "Fútbol 7",
    "foundingDate": "2026", "logo": f"{SITE}/icon-512.png", "url": f"{SITE}/",
    "sameAs": ["https://www.instagram.com/celtadevino.2026"],
    "memberOf": {"@type": "SportsOrganization", "name": "Liga +7"},
}

page = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f4efe4" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1b1715" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{SITE}/">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="El Celta de Vino">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Escudo del Celta de Vino: cruz de Santiago burdeos con corona y copa de vino">
<meta name="twitter:card" content="summary_large_image">
<script src="/theme.js"></script>
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
<div class="w">
<header>
<div class="top"><span id="fecha">Edición digital</span><span>Temporada 2026 · Nº 1</span><span>Liga +7</span><button class="tt" id="tema" type="button" hidden>☾ Oscuro</button></div>
<h1><a href="#top" id="top">El Celta de Vino</a></h1>
<p class="sub">Diario oficial de un equipo recién nacido, con mucha sed de gloria</p>
<div class="band" aria-hidden="true"></div>
<hr class="rule">
<nav class="nav" aria-label="Secciones">
<a href="#presentacion">Presentación</a><a href="#ficha">Ficha</a><a href="#himno">Himno</a><a href="#temporada">Temporada</a><a href="#clasificacion">Clasificación</a><a href="#calendario">Calendario</a><a href="#goleadores">Goleadores</a><a href="#cronicas">Crónicas</a><a href="#breves">Breves</a>
</nav>
</header>
<main id="main">

<section class="hero" id="presentacion" aria-labelledby="t0">
<div>
<div class="kick">Presentación</div>
<h2 class="hl" id="t0">Nace el Celta de Vino: un escudo con denominación de origen</h2>
<div class="cols dc">
<p>Este año 2026 viene con novedad en los campos de fútbol 7: ha nacido el Celta de Vino. Un equipo que mezcla la pasión por los colores celestes con la sana costumbre de arreglar los partidos, y a veces las derrotas, alrededor de una buena copa.</p>
<p>Con una cruz de Santiago burdeos, una corona dorada y una copa de tinto en el centro del escudo, el club deja claro desde su fundación que aquí se viene a competir, pero también a disfrutar del tercer tiempo.</p>
<p>El equipo debuta en la Liga +7, donde se enfrentará a otros nueve conjuntos en una competición que promete emoción, sudor y alguna que otra discusión arbitral. Esta web recogerá, jornada a jornada, las crónicas de cada partido.</p>
<p>Brindemos por la temporada: que la cosecha sea buena.</p>
</div></div>
<figure class="crest"><img src="/img/escudo.webp" width="420" height="515" alt="Escudo del Celta de Vino 2026: cruz de Santiago burdeos con corona dorada y una copa de tinto en el centro" decoding="async"><figcaption>Escudo oficial · Fundado en 2026</figcaption></figure>
</section>

<section class="sec" id="ficha" aria-labelledby="h-ficha"><h2 id="h-ficha">Ficha del club</h2>
<dl class="ficha">
<div><dt>Nombre</dt><dd>Celta de Vino</dd></div>
<div><dt>Fundación</dt><dd>2026</dd></div>
<div><dt>Modalidad</dt><dd>Fútbol 7</dd></div>
<div><dt>Competición</dt><dd>Liga +7 · 10 equipos</dd></div>
<div><dt>División</dt><dd>4ª Guadalajara</dd></div>
<div><dt>Equipación local</dt><dd>{kit("h")} Azul y blanco</dd></div>
<div><dt>Equipación visitante</dt><dd>{kit("a")} Negro y azul</dd></div>
<div><dt>Escudo</dt><dd>Burdeos y oro</dd></div>
<div><dt>Instagram</dt><dd><a href="https://www.instagram.com/celtadevino.2026" target="_blank" rel="noopener">@celtadevino.2026</a></dd></div>
</dl>
<p class="more"><a href="{SRC}" target="_blank" rel="noopener">Consulta la competición completa en la web de la liga →</a></p>
</section>

{SEC_HIMNO}
<section class="sec" id="temporada" aria-labelledby="h-temp"><h2 id="h-temp">La temporada en cifras</h2>
<dl class="stats">{stats}</dl>
{proximo}
<ol class="form" aria-label="Resultados por jornada">{form}</ol>
</section>

{SEC_LIGA}
<section class="sec" id="cronicas" aria-labelledby="h-cron"><h2 id="h-cron">Crónicas de los partidos · de la más reciente a la más antigua</h2>
{j5}
{j4}
<div class="grid">
{j3}
{j2}
{j1}
</div>
<div class="brev" id="breves"><b>Breves</b><br>El equipo ya tiene <a href="#himno">himno oficial</a>, «Domingos en el barro»: se publicó en su Instagram el 17 de noviembre. Balance tras {me["pj"]} {"jornada" if me["pj"] == 1 else "jornadas"}: {G} {"victoria" if G == 1 else "victorias"}, {E} {"empate" if E == 1 else "empates"} y {P} {"derrota" if P == 1 else "derrotas"} ({GF} goles a favor y {GC} en contra).</div>
</section>

</main>
<footer>© 2026 El Celta de Vino · Edición digital · Síguenos en <a href="https://www.instagram.com/celtadevino.2026" target="_blank" rel="noopener">Instagram</a></footer>
</div>

<dialog id="visor" aria-label="Visor de fotos"><div class="lb"><img src="/img/escudo.webp" alt=""><p></p>
<button class="x" type="button" aria-label="Cerrar">×</button><button class="pv" type="button" aria-label="Foto anterior">‹</button><button class="nx" type="button" aria-label="Foto siguiente">›</button></div></dialog>
<script src="/app.js" defer></script>
</body>
</html>
'''
open(f"{PUB}/index.html", "w", encoding="utf-8").write(page)

# ficheros auxiliares
open(f"{PUB}/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
open(f"{PUB}/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}/</loc><lastmod>2026-11-24</lastmod></url></urlset>\n')
open(f"{PUB}/404.html", "w", encoding="utf-8").write(f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Fuera de juego · El Celta de Vino</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.ico"><script src="/theme.js"></script><link rel="stylesheet" href="/style.css"></head>
<body><div class="w"><h1><a href="/">El Celta de Vino</a></h1><p class="sub">Árbitro, esto es fuera de juego</p><hr class="rule"><p class="c404">Esa página no existe (o se la llevó el VAR). <a href="/">Volver a la portada →</a></p></div></body></html>
''')
print("ok", len(page))
