# El Celta de Vino · Diario

Web estática de https://celtadevino.pages.dev. Lo que se sirve vive en `public/`.

## Cómo está montado
- `tools/sync_liga.py` descarga de la web de la liga (4ª División Guadalajara, ligamas7.com)
  la clasificación, el calendario completo y el ranking de goleadores → `data/liga.json`.
- `tools/build.py` genera `public/index.html` con las crónicas (texto escrito a mano dentro
  del propio script) y los datos de `data/liga.json`. Comprueba que las crónicas cuadran con la
  clasificación oficial (G/E/P y goles) y que los goleadores del Celta suman sus goles.
- `public/` (CSS, JS, imágenes, `_headers`…) es estático; no hay build de frontend.

## App instalable (PWA)
La web se puede instalar en el móvil y en el escritorio ("Añadir a pantalla de inicio" / "Instalar").
- `public/manifest.webmanifest`: nombre, colores e iconos (`icon-192/512.png` y los *maskable*
  `icon-maskable-192/512.png`, que se regeneran desde el escudo con `python3 -I tools/icons.py`).
- `public/sw.js` (lo registra `public/pwa.js` en todas las páginas): HTML, CSS y JS van **primero a la
  red** (los datos de la liga siempre salen frescos) y sin conexión se sirve la última copia; si no hay
  copia, la página `/offline` (la genera `build.py`). Las imágenes se sirven desde la caché y se
  refrescan en segundo plano; vídeo y audio no se cachean.
- Si cambias la lista `PRECACHE` o la estrategia de `sw.js`, sube `VERSION` para limpiar las cachés viejas.
- `_headers` sirve `sw.js` y el manifest con `Cache-Control: no-cache` y su `Content-Type` correcto.

## Comandos
- `npm run sync`   → refresca los datos de la liga y regenera la página.
- `npm run build`  → regenera la página con los datos que ya hay.
- `npm run dev`    → servidor local con las cabeceras de `_headers` aplicadas.
- `npm run deploy` → sync + publica en Cloudflare Pages (proyecto `celtadevino`).
  Requiere `npx wrangler login` con la cuenta de Cloudflare de Pablo Manglano.

## Actualización automática
`.github/workflows/actualizar-liga.yml` se ejecuta **todos los días, 4 veces** (07:30, 12:30, 18:30 y 23:30 UTC; el repositorio es público, así que Actions es gratis):
descarga la liga, y **solo si hay cambios** regenera la web, la despliega en Cloudflare Pages
y guarda `data/liga.json` en el repositorio. Necesita los secretos `CLOUDFLARE_API_TOKEN` (permiso
*Cloudflare Pages: Edit*) y `CLOUDFLARE_ACCOUNT_ID`. También se puede lanzar a mano desde la pestaña
Actions ("Run workflow", con la opción de forzar el despliegue).
Clasificación, calendario, goleadores, cifras y "Breves" se actualizan solos; las **crónicas** siguen
siendo manuales (el script se detiene si una crónica no coincide con el marcador oficial).

## Añadir una jornada nueva
1. En `tools/build.py`: añade el partido a la lista `M`, escribe su crónica (`j6 = ...`, mismo
   formato que `j5`), y añádela al principio de las crónicas (orden: más reciente arriba).
2. Fotos: WebP de ~600-900 px en `public/img/`, con `class="zoomable"` para el visor.
3. Actualiza el texto de "Breves" si quieres, y `npm run deploy`.
Si el resultado de la crónica no coincide con la liga, `build.py` se detiene y avisa.
