/*!
 * GENEOS UI · adaptador opcional Chart.js 4
 * Requiere Chart.js cargado en la página. No modifica los gráficos SVG existentes.
 * Datos: <script type="application/json" id="ventas">[{"label":"Ene","value":10}]</script>
 * Vista: <div class="gn-chart" data-gn-chart="bar" data-gn-engine="chartjs"
 *            data-gn-source="ventas" data-gn-title="Ventas"></div>
 */
(function (window, document) {
  "use strict";
  var instances = new WeakMap();
  var palette = ["--gn-chart-1", "--gn-chart-2", "--gn-chart-3", "--gn-chart-4", "--gn-chart-5"];

  function color(styles, name, fallback) {
    return styles.getPropertyValue(name).trim() || fallback;
  }
  function numbers(value) {
    return typeof value === "number" && isFinite(value) ? value : Number(value);
  }
  function readSeries(el) {
    var source = document.getElementById(el.getAttribute("data-gn-source") || "");
    if (!source || source.tagName !== "SCRIPT" || source.type !== "application/json") return null;
    try {
      var data = JSON.parse(source.textContent);
      if (!Array.isArray(data) || !data.length || data.some(function (d) {
        return !d || typeof d.label !== "string" || !isFinite(numbers(d.value));
      })) return null;
      return data;
    } catch (e) { return null; }
  }
  function elements(root) {
    var result = [];
    if (root && root.matches && root.matches('[data-gn-engine="chartjs"]')) result.push(root);
    return result.concat(Array.prototype.slice.call((root || document).querySelectorAll('[data-gn-engine="chartjs"]')));
  }
  function renderOne(el) {
    if (!window.Chart) return false;
    var type = el.getAttribute("data-gn-chart");
    if (["line", "bar", "donut", "doughnut", "pie"].indexOf(type) < 0) return false;
    var data = readSeries(el);
    if (!data) return false;
    var old = instances.get(el);
    if (old) { old.destroy(); instances.delete(el); }
    var styles = window.getComputedStyle(el);
    var htmlStyles = window.getComputedStyle(document.documentElement);
    var css = function (token, fallback) {
      return color(styles, token, color(htmlStyles, token, fallback));
    };
    var colors = palette.map(function (token) { return css(token, "#666"); });
    var axis = css("--gn-chart-axis", "#63636b");
    var grid = css("--gn-chart-grid", "#e4e4e7");
    var typeName = type === "donut" ? "doughnut" : type;
    var round = typeName === "doughnut" || typeName === "pie";
    var title = el.getAttribute("data-gn-title") || "Gráfico";
    var unit = el.getAttribute("data-gn-unit") || "";
    var canvas = document.createElement("canvas");
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", title);
    el.replaceChildren(canvas);
    var table = document.createElement("table");
    table.className = "gn-visually-hidden";
    var caption = document.createElement("caption");
    caption.textContent = title;
    table.appendChild(caption);
    data.forEach(function (point) {
      var row = document.createElement("tr"), th = document.createElement("th"), td = document.createElement("td");
      th.scope = "row";
      th.textContent = point.label;
      td.textContent = numbers(point.value).toLocaleString("es-AR") + (unit ? " " + unit : "");
      row.appendChild(th); row.appendChild(td); table.appendChild(row);
    });
    el.appendChild(table);
    var values = data.map(function (d) { return numbers(d.value); });
    var dataset = {
      label: title,
      data: values,
      backgroundColor: round ? data.map(function (d, i) { return d.color || colors[i % colors.length]; }) : colors[0],
      borderColor: round ? css("--gn-surface", "#fff") : colors[0],
      borderWidth: round ? 2 : 2,
      borderRadius: typeName === "bar" ? 5 : 0,
      tension: typeName === "line" ? 0.3 : 0,
      fill: false
    };
    var settings = {
      type: typeName,
      data: {labels: data.map(function (d) { return d.label; }), datasets: [dataset]},
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? false : undefined,
        plugins: {
          legend: {display: round, position: "bottom",
            labels: {color: axis, font: {family: css("--gn-font", "sans-serif")}}},
          tooltip: {callbacks: {label: function (context) {
            var value = context.parsed;
            if (typeof value === "object" && value !== null) value = value.y;
            return context.label + ": " + Number(value).toLocaleString("es-AR") + (unit ? " " + unit : "");
          }}}
        },
        scales: round ? {} : {
          x: {ticks: {color: axis}, grid: {display: false}},
          y: {ticks: {color: axis}, grid: {color: grid}, beginAtZero: typeName === "bar"}
        }
      }
    };
    try {
      var chart = new window.Chart(canvas, settings);
      instances.set(el, chart);
      el.removeAttribute("data-gn-chart-error");
      return true;
    } catch (e) {
      el.setAttribute("data-gn-chart-error", "render");
      return false;
    }
  }
  function render(root) {
    elements(root).forEach(renderOne);
  }
  function destroy(root) {
    elements(root).forEach(function (el) {
      var chart = instances.get(el);
      if (chart) { chart.destroy(); instances.delete(el); }
    });
  }
  window.GN = window.GN || {};
  window.GN.renderChartJS = render;
  window.GN.destroyChartJS = destroy;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { render(document); });
  else render(document);
  // Seguir los cambios de tema sin afectar los SVG existentes.
  var themeObserver = new MutationObserver(function (changes) {
    if (changes.some(function (change) { return change.attributeName === "data-gn-theme" || change.attributeName === "data-gn-product"; })) render(document);
  });
  themeObserver.observe(document.documentElement, {attributes: true, attributeFilter: ["data-gn-theme", "data-gn-product"]});
})(window, document);
