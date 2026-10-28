/*!
 * GENEOS UI · comportamiento de componentes
 * Sin dependencias. Convive con jQuery/Bootstrap porque solo usa atributos
 * data-gn-* y clases gn-*. Todo se inicializa solo al cargar la página;
 * para contenido agregado después: GN.init(contenedor).
 *
 * Basado en core/static/core/js/dashboard.js de GELECTRIC (sidebar,
 * buscador, tooltips, dropdowns, filtros, filas acordeón, gráficos).
 */
(function (window, document) {
  "use strict";

  var DESKTOP = window.matchMedia("(min-width: 861px)");
  var REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)");

  // ---------------------------------------------------------------- utils
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function store(key, value) {
    try {
      if (value === undefined) return window.localStorage.getItem(key);
      window.localStorage.setItem(key, value);
    } catch (e) { return null; }
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  // Sin mayúsculas ni tildes: "Facturación" == "facturacion".
  function normalize(s) {
    return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
  }
  function readJSON(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }
  function icon(id, cls) {
    return '<svg class="gn-icon' + (cls ? " " + cls : "") + '" aria-hidden="true"><use href="#' + id + '"/></svg>';
  }
  function focusables(root) {
    return $$('a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])', root)
      .filter(function (el) { return el.offsetParent !== null || el === document.activeElement; });
  }

  // ------------------------------------------------------------- tooltip
  var tip;
  function tooltipEl() {
    if (!tip) {
      tip = document.createElement("div");
      tip.className = "gn-tooltip";
      tip.setAttribute("role", "tooltip");
      tip.id = "gn-tooltip";
      document.body.appendChild(tip);
    }
    return tip;
  }
  function showTip(target, text, variant) {
    if (!text) return;
    var t = tooltipEl();
    t.textContent = text;
    t.className = "gn-tooltip" + (variant ? " gn-tooltip--" + variant : "");
    var r = target.getBoundingClientRect();
    t.classList.add("is-visible");
    var tw = t.offsetWidth, th = t.offsetHeight;
    var left, top;
    if (variant === "nav") {
      left = r.right + 10; top = r.top + r.height / 2 - th / 2;
    } else {
      left = r.left + r.width / 2 - tw / 2; top = r.top - th - 8;
      if (top < 8) top = r.bottom + 8;
    }
    left = Math.max(8, Math.min(left, window.innerWidth - tw - 8));
    t.style.left = left + "px";
    t.style.top = top + "px";
  }
  function hideTip() { if (tip) tip.classList.remove("is-visible"); }

  function initTooltips(root) {
    $$("[data-gn-tooltip]", root).forEach(function (el) {
      if (el.__gnTip) return; el.__gnTip = true;
      var text = el.getAttribute("data-gn-tooltip");
      if (!el.hasAttribute("aria-label") && !el.textContent.trim()) el.setAttribute("aria-label", text);
      el.addEventListener("mouseenter", function () { showTip(el, text); });
      el.addEventListener("focus", function () { showTip(el, text); });
      el.addEventListener("mouseleave", hideTip);
      el.addEventListener("blur", hideTip);
    });
  }

  // ------------------------------------------------------------- sidebar
  var PIN_KEY = "gn-sidebar-expanded";
  var LEGACY_PIN_KEY = "geletric-sidebar-pinned"; // GELECTRIC: "1" = expandido

  var SIDEBAR_SYNC = [];
  function initSidebars() { $$("[data-gn-sidebar]").forEach(initSidebar); }

  // Puede haber más de un sidebar en la página (el catálogo tiene uno por
  // producto); los botones de menú actúan solo sobre el que está visible.
  function initSidebar(sidebar) {
    if (!sidebar || sidebar.__gn) return;
    sidebar.__gn = true;
    var toggles = $$("[data-gn-sidebar-toggle]");
    var scrim = $("[data-gn-scrim]");
    var lastFocus = null;

    // estado expandido/contraído en escritorio, recordado entre páginas y por producto
    var key = sidebar.getAttribute("data-gn-storage-key") || PIN_KEY;
    var saved = store(key);
    if (saved === null && /gelectric$/.test(key)) {
      // GELECTRIC ya guardaba esta preferencia con otra clave: se respeta
      var legacy = store(LEGACY_PIN_KEY);
      if (legacy !== null) { saved = legacy === "1" ? "1" : "0"; store(key, saved); }
    }
    var defaultExpanded = sidebar.getAttribute("data-gn-default") !== "collapsed";
    setExpanded(saved === null ? defaultExpanded : saved === "1", false);

    function setExpanded(expanded, persist) {
      sidebar.classList.toggle("is-collapsed", !expanded);
      syncToggles();
      if (persist !== false) store(key, expanded ? "1" : "0");
    }
    function isHorizontal() { return DESKTOP.matches && getNav() === "horizontal"; }
    function isCollapsed() { return DESKTOP.matches && !isHorizontal() && sidebar.classList.contains("is-collapsed"); }
    function syncToggles() {
      if (sidebar.hidden) return;
      toggles.forEach(function (b) {
        if (DESKTOP.matches) {
          b.setAttribute("aria-expanded", sidebar.classList.contains("is-collapsed") ? "false" : "true");
          b.setAttribute("aria-label", sidebar.classList.contains("is-collapsed") ? "Expandir menú" : "Contraer menú");
        } else {
          b.setAttribute("aria-expanded", sidebar.classList.contains("is-open") ? "true" : "false");
          b.setAttribute("aria-label", "Abrir menú");
        }
      });
    }

    // cajón móvil
    function openDrawer() {
      lastFocus = document.activeElement;
      sidebar.classList.add("is-open");
      if (scrim) scrim.hidden = false;
      document.documentElement.style.overflow = "hidden";
      syncToggles();
      var first = $(".gn-sidebar__search-input", sidebar) || focusables(sidebar)[0];
      if (first) window.setTimeout(function () { first.focus(); }, 30);
    }
    function closeDrawer(restore) {
      if (!sidebar.classList.contains("is-open")) return;
      sidebar.classList.remove("is-open");
      if (scrim) scrim.hidden = true;
      document.documentElement.style.overflow = "";
      syncToggles();
      if (restore !== false && lastFocus) lastFocus.focus();
    }

    toggles.forEach(function (b) {
      b.setAttribute("aria-controls", sidebar.id || "gn-sidebar");
      b.addEventListener("click", function () {
        if (sidebar.hidden) return;
        if (DESKTOP.matches) setExpanded(sidebar.classList.contains("is-collapsed"));
        else if (sidebar.classList.contains("is-open")) closeDrawer();
        else openDrawer();
      });
    });
    if (scrim) scrim.addEventListener("click", function () { closeDrawer(); });
    sidebar.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !DESKTOP.matches) { closeDrawer(); return; }
      if (e.key === "Tab" && !DESKTOP.matches && sidebar.classList.contains("is-open")) {
        var f = focusables(sidebar); if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    DESKTOP.addEventListener("change", function () { closeDrawer(false); hideTip(); syncToggles(); applyLayout(); });

    // grupos con submenú
    $$("[data-gn-group-toggle]", sidebar).forEach(function (btn) {
      var sub = document.getElementById(btn.getAttribute("aria-controls"));
      btn.addEventListener("click", function () {
        if (isHorizontal()) {
          // barra horizontal: el submenú es un desplegable y se abre uno por vez
          var open = btn.getAttribute("aria-expanded") !== "true";
          closeGroups(btn);
          setGroup(btn, sub, open);
          if (open) placeDropdown(sub);
          hideTip();
          return;
        }
        if (isCollapsed()) {
          // contraído: el grupo no tiene dónde desplegarse, así que primero se expande el sidebar
          setExpanded(true);
          setGroup(btn, sub, true);
          hideTip();
          return;
        }
        setGroup(btn, sub, btn.getAttribute("aria-expanded") !== "true");
      });
    });
    function setGroup(btn, sub, open) {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      if (sub) sub.hidden = !open;
    }
    var groupToggles = $$("[data-gn-group-toggle]", sidebar);
    function closeGroups(except) {
      groupToggles.forEach(function (b) { if (b !== except) setGroup(b, document.getElementById(b.getAttribute("aria-controls")), false); });
    }
    // Al cambiar de disposición: en horizontal los desplegables arrancan cerrados;
    // en vertical vuelve a abrirse el grupo que contiene la página actual.
    function applyLayout() {
      hideTip();
      groupToggles.forEach(function (b) {
        var entry = b.closest(".gn-nav__entry");
        setGroup(b, document.getElementById(b.getAttribute("aria-controls")), !isHorizontal() && !!entry && entry.classList.contains("has-active"));
      });
      syncToggles();
    }
    document.addEventListener("gn:nav", applyLayout);

    // Barra horizontal en una sola fila: los módulos que no entran pasan al menú «Más»
    // (copias de sus enlaces; los originales solo se ocultan, así permisos, estado activo
    // y buscador siguen saliendo del mismo menú).
    var navList = $(".gn-nav", sidebar);
    var more = $("[data-gn-nav-more]", sidebar);
    var moreList = more && $(".gn-nav__more-list", more);
    function moreLink(a, text) {
      var li = document.createElement("li"), c = document.createElement("a");
      c.className = "gn-nav__subitem"; c.href = a.getAttribute("href") || "#"; c.textContent = text;
      if (a.getAttribute("aria-current")) c.setAttribute("aria-current", a.getAttribute("aria-current"));
      li.appendChild(c); return li;
    }
    function fitBar() {
      if (!more || !navList) return;
      var tops = $$(".gn-nav > .gn-nav__entry:not(.gn-nav__more)", sidebar);
      tops.forEach(function (e) { e.classList.remove("is-overflow"); });
      moreList.innerHTML = "";
      more.classList.remove("has-active");
      more.hidden = true;
      if (!isHorizontal() || sidebar.hidden || !navList.clientWidth) return;
      if (navList.scrollWidth <= navList.clientWidth + 1) return;
      more.hidden = false;
      for (var i = tops.length - 1; i > 0 && navList.scrollWidth > navList.clientWidth + 1; i--) tops[i].classList.add("is-overflow");
      tops.filter(function (e) { return e.classList.contains("is-overflow"); }).forEach(function (e) {
        var item = $(".gn-nav__item", e), label = $(".gn-nav__label", item);
        var text = label ? (label.__gnText || label.textContent).trim() : "";
        var subs = $$(".gn-nav__subitem", e);
        if (!subs.length) moreList.appendChild(moreLink(item, text));
        else {
          var h = document.createElement("li"); h.className = "gn-nav__more-heading"; h.textContent = text; moreList.appendChild(h);
          subs.forEach(function (sa) { moreList.appendChild(moreLink(sa, (sa.__gnText || sa.textContent).trim())); });
        }
        if (e.classList.contains("has-active") || item.getAttribute("aria-current")) more.classList.add("has-active");
      });
    }
    var fitFrame = 0;
    function scheduleFit() { cancelAnimationFrame(fitFrame); fitFrame = requestAnimationFrame(fitBar); }
    window.addEventListener("resize", scheduleFit);
    document.addEventListener("gn:nav", scheduleFit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(scheduleFit);
    SIDEBAR_SYNC.push(scheduleFit);

    // desplegables de la barra: dentro de la ventana, alineados a la derecha si no entran
    function placeDropdown(sub) {
      if (!sub) return;
      sub.classList.remove("is-end");
      sub.style.maxHeight = "";
      var r = sub.getBoundingClientRect();
      if (r.right > window.innerWidth - 8) sub.classList.add("is-end");
      sub.style.maxHeight = Math.max(160, window.innerHeight - sub.getBoundingClientRect().top - 12) + "px";
    }
    document.addEventListener("click", function (e) { if (isHorizontal() && !sidebar.contains(e.target)) closeGroups(); });
    sidebar.addEventListener("keydown", function (e) {
      if (!isHorizontal()) return;
      if (e.key === "Escape") {
        var open = groupToggles.filter(function (b) { return b.getAttribute("aria-expanded") === "true"; })[0];
        if (open) { closeGroups(); open.focus(); }
        return;
      }
      // flechas izquierda/derecha entre los ítems principales de la barra
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      var tops = $$(".gn-nav > .gn-nav__entry > .gn-nav__item", sidebar).filter(function (el) { return el.offsetParent !== null; });
      var cur = document.activeElement.closest(".gn-nav__entry");
      var i = tops.indexOf(cur ? $(".gn-nav__item", cur) : null);
      if (i === -1) return;
      e.preventDefault();
      closeGroups();
      tops[(i + (e.key === "ArrowRight" ? 1 : -1) + tops.length) % tops.length].focus();
    });

    // tooltips: con el sidebar contraído muestran el nombre del ítem; expandido,
    // solo cuando el nombre no entra y se ve cortado con "…" (p. ej. "Contabilidad y Finanzas")
    function truncated(label) { return !!label && label.scrollWidth > label.clientWidth + 1; }
    $$(".gn-nav__item, .gn-nav__subitem, .gn-sidebar__search-btn", sidebar).forEach(function (el) {
      var label = el.classList.contains("gn-nav__subitem") ? el : el.querySelector(".gn-nav__label");
      var text = label ? label.textContent.trim() : el.getAttribute("aria-label");
      function show() {
        if (isCollapsed() && !el.classList.contains("gn-nav__subitem")) showTip(el, text, "nav");
        else if (truncated(label)) showTip(el, text, "nav");
      }
      el.addEventListener("mouseenter", show);
      el.addEventListener("focus", show);
      el.addEventListener("mouseleave", hideTip);
      el.addEventListener("blur", hideTip);
      el.addEventListener("click", hideTip);
    });

    // botón de búsqueda visible con el sidebar contraído
    var searchBtn = $(".gn-sidebar__search-btn", sidebar);
    if (searchBtn) searchBtn.addEventListener("click", function () {
      setExpanded(true);
      var input = $(".gn-sidebar__search-input", sidebar);
      if (input) window.setTimeout(function () { input.focus(); }, 60);
    });

    // al navegar en móvil, cerrar el cajón
    $$("a.gn-nav__item, a.gn-nav__subitem", sidebar).forEach(function (a) {
      a.addEventListener("click", function () { if (!DESKTOP.matches) closeDrawer(false); });
    });

    // flechas arriba/abajo entre ítems visibles del menú
    var nav = $(".gn-sidebar__nav", sidebar);
    if (nav) nav.addEventListener("keydown", function (e) {
      if (["ArrowDown", "ArrowUp", "Home", "End"].indexOf(e.key) === -1) return;
      var items = $$(".gn-nav__item, .gn-nav__subitem", nav).filter(function (el) { return el.offsetParent !== null; });
      var i = items.indexOf(document.activeElement);
      if (i === -1) return;
      e.preventDefault();
      var next = e.key === "Home" ? 0 : e.key === "End" ? items.length - 1 : i + (e.key === "ArrowDown" ? 1 : -1);
      if (next < 0) { var q = $(".gn-sidebar__search-input", sidebar); if (q && q.offsetParent) { q.focus(); return; } next = 0; }
      items[Math.min(next, items.length - 1)].focus();
    });

    initSidebarSearch(sidebar, setGroup);
    if (isHorizontal()) applyLayout();
    fitBar();
    syncToggles();
    SIDEBAR_SYNC.push(syncToggles);

    if (!sidebar.hidden) window.GN.sidebar = { expand: function () { setExpanded(true); }, collapse: function () { setExpanded(false); }, open: openDrawer, close: closeDrawer };
  }

  // Buscador del sidebar: filtra módulos y submenús en el lugar, sin
  // recargar, sin distinguir mayúsculas ni tildes; abre los grupos que
  // tienen coincidencias y los vuelve a su estado al limpiar la búsqueda.
  function initSidebarSearch(sidebar, setGroup) {
    var input = $(".gn-sidebar__search-input", sidebar);
    var nav = $(".gn-sidebar__nav", sidebar);
    if (!input || !nav) return;
    var clear = $(".gn-sidebar__search-clear", sidebar);
    var empty = $(".gn-sidebar__empty", sidebar);
    var status = $(".gn-sidebar__status", sidebar);
    var foot = $(".gn-sidebar__foot", sidebar);
    var entries = $$(".gn-nav__entry:not(.gn-nav__more)", nav);
    var sections = $$(".gn-nav__section", nav);
    var initial = null;

    // guardo el texto original de cada etiqueta para poder resaltar y restaurar
    $$(".gn-nav__label, .gn-nav__subitem", nav).forEach(function (el) {
      el.__gnText = el.textContent.trim();
    });

    function haystack(textEl, keywordsEl) {
      return normalize((textEl.__gnText || textEl.textContent) + " " + ((keywordsEl || textEl).getAttribute("data-gn-keywords") || ""));
    }
    function paint(el, q) {
      var text = el.__gnText;
      if (!q) { el.textContent = text; return; }
      var n = normalize(text), i = n.indexOf(q);
      if (i === -1) { el.textContent = text; return; }
      // Al quitar las marcas de acento cada letra vuelve a ocupar un carácter,
      // así que las posiciones del texto normalizado coinciden con el original.
      el.innerHTML = escapeHtml(text.slice(0, i)) + "<mark>" + escapeHtml(text.slice(i, i + q.length)) + "</mark>" + escapeHtml(text.slice(i + q.length));
    }
    function snapshot() {
      return $$("[data-gn-group-toggle]", nav).map(function (b) { return [b, b.getAttribute("aria-expanded") === "true"]; });
    }

    function run() {
      var raw = input.value;
      var q = normalize(raw);
      if (clear) clear.hidden = !q;
      if (q && !initial) initial = snapshot();
      var words = q.split(/\s+/).filter(Boolean);
      function hit(hay) { return words.every(function (w) { return hay.indexOf(w) !== -1; }); }
      var total = 0;
      entries.forEach(function (entry) {
        var item = $(".gn-nav__item", entry);
        var label = item && $(".gn-nav__label", item);
        var subs = $$(".gn-nav__subitem", entry);
        if (!q) {
          entry.hidden = false;
          if (label) paint(label, "");
          subs.forEach(function (s) { s.parentElement.hidden = false; paint(s, ""); });
          return;
        }
        var selfMatch = !!(label && hit(haystack(label, item)));
        var subMatches = 0;
        subs.forEach(function (s) {
          var own = hit(haystack(s));
          // si coincide el grupo, se muestran todas sus opciones
          s.parentElement.hidden = !(own || selfMatch);
          paint(s, own ? words[0] : "");
          if (own) subMatches++;
        });
        var visible = selfMatch || subMatches > 0;
        entry.hidden = !visible;
        if (label) paint(label, selfMatch ? words[0] : "");
        var toggle = $("[data-gn-group-toggle]", entry);
        if (toggle && visible) setGroup(toggle, document.getElementById(toggle.getAttribute("aria-controls")), true);
        if (visible) total += Math.max(1, subMatches);
      });
      // los títulos de sección se ocultan si no queda nada debajo
      sections.forEach(function (sec) {
        var el = sec.nextElementSibling, any = false;
        while (el && !el.classList.contains("gn-nav__section")) { if (!el.hidden) any = true; el = el.nextElementSibling; }
        sec.hidden = q ? !any : false;
      });
      if (empty) {
        empty.hidden = !q || total > 0;
        empty.textContent = 'Sin resultados para "' + raw.trim() + '".';
      }
      if (foot) foot.hidden = !!q;
      if (status) status.textContent = q ? (total ? total + (total === 1 ? " resultado" : " resultados") : "Sin resultados") : "";
      if (!q && initial) {
        initial.forEach(function (pair) { setGroup(pair[0], document.getElementById(pair[0].getAttribute("aria-controls")), pair[1]); });
        initial = null;
      }
    }

    input.addEventListener("input", run);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && input.value) { e.stopPropagation(); input.value = ""; run(); }
      if (e.key === "ArrowDown" || e.key === "Enter") {
        var first = $$(".gn-nav__item, .gn-nav__subitem", nav).filter(function (el) { return el.offsetParent !== null; })[0];
        if (!first) return;
        e.preventDefault();
        if (e.key === "Enter" && input.value) {
          // Enter abre el primer resultado navegable
          var link = $$("a.gn-nav__subitem, a.gn-nav__item", nav).filter(function (el) { return el.offsetParent !== null; })[0];
          if (link) { link.click(); return; }
        }
        first.focus();
      }
    });
    if (clear) clear.addEventListener("click", function () { input.value = ""; run(); input.focus(); });
    // atajo "/" para ir al buscador del menú (como en GELECTRIC con ⌘K para el global)
    document.addEventListener("keydown", function (e) {
      if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
      var t = e.target; if (t && (t.isContentEditable || /INPUT|TEXTAREA|SELECT/.test(t.tagName))) return;
      if (!input.offsetParent) return;
      e.preventDefault(); input.focus();
    });
    run();
  }

  // ----------------------------------------------------------- dropdowns
  // <button data-gn-dropdown="id-del-menu" aria-expanded="false">…</button>
  // <div class="gn-dropdown__menu" id="id-del-menu" role="menu" hidden>…</div>
  var openMenu = null;
  function closeMenu(focusToggle) {
    if (!openMenu) return;
    openMenu.menu.hidden = true;
    openMenu.toggle.setAttribute("aria-expanded", "false");
    if (focusToggle) openMenu.toggle.focus();
    openMenu = null;
  }
  function menuItems(menu) {
    return $$('[role="menuitem"], .gn-dropdown__item', menu).filter(function (el) { return !el.hidden && !el.disabled; });
  }
  function initDropdowns(root) {
    $$("[data-gn-dropdown]", root).forEach(function (toggle) {
      if (toggle.__gn) return; toggle.__gn = true;
      var menu = document.getElementById(toggle.getAttribute("data-gn-dropdown"));
      if (!menu) return;
      toggle.setAttribute("aria-haspopup", menu.getAttribute("role") === "menu" ? "menu" : "true");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-controls", menu.id);
      toggle.addEventListener("click", function (e) {
        e.stopPropagation();
        var wasOpen = openMenu && openMenu.menu === menu;
        closeMenu();
        if (wasOpen) return;
        menu.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
        openMenu = { toggle: toggle, menu: menu };
        if (e.detail === 0) { var f = menuItems(menu)[0]; if (f) f.focus(); } // abierto con teclado
      });
      toggle.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown" && menu.hidden) { e.preventDefault(); toggle.click(); var f = menuItems(menu)[0]; if (f) f.focus(); }
      });
      menu.addEventListener("click", function (e) {
        e.stopPropagation();
        var item = e.target.closest(".gn-dropdown__item");
        if (item && !item.hasAttribute("data-gn-keep-open")) closeMenu(true);
      });
      menu.addEventListener("keydown", function (e) {
        var items = menuItems(menu), i = items.indexOf(document.activeElement);
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          var n = i + (e.key === "ArrowDown" ? 1 : -1);
          if (n < 0) n = items.length - 1; if (n >= items.length) n = 0;
          if (items[n]) items[n].focus();
        } else if (e.key === "Home" || e.key === "End") {
          e.preventDefault(); var t = items[e.key === "Home" ? 0 : items.length - 1]; if (t) t.focus();
        } else if (e.key === "Tab") { closeMenu(); }
      });
    });
  }
  document.addEventListener("click", function () { closeMenu(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && openMenu) closeMenu(true); });

  // --------------------------------------------------------------- tabs
  // <div class="gn-tabs" role="tablist"> <button role="tab" aria-controls="p1">…
  function initTabs(root) {
    $$('[role="tablist"].gn-tabs', root).forEach(function (list) {
      if (list.__gn) return; list.__gn = true;
      var tabs = $$('[role="tab"]', list);
      function select(tab, focus) {
        tabs.forEach(function (t) {
          var on = t === tab;
          t.setAttribute("aria-selected", on ? "true" : "false");
          t.tabIndex = on ? 0 : -1;
          var p = document.getElementById(t.getAttribute("aria-controls"));
          if (p) p.hidden = !on;
        });
        if (focus) tab.focus();
      }
      tabs.forEach(function (t, i) {
        t.addEventListener("click", function () { select(t); });
        t.addEventListener("keydown", function (e) {
          var n = null;
          if (e.key === "ArrowRight") n = (i + 1) % tabs.length;
          if (e.key === "ArrowLeft") n = (i - 1 + tabs.length) % tabs.length;
          if (e.key === "Home") n = 0;
          if (e.key === "End") n = tabs.length - 1;
          if (n !== null) { e.preventDefault(); select(tabs[n], true); }
        });
      });
      select(tabs.filter(function (t) { return t.getAttribute("aria-selected") === "true"; })[0] || tabs[0]);
    });
  }

  // ------------------------------------------------------------ filtros
  function initFilters(root) {
    // botón que muestra/oculta los filtros en móvil
    $$("[data-gn-filters-toggle]", root).forEach(function (btn) {
      if (btn.__gn) return; btn.__gn = true;
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      if (!panel) return;
      btn.addEventListener("click", function () {
        var open = btn.getAttribute("aria-expanded") !== "true";
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        panel.classList.toggle("is-open", open);
      });
    });
    // pills de filtro rápido (uno activo por grupo)
    $$("[data-gn-pills]", root).forEach(function (group) {
      if (group.__gn) return; group.__gn = true;
      group.addEventListener("click", function (e) {
        var b = e.target.closest(".gn-pill-toggle"); if (!b) return;
        $$(".gn-pill-toggle", group).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        group.dispatchEvent(new CustomEvent("gn:pill", { bubbles: true, detail: { value: b.value || b.getAttribute("data-value") } }));
      });
    });
    // filtros avanzados "+ Agregar filtro"
    $$("[data-gn-filter-builder]", root).forEach(function (builder) {
      if (builder.__gn) return; builder.__gn = true;
      var defs = readJSON(builder.getAttribute("data-gn-filter-builder")) || [];
      var byKey = {}; defs.forEach(function (f) { byKey[f.key] = f; });
      var row = $("[data-gn-filter-fields]", builder);
      var menu = $("[data-gn-filter-menu]", builder);
      var visibleInput = $("[data-gn-filter-visible]", builder);
      if (!row || !menu) return;
      function active() { return $$("[data-filter-key]", row).map(function (f) { return f.getAttribute("data-filter-key"); }); }
      function sync() {
        var keys = active();
        $$("[data-gn-add-filter]", menu).forEach(function (it) { it.hidden = keys.indexOf(it.getAttribute("data-gn-add-filter")) !== -1; });
        if (visibleInput) visibleInput.value = keys.join(",");
        builder.dispatchEvent(new CustomEvent("gn:filters", { bubbles: true, detail: { keys: keys } }));
      }
      function control(f) {
        var id = "gn-f-" + f.key;
        if (f.type === "text") return '<input type="search" id="' + id + '" name="' + f.key + '" class="gn-input" placeholder="' + escapeHtml(f.placeholder || f.label) + '">';
        if (f.type === "daterange") {
          return '<span class="gn-filter__range"><input type="date" id="' + id + '" name="' + f.params[0] + '" class="gn-input" aria-label="' + escapeHtml(f.label) + ' desde">' +
            '<span aria-hidden="true">–</span><input type="date" name="' + f.params[1] + '" class="gn-input" aria-label="' + escapeHtml(f.label) + ' hasta"></span>';
        }
        var o = '<option value="">Todos</option>';
        (f.options || []).forEach(function (x) { o += '<option value="' + escapeHtml(x.value) + '">' + escapeHtml(x.label) + "</option>"; });
        return '<select id="' + id + '" name="' + f.key + '" class="gn-select">' + o + "</select>";
      }
      function bind(field) {
        var b = $("[data-gn-remove-filter]", field);
        if (b) b.addEventListener("click", function () {
          var key = field.getAttribute("data-filter-key");
          field.remove(); sync();
          var toggle = $("[data-gn-dropdown]", builder); if (toggle) toggle.focus();
          announce("Filtro " + (byKey[key] ? byKey[key].label : "") + " quitado");
        });
      }
      function add(key) {
        var f = byKey[key]; if (!f) return;
        var el = document.createElement("div");
        el.className = "gn-filter"; el.setAttribute("data-filter-key", f.key);
        el.innerHTML = '<div class="gn-filter__head"><label class="gn-filter__label" for="gn-f-' + f.key + '">' + escapeHtml(f.label) + "</label>" +
          '<button type="button" class="gn-filter__remove" data-gn-remove-filter aria-label="Quitar filtro ' + escapeHtml(f.label) + '">' + icon("i-x") + "</button></div>" + control(f);
        row.appendChild(el); bind(el); sync();
        var c = $("input, select", el); if (c) c.focus();
      }
      $$(".gn-filter", row).forEach(bind);
      $$("[data-gn-add-filter]", menu).forEach(function (it) {
        it.addEventListener("click", function () { add(it.getAttribute("data-gn-add-filter")); });
      });
      sync();
    });
  }

  // -------------------------------------------------------------- tablas
  function initTables(root) {
    // filas acordeón en móvil
    $$(".gn-row-summary__btn", root).forEach(function (btn) {
      if (btn.__gn) return; btn.__gn = true;
      btn.addEventListener("click", function () {
        var tr = btn.closest("tr"); if (!tr) return;
        var open = !tr.classList.contains("is-open");
        tr.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
    // orden en el navegador para tablas chicas (data-gn-sort="client").
    // Las tablas grandes ordenan en el servidor con links (?o=campo).
    $$('table[data-gn-sort="client"]', root).forEach(function (table) {
      if (table.__gn) return; table.__gn = true;
      var ths = $$("thead th", table);
      ths.forEach(function (th, col) {
        var btn = $(".gn-table__sort", th); if (!btn) return;
        btn.addEventListener("click", function () {
          var dir = th.getAttribute("aria-sort") === "ascending" ? "descending" : "ascending";
          ths.forEach(function (o) { if (o !== th) o.removeAttribute("aria-sort"); });
          th.setAttribute("aria-sort", dir);
          var tbody = table.tBodies[0];
          var rows = Array.prototype.slice.call(tbody.rows);
          var type = th.getAttribute("data-gn-type") || "text";
          rows.sort(function (a, b) {
            // la celda de resumen del acordeón móvil no tiene encabezado
            var off = a.cells[0] && a.cells[0].classList.contains("gn-row-summary") ? 1 : 0;
            var x = a.cells[col + off], y = b.cells[col + off];
            var vx = x.getAttribute("data-value") || x.textContent.trim();
            var vy = y.getAttribute("data-value") || y.textContent.trim();
            var r = type === "number" ? parseFloat(vx) - parseFloat(vy) : vx.localeCompare(vy, "es", { sensitivity: "base", numeric: true });
            return dir === "ascending" ? r : -r;
          });
          rows.forEach(function (r) { tbody.appendChild(r); });
          announce("Ordenado por " + btn.textContent.trim() + (dir === "ascending" ? ", ascendente" : ", descendente"));
        });
      });
    });
  }

  // -------------------------------------------------------------- modales
  // <button data-gn-modal-open="id">  <dialog class="gn-modal" id="id">
  function initModals(root) {
    $$("[data-gn-modal-open]", root).forEach(function (btn) {
      if (btn.__gnModal) return; btn.__gnModal = true;
      btn.setAttribute("aria-haspopup", "dialog");
      btn.addEventListener("click", function () { openModal(btn.getAttribute("data-gn-modal-open"), btn); });
    });
    $$("dialog.gn-modal", root).forEach(function (dlg) {
      if (dlg.__gn) return; dlg.__gn = true;
      dlg.addEventListener("click", function (e) {
        if (e.target.closest("[data-gn-modal-close]")) { closeModal(dlg); return; }
        // clic en el fondo: el target es el propio <dialog>
        if (e.target === dlg && dlg.getAttribute("data-gn-dismissable") !== "false") closeModal(dlg);
      });
      dlg.addEventListener("close", function () {
        if (dlg.__gnOpener && document.contains(dlg.__gnOpener)) dlg.__gnOpener.focus();
      });
    });
  }
  function openModal(id, opener) {
    var dlg = typeof id === "string" ? document.getElementById(id) : id;
    if (!dlg) return;
    dlg.__gnOpener = opener || document.activeElement;
    if (typeof dlg.showModal === "function") dlg.showModal(); else dlg.setAttribute("open", "");
    var auto = $("[autofocus]", dlg) || $(".gn-modal__body input, .gn-modal__body select", dlg) || $(".gn-modal__foot .gn-btn", dlg);
    if (auto) auto.focus();
  }
  function closeModal(dlg, value) {
    if (typeof dlg === "string") dlg = document.getElementById(dlg);
    if (!dlg) return;
    if (typeof dlg.close === "function") dlg.close(value); else dlg.removeAttribute("open");
  }

  // --------------------------------------------- alertas y notificaciones
  var live;
  function announce(msg) {
    if (!live) {
      live = document.createElement("div");
      live.className = "gn-visually-hidden"; live.setAttribute("aria-live", "polite");
      document.body.appendChild(live);
    }
    live.textContent = ""; window.setTimeout(function () { live.textContent = msg; }, 40);
  }
  function initAlerts(root) {
    $$("[data-gn-dismiss]", root).forEach(function (btn) {
      if (btn.__gn) return; btn.__gn = true;
      btn.addEventListener("click", function () { var a = btn.closest(".gn-alert"); if (a) a.remove(); });
    });
  }
  var ICONS = { good: "i-check-circle", warning: "i-alert", critical: "i-x-circle", info: "i-info" };
  function toast(message, opts) {
    opts = opts || {};
    var kind = opts.kind || "info";
    var host = $(".gn-toasts");
    if (!host) {
      host = document.createElement("div");
      host.className = "gn-toasts"; host.setAttribute("role", "region"); host.setAttribute("aria-label", "Notificaciones");
      document.body.appendChild(host);
    }
    var el = document.createElement("div");
    el.className = "gn-toast gn-toast--" + kind;
    el.setAttribute("role", kind === "critical" ? "alert" : "status");
    el.innerHTML = icon(ICONS[kind] || ICONS.info) +
      '<div class="gn-toast__body">' + (opts.title ? '<b class="gn-toast__title">' + escapeHtml(opts.title) + "</b>" : "") + escapeHtml(message) + "</div>" +
      '<button type="button" class="gn-alert__close" aria-label="Cerrar notificación">' + icon("i-x") + "</button>";
    host.appendChild(el);
    function remove() {
      if (!el.isConnected) return;
      if (REDUCED.matches) { el.remove(); return; }
      el.classList.add("is-leaving"); window.setTimeout(function () { el.remove(); }, 200);
    }
    el.querySelector("button").addEventListener("click", remove);
    var ms = opts.duration === undefined ? 5000 : opts.duration;
    if (ms) {
      var timer = window.setTimeout(remove, ms);
      el.addEventListener("mouseenter", function () { window.clearTimeout(timer); });
      el.addEventListener("mouseleave", function () { timer = window.setTimeout(remove, 2500); });
    }
    return el;
  }
  function initToastTriggers(root) {
    $$("[data-gn-toast]", root).forEach(function (btn) {
      if (btn.__gnToast) return; btn.__gnToast = true;
      btn.addEventListener("click", function () {
        toast(btn.getAttribute("data-gn-toast"), { kind: btn.getAttribute("data-gn-toast-kind") || "info", title: btn.getAttribute("data-gn-toast-title") || "" });
      });
    });
    // mensajes de Django renderizados como <script type="application/json" id="gn-messages">
    var msgs = readJSON("gn-messages");
    if (msgs && msgs.length && !initToastTriggers.__done) {
      initToastTriggers.__done = true;
      msgs.forEach(function (m) { toast(m.message, { kind: m.kind }); });
    }
  }

  // --------------------------------------------------------- botones
  function setLoading(btn, loading, text) {
    if (!btn) return;
    if (loading) {
      btn.__gnHtml = btn.innerHTML;
      btn.classList.add("is-loading"); btn.setAttribute("aria-busy", "true"); btn.disabled = true;
      btn.innerHTML = icon("i-spinner") + "<span>" + escapeHtml(text || "Guardando…") + "</span>";
    } else {
      btn.classList.remove("is-loading"); btn.removeAttribute("aria-busy"); btn.disabled = false;
      if (btn.__gnHtml) btn.innerHTML = btn.__gnHtml;
    }
  }

  // ------------------------------------------------------------ gráficos
  // Línea: <div class="gn-chart" data-gn-chart="line" data-gn-source="id-json" data-gn-unit="MWh">
  // JSON: [{"label":"May","value":1200}, …]
  function lineChart(el) {
    var series = readJSON(el.getAttribute("data-gn-source")); if (!series || !series.length) return;
    var unit = el.getAttribute("data-gn-unit") || "";
    var title = el.getAttribute("data-gn-title") || "Gráfico de línea";
    var values = series.map(function (d) { return d.value; });
    var w = 640, h = 220, pl = 44, pr = 14, pt = 14, pb = 28;
    var lo = Math.min.apply(null, values), hi = Math.max.apply(null, values);
    var span = hi - lo || hi || 1;
    var step = Math.pow(10, Math.floor(Math.log10(span / 3)));
    [1, 2, 2.5, 5, 10].some(function (m) { if (span / (step * m) <= 4) { step *= m; return true; } return false; });
    var min = Math.floor(lo / step) * step, max = Math.ceil(hi / step) * step; if (max === min) max = min + step;
    var n = values.length;
    var x = function (i) { return pl + (w - pl - pr) * (n === 1 ? 0.5 : i / (n - 1)); };
    var y = function (v) { return pt + (h - pt - pb) * (1 - (v - min) / (max - min)); };
    var fmt = function (v) { return Number(v).toLocaleString("es-AR"); };
    var grid = "";
    for (var g = min; g <= max + 1e-9; g += step) {
      grid += '<line x1="' + pl + '" x2="' + (w - pr) + '" y1="' + y(g) + '" y2="' + y(g) + '" stroke="var(--gn-chart-grid)"/>' +
        '<text x="' + (pl - 8) + '" y="' + (y(g) + 4) + '" text-anchor="end" font-size="11" fill="var(--gn-chart-axis)">' + fmt(g) + "</text>";
    }
    var pts = values.map(function (v, i) { return x(i) + "," + y(v); }).join(" ");
    var gid = "gn-area-" + Math.random().toString(36).slice(2, 8);
    var area = "M" + x(0) + "," + (h - pb) + " L" + pts.split(" ").join(" L") + " L" + x(n - 1) + "," + (h - pb) + " Z";
    var labels = series.map(function (d, i) { return '<text x="' + x(i) + '" y="' + (h - 8) + '" text-anchor="middle" font-size="11" fill="var(--gn-chart-axis)">' + escapeHtml(d.label) + "</text>"; }).join("");
    var last = n - 1;
    el.innerHTML = '<svg viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + escapeHtml(title) + '">' + grid +
      '<defs><linearGradient id="' + gid + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--gn-chart-1)" stop-opacity=".22"/><stop offset="1" stop-color="var(--gn-chart-1)" stop-opacity="0"/></linearGradient></defs>' +
      '<path d="' + area + '" fill="url(#' + gid + ')"/>' +
      '<polyline points="' + pts + '" fill="none" stroke="var(--gn-chart-1)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>' +
      values.map(function (v, i) { return i === last ? "" : '<circle cx="' + x(i) + '" cy="' + y(v) + '" r="3" fill="var(--gn-surface)" stroke="var(--gn-chart-1)" stroke-width="2"/>'; }).join("") +
      '<circle cx="' + x(last) + '" cy="' + y(values[last]) + '" r="5.5" fill="var(--gn-chart-1)" stroke="var(--gn-surface)" stroke-width="2.5"/>' +
      labels + '<line class="gn-chart__hover" x1="0" x2="0" y1="' + pt + '" y2="' + (h - pb) + '" stroke="var(--gn-border-strong)" opacity="0"/></svg>' +
      '<div class="gn-chart__tip" aria-hidden="true"></div>' +
      '<table class="gn-visually-hidden"><caption>' + escapeHtml(title) + "</caption>" + series.map(function (d) { return "<tr><th>" + escapeHtml(d.label) + "</th><td>" + fmt(d.value) + " " + escapeHtml(unit) + "</td></tr>"; }).join("") + "</table>";
    var svg = el.querySelector("svg"), tipEl = el.querySelector(".gn-chart__tip"), hover = el.querySelector(".gn-chart__hover");
    svg.addEventListener("mousemove", function (e) {
      var r = svg.getBoundingClientRect(), s = r.width / w;
      var i = Math.round((((e.clientX - r.left) / s) - pl) / ((w - pl - pr) / Math.max(1, n - 1)));
      i = Math.max(0, Math.min(n - 1, i));
      hover.setAttribute("x1", x(i)); hover.setAttribute("x2", x(i)); hover.setAttribute("opacity", 1);
      tipEl.style.left = x(i) * s + "px"; tipEl.style.top = y(values[i]) * s + "px"; tipEl.style.opacity = 1;
      tipEl.innerHTML = escapeHtml(series[i].label) + " · <b>" + fmt(values[i]) + " " + escapeHtml(unit) + "</b>";
    });
    svg.addEventListener("mouseleave", function () { tipEl.style.opacity = 0; hover.setAttribute("opacity", 0); });
  }
  // Dona: data-gn-chart="donut" data-gn-source="id" ; JSON: [{"label":"Al día","value":72}, …]
  function donutChart(el) {
    var segs = readJSON(el.getAttribute("data-gn-source")); if (!segs || !segs.length) return;
    var total = segs.reduce(function (a, s) { return a + s.value; }, 0) || 1;
    var r = 46, c = 60, sw = 15, circ = 2 * Math.PI * r, off = 0;
    var colors = ["var(--gn-chart-1)", "var(--gn-chart-2)", "var(--gn-chart-3)", "var(--gn-chart-4)", "var(--gn-chart-5)"];
    var arcs = segs.map(function (s, i) {
      var f = s.value / total, len = Math.max(0, f * circ - 2);
      var a = '<circle cx="' + c + '" cy="' + c + '" r="' + r + '" fill="none" stroke="' + (s.color || colors[i % colors.length]) + '" stroke-width="' + sw + '" stroke-dasharray="' + len + " " + circ + '" stroke-dashoffset="' + -off + '" transform="rotate(-90 ' + c + " " + c + ')"/>';
      off += f * circ; return a;
    }).join("");
    var pct = Math.round(segs[0].value / total * 100);
    var center = el.getAttribute("data-gn-center") || segs[0].label;
    el.innerHTML = '<svg viewBox="0 0 120 120" role="img" aria-label="' + escapeHtml(center + ": " + pct + "%") + '"><circle cx="' + c + '" cy="' + c + '" r="' + r + '" fill="none" stroke="var(--gn-surface-2)" stroke-width="' + sw + '"/>' + arcs +
      '<text x="60" y="60" text-anchor="middle" font-size="22" font-weight="700" fill="var(--gn-text)">' + pct + "%</text>" +
      '<text x="60" y="75" text-anchor="middle" font-size="8.5" letter-spacing=".06em" fill="var(--gn-text-muted)">' + escapeHtml(center.toUpperCase()) + "</text></svg>" +
      '<ul class="gn-donut__legend">' + segs.map(function (s, i) {
        return '<li><i style="background:' + (s.color || colors[i % colors.length]) + '"></i>' + escapeHtml(s.label) + "<b>" + Number(s.value).toLocaleString("es-AR") + "</b></li>";
      }).join("") + "</ul>";
  }
  function initCharts(root) {
    $$("[data-gn-chart]", root).forEach(function (el) {
      var t = el.getAttribute("data-gn-chart");
      if (t === "line") lineChart(el);
      if (t === "donut") donutChart(el);
    });
  }

  // --------------------------------------------------------- modo de color
  // Claro por defecto. La elección se guarda en localStorage ("gn-theme") y
  // se aplica con data-gn-theme en <html>. {% gn_theme_boot %} la aplica en
  // el <head>, antes de pintar, para que no haya parpadeo.
  var THEME_KEY = "gn-theme";
  function getTheme() {
    return document.documentElement.getAttribute("data-gn-theme") === "dark" ? "dark" : "light";
  }
  function syncThemeSwitches() {
    var t = getTheme();
    $$("[data-gn-theme-switch]").forEach(function (group) {
      $$("[data-gn-theme-value]", group).forEach(function (b) {
        var on = b.getAttribute("data-gn-theme-value") === t;
        b.setAttribute("aria-checked", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
      });
    });
  }
  function setTheme(theme, persist) {
    var t = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-gn-theme", t);
    if (persist !== false) store(THEME_KEY, t);
    syncThemeSwitches();
    document.dispatchEvent(new CustomEvent("gn:theme", { detail: { theme: t } }));
    return t;
  }
  function initTheme(root) {
    if (!initTheme.__done) {
      initTheme.__done = true;
      var saved = store(THEME_KEY);
      setTheme(saved === "dark" ? "dark" : "light", false);
    }
    $$("[data-gn-theme-switch]", root).forEach(function (group) {
      if (group.__gn) return; group.__gn = true;
      var buttons = $$("[data-gn-theme-value]", group);
      buttons.forEach(function (b, i) {
        b.addEventListener("click", function () {
          var t = setTheme(b.getAttribute("data-gn-theme-value"));
          announce(t === "dark" ? "Modo oscuro activado" : "Modo claro activado");
        });
        b.addEventListener("keydown", function (e) {
          var d = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
          if (!d) return;
          e.preventDefault();
          var n = buttons[(i + d + buttons.length) % buttons.length];
          n.focus(); n.click();
        });
      });
    });
    syncThemeSwitches();
  }

  // ------------------------------------------------- disposición del menú
  // Misma lógica que el modo de color: data-gn-nav en <html> ("vertical" u
  // "horizontal"), elección guardada en localStorage ("gn-nav") y aplicada en
  // el <head> por {% gn_nav_boot %}. Sin elección guardada se usa el valor del
  // producto (data-gn-nav-default). Es independiente del tema y del producto.
  // En pantallas chicas siempre se usa el menú lateral desplegable.
  var NAV_KEY = "gn-nav";
  function getNav() {
    return document.documentElement.getAttribute("data-gn-nav") === "horizontal" ? "horizontal" : "vertical";
  }
  function navDefault() {
    return document.documentElement.getAttribute("data-gn-nav-default") === "horizontal" ? "horizontal" : "vertical";
  }
  function syncNavSwitches() {
    var n = getNav();
    $$("[data-gn-nav-switch]").forEach(function (group) {
      $$("[data-gn-nav-value]", group).forEach(function (b) {
        var on = b.getAttribute("data-gn-nav-value") === n;
        b.setAttribute("aria-checked", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
      });
    });
  }
  function setNav(layout, persist) {
    var n = layout === "horizontal" ? "horizontal" : "vertical";
    var changed = n !== getNav();
    document.documentElement.setAttribute("data-gn-nav", n);
    if (persist !== false) store(NAV_KEY, n);
    syncNavSwitches();
    if (changed || persist !== false) document.dispatchEvent(new CustomEvent("gn:nav", { detail: { layout: n } }));
    return n;
  }
  // Cambia el valor por defecto (p. ej. al cambiar de producto en el catálogo) y lo aplica si el usuario no eligió.
  function setNavDefault(layout) {
    document.documentElement.setAttribute("data-gn-nav-default", layout === "horizontal" ? "horizontal" : "vertical");
    var saved = store(NAV_KEY);
    if (saved !== "vertical" && saved !== "horizontal") setNav(navDefault(), false);
  }
  function initNav(root) {
    if (!initNav.__done) {
      initNav.__done = true;
      var saved = store(NAV_KEY);
      setNav(saved === "vertical" || saved === "horizontal" ? saved : navDefault(), false);
    }
    $$("[data-gn-nav-switch]", root).forEach(function (group) {
      if (group.__gn) return; group.__gn = true;
      var buttons = $$("[data-gn-nav-value]", group);
      buttons.forEach(function (b, i) {
        b.addEventListener("click", function () {
          var n = setNav(b.getAttribute("data-gn-nav-value"));
          announce(n === "horizontal" ? "Menú horizontal" : "Menú vertical");
        });
        b.addEventListener("keydown", function (e) {
          var d = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
          if (!d) return;
          e.preventDefault();
          var nb = buttons[(i + d + buttons.length) % buttons.length];
          nb.focus(); nb.click();
        });
      });
    });
    syncNavSwitches();
  }

  // ---------------------------------------------------------------- init
  function init(root) {
    initTheme(root);
    initNav(root);
    initTooltips(root);
    initDropdowns(root);
    initTabs(root);
    initFilters(root);
    initTables(root);
    initModals(root);
    initAlerts(root);
    initToastTriggers(root);
    initCharts(root);
  }

  window.GN = window.GN || {};
  window.GN.version = "0.2.0";
  window.GN.init = init;
  window.GN.toast = toast;
  window.GN.announce = announce;
  window.GN.openModal = openModal;
  window.GN.closeModal = closeModal;
  window.GN.setLoading = setLoading;
  window.GN.renderCharts = initCharts;
  window.GN.syncSidebars = function () { SIDEBAR_SYNC.forEach(function (f) { f(); }); };
  window.GN.normalize = normalize;
  window.GN.setTheme = setTheme;
  window.GN.getTheme = getTheme;
  window.GN.setNav = setNav;
  window.GN.getNav = getNav;
  window.GN.setNavDefault = setNavDefault;

  function boot() { initSidebars(); init(document); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})(window, document);
