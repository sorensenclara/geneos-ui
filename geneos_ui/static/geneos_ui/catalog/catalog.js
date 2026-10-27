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
    // el buscador del encabezado cambia solo el texto de ayuda (el diseño del topbar no cambia)
    var gs = document.getElementById("kit-global-search");
    if (gs && gs.dataset.kitPlaceholders) { try { gs.placeholder = JSON.parse(gs.dataset.kitPlaceholders)[key] || gs.placeholder; } catch (e) {} }
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

  // ---- demo de botón con carga
  document.querySelectorAll("[data-kit-save]").forEach(function (save) {
    save.addEventListener("click", function () {
      GN.setLoading(save, true, "Guardando…");
      setTimeout(function () { GN.setLoading(save, false); GN.toast("Cambios guardados.", { kind: "good" }); }, 1400);
    });
  });

  // ---- formulario de ejemplo: no se envía
  document.querySelectorAll("[data-kit-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      GN.toast("Corregí los " + form.dataset.kitErrors + " campos marcados antes de guardar.", { kind: "critical", title: "No se guardó" });
      var first = form.querySelector('[aria-invalid="true"]'); if (first) first.focus();
    });
  });

  // ---- pills de "Filtros combinados" filtran la tabla visible por estado
  document.addEventListener("gn:pill", function (e) {
    if (!e.target.closest || !e.target.closest("[data-kit-table-pills]")) return;
    var v = e.detail.value || "";
    document.querySelectorAll('[data-kit-product]:not([hidden]) table tbody tr').forEach(function (tr) {
      var badge = tr.querySelector("td[data-value] .gn-badge");
      var kind = badge ? (badge.className.match(/gn-badge--(good|warning|critical|info)/) || [])[1] : "";
      tr.hidden = !!v && kind !== v;
    });
  });
  document.querySelectorAll("[data-kit-clear-filters]").forEach(function (clear) {
    clear.addEventListener("click", function () {
      clear.closest("[data-kit-filters-card]").querySelectorAll("[data-gn-remove-filter]").forEach(function (b) { b.click(); });
      GN.announce("Filtros quitados");
    });
  });
  // ---- iconografía por producto: filtros por producto, módulo y estado
  var lib = document.querySelector("[data-kit-iconlib]");
  if (lib) {
    var selP = lib.querySelector("[data-kit-ic-product]"), selM = lib.querySelector("[data-kit-ic-module]"), selS = lib.querySelector("[data-kit-ic-set]");
    var pills = lib.querySelector("[data-kit-ic-status]"), count = lib.querySelector("[data-kit-ic-count]");
    var empty = lib.querySelector("[data-kit-ic-empty]"), cards = lib.querySelectorAll(".kit-ic");
    var status = "";
    var modOptions = Array.prototype.slice.call(selM.options);
    function refreshModules() {
      // solo los módulos que existen en el producto elegido
      var prod = selP.value, present = {};
      cards.forEach(function (c) { if (!prod || (" " + c.dataset.products + " ").indexOf(" " + prod + " ") > -1) present[c.dataset.module] = 1; });
      modOptions.forEach(function (o) { o.hidden = !!o.value && !present[o.value]; });
      if (selM.selectedOptions[0] && selM.selectedOptions[0].hidden) selM.value = "";
    }
    function apply() {
      var prod = selP.value, mod = selM.value, n = 0;
      cards.forEach(function (c) {
        var ok = (!prod || (" " + c.dataset.products + " ").indexOf(" " + prod + " ") > -1) &&
                 (!mod || c.dataset.module === mod) && (!status || c.dataset.status === status) &&
                 (!selS.value || c.dataset.set === selS.value);
        c.hidden = !ok; if (ok) n++;
      });
      count.textContent = n + (n === 1 ? " registro" : " registros");
      empty.hidden = n > 0;
    }
    selP.addEventListener("change", function () { refreshModules(); apply(); });
    selM.addEventListener("change", apply);
    selS.addEventListener("change", apply);
    // fondo de las miniaturas: no cambia los archivos, solo el fondo de la vista previa
    var grid = lib.querySelector("[data-kit-ic-grid]");
    lib.querySelector("[data-kit-ic-bg]").addEventListener("gn:pill", function (e) { grid.dataset.bg = e.detail.value || "auto"; });
    pills.addEventListener("gn:pill", function (e) { status = e.detail.value || ""; apply(); });
  }
})();
