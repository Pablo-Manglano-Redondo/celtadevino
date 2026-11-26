// Registra el service worker (sw.js) para que la web sea instalable y funcione sin conexión.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").catch(function () {});
  });
}
