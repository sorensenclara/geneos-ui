/* GENEOS UI · interacción propia del catálogo (selector de producto, modo oscuro, demos) */
(function () {
  "use strict";
  var root = document.documentElement;
  var KEY_P = "gn-kit-product";
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // ---- producto
  var switches = Array.prototype.slice.call(document.querySelectorAll("[data-kit-switch]"));
  function applyProduct(key, persist) {
    if (!document.querySelector('[data-kit-switch="' + key + '"]')) return;
    root.setAttribute("data-gn-product", key);
    switches.forEach(function (b) { b.setAttribute("aria-checked", b.getAttribute("data-kit-switch") === key ? "true" : "false"); });
    document.querySelectorAll("[data-kit-product]").forEach(function (el) { el.hidden = el.getAttribute("data-kit-product") !== key; });
    document.querySelectorAll("[data-gn-sidebar]").forEach(function (sb) { sb.hidden = sb.id !== "gn-sidebar-" + key; });
    if (persist) set(KEY_P, key);
    if (window.GN && GN.renderCharts) GN.renderCharts(document);
    if (window.GN && GN.syncSidebars) GN.syncSidebars();
  }
  switches.forEach(function (b, i) {
    b.addEventListener("click", function () { applyProduct(b.getAttribute("data-kit-switch"), true); GN.announce("Tema " + b.textContent.trim()); });
    b.addEventListener("keydown", function (e) {
      var n = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
      if (!n) return; e.preventDefault();
      var t = switches[(i + n + switches.length) % switches.length]; t.focus(); t.click();
    });
  });
  var fromHash = (location.hash || "").replace("#", "");
  var initial = document.querySelector('[data-kit-switch="' + fromHash + '"]') ? fromHash : get(KEY_P);
  if (initial) applyProduct(initial, false);

  // El modo claro/oscuro lo maneja geneos-ui.js (GN.setTheme, data-gn-theme-switch):
  // arranca en claro y recuerda la elección en localStorage ("gn-theme").

  // ---- grilla de íconos a partir del sprite
  var grid = document.getElementById("kit-icons");
  if (grid) {
    var html = "";
    document.querySelectorAll("svg defs symbol[id]").forEach(function (s) {
      html += '<li><svg class="gn-icon" aria-hidden="true"><use href="#' + s.id + '"/></svg>' + s.id + "</li>";
    });
    grid.innerHTML = html;
  }

  // ---- demo de botón con carga
  var save = document.getElementById("kit-save");
  if (save) save.addEventListener("click", function () {
    GN.setLoading(save, true, "Guardando…");
    setTimeout(function () { GN.setLoading(save, false); GN.toast("Cambios guardados.", { kind: "good" }); }, 1400);
  });

  // ---- formulario de ejemplo: no se envía
  var form = document.getElementById("kit-form");
  if (form) form.addEventListener("submit", function (e) {
    e.preventDefault();
    GN.toast("Corregí los 2 campos marcados antes de guardar.", { kind: "critical", title: "No se guardó" });
    var first = form.querySelector('[aria-invalid="true"]'); if (first) first.focus();
  });

  // ---- pills filtran la tabla visible por estado
  document.addEventListener("gn:pill", function (e) {
    var v = e.detail.value || "";
    document.querySelectorAll('[data-kit-product]:not([hidden]) table tbody tr').forEach(function (tr) {
      var badge = tr.querySelector("td[data-value] .gn-badge");
      var kind = badge ? (badge.className.match(/gn-badge--(good|warning|critical|info)/) || [])[1] : "";
      tr.hidden = !!v && kind !== v;
    });
  });
  var clear = document.getElementById("kit-clear-filters");
  if (clear) clear.addEventListener("click", function () {
    document.querySelectorAll("#kit-filters-card [data-gn-remove-filter]").forEach(function (b) { b.click(); });
    GN.announce("Filtros quitados");
  });
})();
