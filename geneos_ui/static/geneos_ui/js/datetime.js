/*!
 * GENEOS UI · fecha y hora (0.5.0)
 *
 * gn-popover   panel flotante no modal: se ubica abajo o arriba del control,
 *              no lo recortan los contenedores con overflow y en pantallas
 *              chicas se muestra como hoja inferior. Escape lo cierra y
 *              devuelve el foco al botón que lo abrió.
 * gn-calendar  grilla de días de Cally (componentes web con ARIA y teclado:
 *              flechas, Inicio/Fin, RePág/AvPág) con los tokens de GENEOS UI.
 * gn-time      hora y minutos con dos <select> nativos.
 *
 * Selectores: <span class="gn-datetime" data-gn-datetime="datetime|date|time">
 * con un único <input> adentro (lo genera el widget de Django). Sin JS el
 * input es nativo y envía ISO; con JS pasa a texto con dd/mm/aaaa HH:mm, que
 * es lo mismo que se envía (el widget lo convierte a ISO en el servidor).
 *
 * Cally se carga aparte como módulo (vendor/cally/cally.js). Si no carga,
 * los campos de fecha quedan nativos y siguen funcionando.
 */
(function (window, document) {
  "use strict";

  var GN = window.GN = window.GN || {};
  var SHEET = window.matchMedia("(max-width: 480px)");
  var uid = 0;

  function nextId(prefix) { uid += 1; return "gn-" + prefix + "-" + uid; }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function icon(id) { return '<svg class="gn-icon" aria-hidden="true"><use href="#' + id + '"/></svg>'; }
  function el(tag, cls, attrs) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    return e;
  }
  function addToken(node, attr, token) {
    var list = (node.getAttribute(attr) || "").split(/\s+/).filter(Boolean);
    if (list.indexOf(token) < 0) list.push(token);
    node.setAttribute(attr, list.join(" "));
  }
  function removeToken(node, attr, token) {
    var list = (node.getAttribute(attr) || "").split(/\s+/).filter(function (t) { return t && t !== token; });
    if (list.length) node.setAttribute(attr, list.join(" ")); else node.removeAttribute(attr);
  }
  function fire(node, type) { node.dispatchEvent(new Event(type, { bubbles: true })); }

  // ------------------------------------------------------------ lectura
  // Mismas reglas que geneos_ui/widgets.py (parse_date, parse_time, parse_datetime).
  function mkDate(y, m, d) {
    var dt = new Date(Date.UTC(y, m - 1, d));
    return dt.getUTCFullYear() === y && dt.getUTCMonth() === m - 1 && dt.getUTCDate() === d ? { y: y, m: m, d: d } : null;
  }
  function parseDate(s) {
    s = String(s == null ? "" : s).trim();
    var m = /^(\d{1,2})[\/.\-](\d{1,2})[\/.\-](\d{2}|\d{4})$/.exec(s);
    if (m) return mkDate(m[3].length === 2 ? 2000 + Number(m[3]) : Number(m[3]), Number(m[2]), Number(m[1]));
    m = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(s);
    return m ? mkDate(Number(m[1]), Number(m[2]), Number(m[3])) : null;
  }
  function parseTime(s) {
    s = String(s == null ? "" : s).trim();
    var m = /^(\d{1,2})(?:[:.h](\d{2}))?(?::(\d{2}))?\s*(?:hs?)?$/i.exec(s) || /^(\d{2})(\d{2})$/.exec(s);
    if (!m) return null;
    var h = Number(m[1]), mi = Number(m[2] || 0);
    return h > 23 || mi > 59 ? null : { h: h, mi: mi };
  }
  function parseDateTime(s) {
    var m = /^(\S+?)(?:\s*,\s*|\s+|T)(\S+(?:\s*hs?)?)$/i.exec(String(s == null ? "" : s).trim());
    if (!m) return null;
    var d = parseDate(m[1]), t = parseTime(m[2]);
    return d && t ? { date: d, time: t } : null;
  }
  function fmtDate(d) { return pad(d.d) + "/" + pad(d.m) + "/" + d.y; }
  function isoDate(d) { return d.y + "-" + pad(d.m) + "-" + pad(d.d); }
  function fmtTime(t) { return pad(t.h) + ":" + pad(t.mi); }
  function today() { var n = new Date(); return { y: n.getFullYear(), m: n.getMonth() + 1, d: n.getDate() }; }
  function now(step) {
    var n = new Date(), mi = Math.ceil(n.getMinutes() / step) * step, h = n.getHours();
    if (mi >= 60) { mi = 0; h = (h + 1) % 24; }
    return { h: h, mi: mi };
  }

  var KINDS = {
    datetime: {
      parse: parseDateTime, calendar: true, time: true, icon: "i-calendar",
      fmt: function (v) { return fmtDate(v.date) + " " + fmtTime(v.time); },
      iso: function (v) { return isoDate(v.date) + "T" + fmtTime(v.time); },
      label: "Elegir fecha y hora", invalid: "Ingresá una fecha y hora válidas", noun: "una fecha y hora",
    },
    date: {
      parse: function (s) { var d = parseDate(s); return d && { date: d }; }, calendar: true, time: false, icon: "i-calendar",
      fmt: function (v) { return fmtDate(v.date); }, iso: function (v) { return isoDate(v.date); },
      label: "Elegir fecha", invalid: "Ingresá una fecha válida", noun: "una fecha",
    },
    time: {
      parse: function (s) { var t = parseTime(s); return t && { time: t }; }, calendar: false, time: true, icon: "i-clock",
      fmt: function (v) { return fmtTime(v.time); }, iso: function (v) { return fmtTime(v.time); },
      label: "Elegir hora", invalid: "Ingresá una hora válida", noun: "una hora",
    },
  };
  var PLACEHOLDER = { datetime: "dd/mm/aaaa HH:mm", date: "dd/mm/aaaa", time: "HH:mm" };

  // ------------------------------------------------------------ gn-popover
  var current = null; // { panel, anchor, opener, root, onClose }

  // Ubicación en escritorio (position: fixed, medida contra la ventana):
  //   1. abajo del campo, si entra entero;
  //   2. si no, arriba (sin tapar la etiqueta del campo);
  //   3. si no, se desplaza lo justo el contenedor con scroll del campo para
  //      que entre abajo o arriba, sin sacar el campo de la vista;
  //   4. si tampoco, al costado del campo (derecha o izquierda), entero y a la
  //      vista; o, si no hay lugar al costado, entero dentro de la ventana;
  //   5. solo si el panel es más alto que la ventana: altura limitada con
  //      scroll interno y el pie («Ahora» / «Listo») fijo, siempre visible.
  // Horizontalmente se alinea con el borde izquierdo del campo, o con el
  // derecho si no entra. Al desplazar la página o cambiar el tamaño de la
  // ventana (follow = true) acompaña al campo: no desplaza nada por su cuenta y
  // conserva su ubicación mientras siga entrando.
  var GAP = 6, EDGE = 8;

  // franja superior tapada por una barra fija o pegajosa (la topbar del layout)
  function topLimit() {
    var bar = document.querySelector(".gn-topbar");
    if (bar) {
      var pos = window.getComputedStyle(bar).position;
      if (pos === "fixed" || pos === "sticky") return Math.max(EDGE, bar.getBoundingClientRect().bottom + EDGE);
    }
    return EDGE;
  }

  // contenedor que desplaza al campo (el documento o un ancestro con overflow)
  function scrollParent(node) {
    for (var n = node.parentElement; n && n !== document.body && n !== document.documentElement; n = n.parentElement) {
      var oy = window.getComputedStyle(n).overflowY;
      if ((oy === "auto" || oy === "scroll") && n.scrollHeight > n.clientHeight) return n;
    }
    return document.scrollingElement || document.documentElement;
  }

  function place(p, noScroll, follow) {
    var panel = p.panel;
    var sheet = SHEET.matches;
    panel.classList.toggle("gn-popover--sheet", sheet);
    panel.style.maxHeight = "";
    panel.classList.remove("is-clamped");
    if (sheet) { panel.style.top = panel.style.left = ""; panel.classList.remove("is-above", "is-side"); return; }
    var r = p.anchor.getBoundingClientRect();
    var vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var w = panel.offsetWidth, h = panel.offsetHeight;
    var minTop = topLimit(), maxBottom = vh - EDGE;
    // arriba se mide desde la etiqueta del campo, para no taparla
    var field = p.root && p.root.closest(".gn-field");
    var labelTop = field ? field.getBoundingClientRect().top : r.top;
    var below = maxBottom - (r.bottom + GAP), above = (labelTop - GAP) - minTop;
    var at = {
      below: function () { return { top: r.bottom + GAP, mode: "below" }; },
      above: function () { return { top: labelTop - GAP - h, mode: "above" }; },
    };

    if (follow) {
      noScroll = true;
      var prev = panel.getAttribute("data-gn-place");
      var offscreen = r.bottom < minTop || r.top > vh;
      if (prev === "below" && (offscreen || h <= below)) return finish(p, at.below(), r, w, vw);
      if (prev === "above" && (offscreen || h <= above)) return finish(p, at.above(), r, w, vw);
    }
    if (h <= below) return finish(p, at.below(), r, w, vw);
    if (h <= above) return finish(p, at.above(), r, w, vw);

    if (!noScroll) {
      var sc = scrollParent(p.anchor);
      var isDoc = sc === document.scrollingElement || sc === document.documentElement;
      var room = isDoc ? sc.scrollHeight - vh - window.scrollY : sc.scrollHeight - sc.clientHeight - sc.scrollTop;
      var up = isDoc ? window.scrollY : sc.scrollTop;
      var needDown = h - below, needUp = h - above;
      // instantáneo aunque la página tenga scroll-behavior: smooth (se mide enseguida)
      var scrollBy = function (dy) { (isDoc ? window : sc).scrollBy({ top: dy, left: 0, behavior: "instant" }); };
      // bajar la página: el campo sube y queda lugar abajo (sin que el campo pase bajo la barra)
      if (needDown <= room && labelTop - needDown >= minTop) { scrollBy(needDown); return place(p, true); }
      // subir la página: el campo baja y queda lugar arriba (sin que salga por abajo)
      if (needUp <= up && r.bottom + needUp <= maxBottom) { scrollBy(-needUp); return place(p, true); }
    }

    var avail = maxBottom - minTop;
    if (h <= avail) {
      // entero y a la vista: al costado del campo si hay lugar, o dentro de la ventana
      var top = Math.min(Math.max(r.top - 40, minTop), maxBottom - h);
      if (r.right + GAP + w <= vw - EDGE) return finish(p, { top: top, left: r.right + GAP, mode: "side" }, r, w, vw);
      if (r.left - GAP - w >= EDGE) return finish(p, { top: top, left: r.left - GAP - w, mode: "side" }, r, w, vw);
      return finish(p, { top: below >= above ? maxBottom - h : minTop, mode: below >= above ? "below" : "above" }, r, w, vw);
    }
    // más alto que la ventana: scroll interno, con el pie siempre a la vista
    panel.style.maxHeight = avail + "px";
    panel.classList.add("is-clamped");
    return finish(p, { top: minTop, mode: "clamped" }, r, w, vw);
  }

  function finish(p, pos, r, w, vw) {
    var left = pos.left;
    if (left == null) {
      left = r.left;
      if (left + w > vw - EDGE) left = r.right - w;
    }
    var panel = p.panel;
    panel.style.top = Math.round(pos.top) + "px";
    panel.style.left = Math.round(Math.max(EDGE, Math.min(left, vw - EDGE - w))) + "px";
    panel.setAttribute("data-gn-place", pos.mode);
    panel.classList.toggle("is-above", pos.mode === "above");
    panel.classList.toggle("is-side", pos.mode === "side");
  }

  // Un ancestro con transform, filter, contain… se vuelve la referencia de
  // position: fixed (el panel quedaría corrido) y, si además tiene overflow,
  // lo recortaría. En ese caso el panel se
  // lleva, mientras está abierto, al final del <body> (o del <dialog> abierto
  // que lo contiene, para seguir en la capa superior) y vuelve al cerrarse.
  function trapsFixed(node) {
    for (var n = node.parentElement; n && n !== document.body; n = n.parentElement) {
      var s = window.getComputedStyle(n);
      if (s.transform !== "none" || s.filter !== "none" || s.perspective !== "none" ||
          (s.backdropFilter && s.backdropFilter !== "none") || /paint|layout|strict|content/.test(s.contain || "") ||
          /transform|filter|perspective/.test(s.willChange || "")) return true;
    }
    return false;
  }

  function openPopover(panel, anchor, opener, opts) {
    opts = opts || {};
    if (current && current.panel !== panel) closePopover(false);
    var home = null;
    if (panel.parentNode && trapsFixed(panel)) {
      home = { parent: panel.parentNode, next: panel.nextSibling };
      var dlg = panel.parentNode.closest && panel.parentNode.closest("dialog[open]");
      (dlg || document.body).appendChild(panel);
      panel.classList.add("is-portaled");
    }
    panel.hidden = false;
    if (opener) opener.setAttribute("aria-expanded", "true");
    current = { panel: panel, anchor: anchor || opener, opener: opener, root: opts.root || null, onClose: opts.onClose, home: home };
    place(current);
    panel.classList.add("is-open");
    // el contenido (p. ej. el calendario) puede terminar de dibujarse después: se reubica
    if (window.ResizeObserver) {
      if (!panel.__gnResize) panel.__gnResize = new ResizeObserver(function () { if (current && current.panel === panel) place(current); });
      panel.__gnResize.observe(panel);
    }
  }

  function closePopover(restoreFocus) {
    var p = current;
    if (!p) return;
    current = null;
    p.panel.hidden = true;
    p.panel.classList.remove("is-open");
    if (p.panel.__gnResize) p.panel.__gnResize.disconnect();
    if (p.home) {
      p.home.parent.insertBefore(p.panel, p.home.next && p.home.next.parentNode === p.home.parent ? p.home.next : null);
      p.panel.classList.remove("is-portaled");
    }
    if (p.opener) p.opener.setAttribute("aria-expanded", "false");
    if (p.onClose) p.onClose();
    if (restoreFocus && p.opener) p.opener.focus();
  }

  // Panel llevado al <body>: Tab al salir por el final vuelve al botón que lo
  // abrió, como si siguiera en su lugar del formulario.
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Tab" || !current || !current.home) return;
    var panel = current.panel;
    var light = Array.prototype.filter.call(panel.querySelectorAll("button, input, select, textarea, [tabindex]:not([tabindex='-1'])"),
      function (n) { return !n.disabled && n.tabIndex >= 0 && n.getClientRects().length; });
    if (!e.shiftKey && document.activeElement === light[light.length - 1]) { e.preventDefault(); closePopover(true); }
  });

  function inside(p, node) {
    return !!node && (p.panel.contains(node) || (p.opener && p.opener.contains(node)) || (p.root && p.root.contains(node)));
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && current) {
      e.preventDefault(); // dentro de un <dialog> no cierra el modal
      e.stopPropagation();
      closePopover(true);
    }
  }, true);
  document.addEventListener("pointerdown", function (e) {
    if (current && !inside(current, e.target)) closePopover(false);
  }, true);
  document.addEventListener("focusin", function (e) {
    if (current && !inside(current, e.target)) closePopover(false);
  });
  // Al cambiar el tamaño de la ventana se vuelve a ubicar desde cero; si el
  // campo quedó fuera de la vista, primero se lo trae (el panel va con él).
  window.addEventListener("resize", function () {
    if (!current || SHEET.matches) { if (current) place(current, true); return; }
    var r = current.anchor.getBoundingClientRect();
    if (r.bottom < topLimit() || r.top > window.innerHeight) current.anchor.scrollIntoView({ block: "center", behavior: "instant" });
    place(current);
  });
  window.addEventListener("scroll", function (e) {
    // el scroll interno del propio panel no lo mueve
    if (current && !(e.target instanceof Node && current.panel.contains(e.target))) place(current, true, true);
  }, true);
  if (SHEET.addEventListener) SHEET.addEventListener("change", function () { if (current) place(current, true); });

  function firstFocusable(root) {
    return root.querySelector('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])');
  }

  // <button data-gn-popover="id">  <div class="gn-popover" id="id" role="dialog" aria-label="…" hidden>
  function initPopoverTriggers(root) {
    Array.prototype.forEach.call(root.querySelectorAll("[data-gn-popover]"), function (btn) {
      if (btn.__gnPopover) return;
      var panel = document.getElementById(btn.getAttribute("data-gn-popover"));
      if (!panel) return;
      btn.__gnPopover = true;
      btn.setAttribute("aria-haspopup", "dialog");
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-controls", panel.id);
      btn.addEventListener("click", function () {
        if (current && current.panel === panel) { closePopover(true); return; }
        openPopover(panel, btn, btn);
        var f = firstFocusable(panel);
        (f || panel).focus();
      });
      panel.addEventListener("click", function (e) {
        if (e.target.closest("[data-gn-popover-close]")) closePopover(true);
      });
    });
  }

  // ------------------------------------------------------------ gn-calendar
  function fillCalendar(cal) {
    // locale y primer día conviene escribirlos en el HTML: si Cally ya dibujó, se
    // fijan también como propiedades para que actualice los nombres de los días
    if (!cal.getAttribute("locale")) { cal.setAttribute("locale", "es-AR"); cal.locale = "es-AR"; }
    if (!cal.hasAttribute("first-day-of-week")) cal.setAttribute("first-day-of-week", "1");
    cal.classList.add("gn-calendar");
    if (!cal.querySelector('[slot="previous"]')) {
      cal.insertAdjacentHTML("afterbegin",
        '<span slot="previous" class="gn-calendar__nav">' + icon("i-chevleft") + '<span class="gn-visually-hidden">Mes anterior</span></span>' +
        '<span slot="next" class="gn-calendar__nav">' + icon("i-chevright") + '<span class="gn-visually-hidden">Mes siguiente</span></span>');
    }
    if (!cal.querySelector('[slot="heading"]')) {
      // Cally muestra solo el año en el encabezado; acá va mes y año. Para el lector de
      // pantalla Cally ya anuncia el mes en su región aria-live, por eso aria-hidden.
      var heading = el("span", "gn-calendar__heading", { slot: "heading", "aria-hidden": "true" });
      cal.appendChild(heading);
      cal.addEventListener("focusday", function (e) { updateHeading(cal, e.detail); });
    }
    if (!cal.querySelector("calendar-month")) cal.appendChild(document.createElement("calendar-month"));
    updateHeading(cal);
    return cal;
  }
  var MONTH_FMT = window.Intl ? new Intl.DateTimeFormat("es-AR", { month: "long", year: "numeric", timeZone: "UTC" }) : null;
  function updateHeading(cal, date) {
    var heading = cal.querySelector(".gn-calendar__heading");
    if (!heading || !MONTH_FMT) return;
    if (!(date instanceof Date)) {
      var d = parseDate(cal.focusedDate || cal.getAttribute("focused-date") || cal.value || "") || today();
      date = new Date(Date.UTC(d.y, d.m - 1, d.d));
    }
    var text = MONTH_FMT.format(date);
    heading.textContent = text.charAt(0).toUpperCase() + text.slice(1);
  }
  function buildCalendar() { return fillCalendar(document.createElement("calendar-date")); }
  // Cally vuelve a dibujar el mes de forma asíncrona: se espera a que el día
  // enfocable sea el pedido (por su nombre accesible, "13 de noviembre") para no
  // enfocar un botón que todavía muestra el mes anterior.
  function focusCalendar(cal, d) {
    var month = cal.querySelector("calendar-month");
    var want = null;
    try {
      want = d && new Intl.DateTimeFormat(cal.getAttribute("locale") || "es-AR", { day: "numeric", month: "long", timeZone: "UTC" })
        .format(new Date(Date.UTC(d.y, d.m - 1, d.d)));
    } catch (e) { want = null; }
    var tries = 0;
    (function attempt() {
      var btn = month && month.shadowRoot && month.shadowRoot.querySelector("button[tabindex='0']");
      if (btn && (!want || btn.getAttribute("aria-label") === want)) { btn.focus(); return; }
      if (tries++ < 30) window.requestAnimationFrame(attempt);
      else if (btn) btn.focus();
    })();
  }

  // ------------------------------------------------------------ gn-time
  // Dos campos compactos HH : mm (role="spinbutton"): se escribe directo o se
  // ajusta con ↑/↓ (minutos de a `step`; Mayús+↑/↓ de a 1), Inicio/Fin. Formato
  // de 24 horas. Al completar la hora pasa solo a los minutos. Un valor vacío o
  // fuera de rango no se corrige solo: queda marcado con un mensaje (vinculado
  // con aria-describedby), no cambia el campo principal y «Listo» no cierra
  // hasta corregirlo.
  function buildTime(step, label) {
    var group = el("div", "gn-time", { role: "group", "aria-label": label || "Hora" });
    var state = { h: 0, mi: 0 };
    var parts = {};
    group.innerHTML = '<span class="gn-time__label" aria-hidden="true">Hora</span><span class="gn-time__fields"></span>';
    var fields = group.lastChild;
    var errorEl = el("span", "gn-field__error gn-time__error", { id: nextId("hora-error"), "aria-live": "polite" });
    errorEl.hidden = true;
    var invalid = {};
    var MSG = {
      h: { range: "La hora tiene que estar entre 00 y 23.", empty: "Completá la hora (00 a 23)." },
      mi: { range: "Los minutos tienen que estar entre 00 y 59.", empty: "Completá los minutos (00 a 59)." },
    };
    function showErrors() {
      var msg = invalid.h || invalid.mi || "";
      errorEl.hidden = !msg;
      errorEl.innerHTML = msg ? icon("i-alert") + "<span></span>" : "";
      if (msg) errorEl.lastChild.textContent = msg;
    }
    function setInvalid(part, kind) {
      invalid[part.key] = kind ? MSG[part.key][kind] : "";
      if (kind) {
        part.input.setAttribute("aria-invalid", "true");
        addToken(part.input, "aria-describedby", errorEl.id);
      } else {
        part.input.removeAttribute("aria-invalid");
        removeToken(part.input, "aria-describedby", errorEl.id);
      }
      showErrors();
    }

    function emit() { group.dispatchEvent(new Event("change", { bubbles: true })); }

    function makePart(key, max, name, unit) {
      var wrap = el("span", "gn-time__field");
      var input = el("input", "gn-time__input", {
        type: "text", inputmode: "numeric", autocomplete: "off", maxlength: "2", spellcheck: "false",
        role: "spinbutton", "aria-label": name, "aria-valuemin": "0", "aria-valuemax": String(max),
      });
      var steps = el("span", "gn-time__steps");
      steps.innerHTML =
        '<button type="button" tabindex="-1" class="gn-time__step" data-dir="1" aria-label="Subir ' + unit + '">' + icon("i-chevup") + "</button>" +
        '<button type="button" tabindex="-1" class="gn-time__step" data-dir="-1" aria-label="Bajar ' + unit + '">' + icon("i-chevdown") + "</button>";
      wrap.appendChild(input);
      wrap.appendChild(steps);
      var part = { key: key, max: max, input: input, unit: unit };
      parts[key] = part;

      // al entrar se selecciona todo, así lo que se escribe reemplaza el valor
      var justFocused = false;
      input.addEventListener("focus", function () { input.select(); justFocused = true; });
      input.addEventListener("mouseup", function (e) { if (justFocused) { e.preventDefault(); justFocused = false; } });
      input.addEventListener("keydown", function () { justFocused = false; });
      input.addEventListener("change", function (e) { e.stopPropagation(); }); // el grupo avisa al confirmar
      input.addEventListener("keydown", function (e) {
        var delta = 0;
        var unitStep = key === "mi" && !e.shiftKey ? step : 1;
        if (e.key === "ArrowUp") delta = unitStep;
        else if (e.key === "ArrowDown") delta = -unitStep;
        else if (e.key === "Home") { e.preventDefault(); commit(part, 0); return; }
        else if (e.key === "End") { e.preventDefault(); commit(part, max); return; }
        else if (e.key === ":" && key === "h") { e.preventDefault(); parts.mi.input.focus(); return; }
        else return;
        e.preventDefault();
        bump(part, delta);
      });
      input.addEventListener("input", function () {
        var digits = input.value.replace(/\D/g, "").slice(0, 2);
        if (digits !== input.value) input.value = digits;
        var n = digits === "" ? NaN : Number(digits);
        var bad = digits !== "" && n > max;
        setInvalid(part, bad ? "range" : "");
        if (bad || digits === "") return;
        // dos cifras, o una que ya no admite segunda (hora 3–9): se confirma
        if (digits.length === 2 || (key === "h" && n > 2)) {
          commit(part, n, true);
          if (key === "h") { parts.mi.input.focus(); parts.mi.input.select(); }
        }
      });
      input.addEventListener("blur", function () {
        var digits = input.value.replace(/\D/g, "");
        if (digits !== "" && Number(digits) <= max) commit(part, Number(digits));
        else setInvalid(part, digits === "" ? "empty" : "range"); // no se corrige solo
      });
      steps.addEventListener("pointerdown", function (e) { e.preventDefault(); }); // el foco queda en el campo
      steps.addEventListener("click", function (e) {
        var b = e.target.closest("button");
        if (!b) return;
        bump(part, Number(b.getAttribute("data-dir")) * (key === "mi" ? step : 1));
        input.focus();
      });
      return wrap;
    }

    function render(part, keepText) {
      var v = state[part.key];
      if (!keepText) part.input.value = pad(v);
      setInvalid(part, "");
      part.input.setAttribute("aria-valuenow", String(v));
      part.input.setAttribute("aria-valuetext", pad(v) + " " + (part.key === "h" ? (v === 1 ? "hora" : "horas") : (v === 1 ? "minuto" : "minutos")));
    }
    function commit(part, n, typing) {
      var changed = state[part.key] !== n;
      state[part.key] = n;
      render(part, typing && part.input.value.length < 2 && part.key !== "h");
      if (typing) part.input.value = pad(n);
      if (changed) emit();
    }
    function bump(part, delta) {
      var size = part.max + 1, v = state[part.key];
      if (part.key === "mi" && Math.abs(delta) > 1) v = delta > 0 ? Math.floor(v / delta) * delta : Math.ceil(v / -delta) * -delta;
      commit(part, ((v + delta) % size + size) % size);
      part.input.select();
    }

    fields.appendChild(makePart("h", 23, "Hora", "la hora"));
    fields.appendChild(el("span", "gn-time__sep", { "aria-hidden": "true" })).textContent = ":";
    fields.appendChild(makePart("mi", 59, "Minutos", "los minutos"));
    fields.appendChild(el("span", "gn-time__suffix", { "aria-hidden": "true" })).textContent = "hs";
    group.appendChild(errorEl);
    render(parts.h); render(parts.mi);

    return {
      el: group,
      valid: function () { return !invalid.h && !invalid.mi; },
      focusInvalid: function () { (invalid.h ? parts.h : parts.mi).input.focus(); },
      get: function () { return { h: state.h, mi: state.mi }; },
      set: function (t) { state.h = t.h; state.mi = t.mi; render(parts.h); render(parts.mi); },
      focus: function () { parts.h.input.focus(); },
    };
  }

  // ------------------------------------------------------------ selectores
  function readBound(kind, s) { var v = s ? kind.parse(s) : null; return v ? kind.iso(v) : ""; }

  function enhance(wrap) {
    if (wrap.__gnDatetime) return;
    var kindName = wrap.getAttribute("data-gn-datetime");
    var kind = KINDS[kindName];
    var input = wrap.querySelector("input");
    if (!kind || !input) return;
    if (kind.calendar && !(window.customElements && window.customElements.get("calendar-date"))) {
      // Cally todavía no cargó: se espera; si nunca carga, el input nativo sigue andando.
      if (window.customElements && !wrap.__gnWaiting) {
        wrap.__gnWaiting = true;
        window.customElements.whenDefined("calendar-date").then(function () { enhance(wrap); });
      }
      return;
    }
    wrap.__gnDatetime = true;

    var step = Math.max(1, Math.min(30, Number(wrap.getAttribute("data-gn-minute-step")) || 5));
    var label = wrap.getAttribute("data-gn-label") || kind.label;
    var invalidMsg = wrap.getAttribute("data-gn-invalid-message") || kind.invalid;
    var defaultTime = parseTime(wrap.getAttribute("data-gn-default-time") || "") || { h: 0, mi: 0 };
    var min = readBound(kind, input.getAttribute("min"));
    var max = readBound(kind, input.getAttribute("max"));
    var raw = wrap.getAttribute("data-gn-raw");
    var initial = kind.parse(input.value);

    input.type = "text";
    input.value = raw || (initial ? kind.fmt(initial) : "");
    ["min", "max", "step"].forEach(function (a) { input.removeAttribute(a); });
    if (!input.placeholder) input.placeholder = wrap.getAttribute("data-gn-display") || PLACEHOLDER[kindName];
    input.setAttribute("autocomplete", "off");
    input.setAttribute("spellcheck", "false");
    if (min) input.setAttribute("data-gn-min", min);
    if (max) input.setAttribute("data-gn-max", max);

    var hint = el("span", "gn-visually-hidden", { id: nextId("formato") });
    hint.textContent = "Formato: " + PLACEHOLDER[kindName].replace("HH:mm", "hora y minutos") + ".";
    wrap.appendChild(hint);
    addToken(input, "aria-describedby", hint.id);

    var panelId = nextId("picker");
    var btn = el("button", "gn-datetime__btn", {
      type: "button", "aria-label": label, "aria-haspopup": "dialog", "aria-expanded": "false", "aria-controls": panelId,
    });
    btn.innerHTML = icon(kind.icon);
    btn.disabled = input.disabled || input.readOnly;
    wrap.appendChild(btn);
    wrap.classList.add("is-enhanced");

    var error = el("span", "gn-field__error gn-datetime__error", { id: nextId("error"), "aria-live": "polite" });
    error.hidden = true;
    wrap.parentNode.insertBefore(error, wrap.nextSibling);
    var weMarkedInvalid = false;

    function setError(msg) {
      input.setCustomValidity(msg || "");
      if (msg) {
        error.innerHTML = icon("i-alert") + "<span></span>";
        error.lastChild.textContent = msg;
        error.hidden = false;
        addToken(input, "aria-describedby", error.id);
        if (input.getAttribute("aria-invalid") !== "true") { input.setAttribute("aria-invalid", "true"); weMarkedInvalid = true; }
      } else {
        error.hidden = true;
        error.textContent = "";
        removeToken(input, "aria-describedby", error.id);
        if (weMarkedInvalid) { input.removeAttribute("aria-invalid"); weMarkedInvalid = false; }
      }
    }

    // Valida y normaliza lo escrito: "5/11/26 9" → "05/11/2026 09:00".
    function validate() {
      var text = input.value.trim();
      if (!text) { setError(""); return true; }
      var v = kind.parse(text);
      if (!v) { setError(invalidMsg); return false; }
      var formatted = kind.fmt(v);
      if (formatted !== input.value) input.value = formatted;
      var iso = kind.iso(v);
      if (min && iso < min) { setError("Elegí " + kind.noun + " desde " + kind.fmt(kind.parse(min)) + "."); return false; }
      if (max && iso > max) { setError("Elegí " + kind.noun + " hasta " + kind.fmt(kind.parse(max)) + "."); return false; }
      setError("");
      return true;
    }
    input.addEventListener("change", validate);
    input.addEventListener("input", function () { if (!error.hidden && kind.parse(input.value)) setError(""); });
    var form = input.form;
    if (form) form.addEventListener("submit", function (e) {
      // un campo oculto (p. ej. una opción no elegida) no bloquea el envío, como en el navegador
      if (!input.getClientRects().length) return;
      if (!validate()) { e.preventDefault(); e.stopImmediatePropagation(); input.focus(); }
    }, true);

    function setValue(v, silent) {
      input.value = v ? kind.fmt(v) : "";
      validate();
      if (!silent) { fire(input, "input"); fire(input, "change"); }
    }

    var panel, cal, time, focusDay;
    function ensurePanel() {
      if (panel) return;
      panel = el("div", "gn-popover gn-datetime__panel", { id: panelId, role: "dialog", "aria-label": label });
      panel.hidden = true;
      if (kind.calendar) {
        cal = buildCalendar();
        panel.appendChild(cal);
        cal.addEventListener("change", function () {
          var d = parseDate(cal.value);
          if (!d) return;
          if (kind.time) {
            var prev = kind.parse(input.value);
            setValue({ date: d, time: prev ? prev.time : time.get() });
          } else {
            setValue({ date: d });
            closePopover(true);
          }
        });
      }
      if (kind.time) {
        time = buildTime(step, kindName === "time" ? label : "Hora y minutos");
        panel.appendChild(time.el);
        time.el.addEventListener("change", function () {
          if (kind.calendar) {
            var prev = kind.parse(input.value), d = prev ? prev.date : parseDate(cal.value) || today();
            setValue({ date: d, time: time.get() });
            cal.value = isoDate(d);
          } else {
            setValue({ time: time.get() });
          }
        });
      }
      var foot = el("div", "gn-popover__foot");
      var nowBtn = el("button", "gn-btn gn-btn--ghost gn-btn--sm", { type: "button" });
      nowBtn.textContent = kind.time ? "Ahora" : "Hoy";
      nowBtn.addEventListener("click", function () {
        var v = { date: today(), time: now(step) };
        if (cal) { cal.value = isoDate(v.date); cal.focusedDate = isoDate(v.date); updateHeading(cal); }
        if (time) time.set(v.time);
        setValue(v);
        if (!kind.time) closePopover(true);
      });
      var done = el("button", "gn-btn gn-btn--primary gn-btn--sm", { type: "button" });
      done.textContent = kind.time ? "Listo" : "Cerrar";
      done.addEventListener("click", function () {
        if (time && !time.valid()) { time.focusInvalid(); return; } // primero hay que corregir la hora
        closePopover(true);
      });
      foot.appendChild(nowBtn);
      foot.appendChild(done);
      panel.appendChild(foot);
      wrap.appendChild(panel);
    }

    function clampDate(d) {
      var iso = isoDate(d);
      if (min && iso < min.slice(0, 10)) return parseDate(min.slice(0, 10));
      if (max && iso > max.slice(0, 10)) return parseDate(max.slice(0, 10));
      return d;
    }

    function open() {
      if (btn.disabled) return;
      ensurePanel();
      var v = kind.parse(input.value);
      if (cal) {
        cal.value = v ? isoDate(v.date) : "";
        if (kindName !== "time") {
          if (min) cal.setAttribute("min", min.slice(0, 10)); else cal.removeAttribute("min");
          if (max) cal.setAttribute("max", max.slice(0, 10)); else cal.removeAttribute("max");
        }
        focusDay = v ? v.date : clampDate(today());
        cal.focusedDate = isoDate(focusDay); // propiedad: el atributo no cambia si se navegó
        updateHeading(cal);
      }
      if (time) time.set(v ? v.time : defaultTime);
      openPopover(panel, wrap, btn, { root: wrap });
      if (cal) focusCalendar(cal, focusDay); else time.focus();
    }

    btn.addEventListener("click", function () {
      if (current && current.panel === panel) closePopover(true); else open();
    });
    input.addEventListener("keydown", function (e) {
      if (e.altKey && e.key === "ArrowDown") { e.preventDefault(); open(); }
    });

    wrap.__gnApi = {
      value: function () { var t = input.value.trim(); if (!t) return ""; var v = kind.parse(t); return v ? kind.iso(v) : null; },
      setValue: function (iso, silent) { setValue(iso ? kind.parse(iso) : null, silent); },
      validate: validate,
      open: open,
      close: function () { if (current && current.panel === panel) closePopover(false); },
    };
  }

  function api(input) {
    var wrap = input && input.closest ? input.closest("[data-gn-datetime]") : null;
    return wrap && wrap.__gnApi;
  }

  function init(root) {
    root = root || document;
    initPopoverTriggers(root);
    Array.prototype.forEach.call(root.querySelectorAll("calendar-date[data-gn-calendar]"), fillCalendar);
    Array.prototype.forEach.call(root.querySelectorAll("[data-gn-datetime]"), enhance);
  }

  GN.initDateTime = init;
  GN.popover = { open: openPopover, close: closePopover, place: function () { if (current) place(current); } };
  GN.datetime = {
    init: init,
    parseDate: parseDate,
    parseTime: parseTime,
    parseDateTime: parseDateTime,
    // ISO del valor del campo ("" vacío, null si lo escrito no es válido)
    value: function (input) {
      var a = api(input);
      if (a) return a.value();
      return input.value; // sin mejorar (nativo): ya es ISO
    },
    setValue: function (input, iso, silent) {
      var a = api(input);
      if (a) a.setValue(iso, silent); else { input.value = iso || ""; if (!silent) { fire(input, "input"); fire(input, "change"); } }
    },
    validate: function (input) { var a = api(input); return a ? a.validate() : input.checkValidity(); },
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { init(document); });
  else init(document);
})(window, document);
