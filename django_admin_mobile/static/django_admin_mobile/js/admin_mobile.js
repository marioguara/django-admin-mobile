/* =========================================================================
 * django-admin-mobile
 * Costruisce sopra l'admin di Django la struttura di una normale app per
 * telefono: barra in alto con titolo e tasto indietro, barra di navigazione
 * in basso, menu laterale con ricerca, pannello dei filtri che sale dal
 * basso, elenchi a schede e bottone flottante per aggiungere.
 *
 * Il menu arriva dal server dentro <script id="dam-config">: qui non si
 * indovina niente sull'applicazione ospite.
 *
 * Gli spostamenti di nodi nel DOM sono reversibili: ogni nodo spostato
 * lascia un segnaposto e torna al suo posto se si passa al desktop, così
 * ruotare il telefono o allargare la finestra non rompe la pagina.
 * ========================================================================= */
(function () {
    "use strict";

    if (window.__damShell) { return; }
    window.__damShell = true;

    // ── Configurazione ───────────────────────────────────────────────────
    var CFG = null;
    try {
        var cfgEl = document.getElementById("dam-config");
        if (cfgEl) { CFG = JSON.parse(cfgEl.textContent || cfgEl.innerText || "null"); }
    } catch (err) {
        CFG = null;
    }
    if (!CFG) { return; }

    var F = CFG.features || {};
    var L = CFG.labels || {};
    var U = CFG.urls || {};
    var BREAKPOINT = parseInt(CFG.breakpoint, 10) || 1024;
    var mq = window.matchMedia("(max-width: " + BREAKPOINT + "px)");

    if (/^#[0-9a-fA-F]{3,8}$/.test(CFG.accent || "")) {
        document.documentElement.style.setProperty("--dam-accent", CFG.accent);
    }

    // ── Utilità ──────────────────────────────────────────────────────────
    function el(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) { node.className = cls; }
        if (text !== undefined && text !== null) { node.textContent = text; }
        return node;
    }

    function each(list, fn) { Array.prototype.forEach.call(list || [], fn); }

    function closest(node, selector) {
        while (node && node.nodeType === 1) {
            if (node.matches && node.matches(selector)) { return node; }
            node = node.parentNode;
        }
        return null;
    }

    /** Sposta un nodo lasciando un segnaposto per poterlo rimettere a posto. */
    function park(node, parent) {
        if (!node || !parent || node.damHome) { return; }
        var mark = document.createComment("dam");
        if (node.parentNode) { node.parentNode.insertBefore(mark, node); }
        node.damHome = mark;
        parent.appendChild(node);
    }

    function unpark(node) {
        if (!node || !node.damHome) { return; }
        var mark = node.damHome;
        if (mark.parentNode) {
            mark.parentNode.insertBefore(node, mark);
            mark.parentNode.removeChild(mark);
        }
        node.damHome = null;
    }

    function cookie(name) {
        var parts = ("; " + document.cookie).split("; " + name + "=");
        return parts.length === 2 ? parts.pop().split(";").shift() : "";
    }

    /** Di tutte le voci, quella il cui indirizzo è il prefisso più lungo. */
    function bestMatch(entries, getUrl) {
        var path = window.location.pathname;
        var best = null;
        var bestLen = -1;
        each(entries, function (entry) {
            var url = getUrl(entry);
            if (!url || url === "#") { return; }
            if (path.indexOf(url) === 0 && url.length > bestLen) {
                best = entry;
                bestLen = url.length;
            }
        });
        return best;
    }

    function allItems() {
        var items = [];
        each(CFG.groups, function (group) {
            each(group.items, function (item) { items.push(item); });
        });
        return items;
    }

    var ITEMS = allItems();
    var CURRENT = bestMatch(ITEMS, function (i) { return i.url; });

    // ── Tipo di pagina ───────────────────────────────────────────────────
    function pageKind() {
        var body = document.body;
        if (body.classList.contains("popup") || window.name.indexOf("popup") === 0) { return "popup"; }
        if (body.classList.contains("login") || document.getElementById("login-form")) { return "login"; }
        if (document.getElementById("changelist")) { return "changelist"; }
        if (window.location.pathname === U.home) { return "index"; }
        if (body.classList.contains("dashboard")) { return "index"; }
        if (document.querySelector(".submit-row")) { return "form"; }
        return "other";
    }

    var KIND = pageKind();
    if (KIND === "popup") { return; }

    // ── Titolo della barra in alto ───────────────────────────────────────
    function pageTitle() {
        if (KIND === "index") { return CFG.title || "Admin"; }
        // Negli elenchi il titolo di Django ("Scegli X da modificare") è
        // troppo lungo per una barra: si usa il nome della sezione.
        if (KIND === "changelist" && CURRENT) { return CURRENT.label; }
        var h1 = document.querySelector("#content > h1, #content h1");
        if (h1 && h1.textContent.trim()) { return h1.textContent.trim(); }
        if (CURRENT) { return CURRENT.label; }
        return (document.title || "").split("|")[0].trim() || CFG.title || "Admin";
    }

    /** Indirizzo del livello superiore, letto dalle briciole di pane. */
    function backHref() {
        var links = document.querySelectorAll(".breadcrumbs a");
        if (links.length >= 2) { return links[links.length - 1].href; }
        if (links.length === 1 && KIND !== "index") { return links[0].href; }
        return null;
    }

    // ── Pannelli: apertura, chiusura, tasto Esc ──────────────────────────
    var openPanel = null;
    var lastFocus = null;

    function closePanel() {
        if (!openPanel) { return; }
        openPanel.classList.remove("dam-open");
        if (S.scrim) { S.scrim.classList.remove("dam-open"); }
        document.body.classList.remove("dam-locked");
        openPanel = null;
        if (lastFocus && lastFocus.focus) { lastFocus.focus(); }
        lastFocus = null;
    }

    function showPanel(panel, focusTarget) {
        if (!panel) { return; }
        if (openPanel && openPanel !== panel) { closePanel(); }
        lastFocus = document.activeElement;
        panel.classList.add("dam-open");
        if (S.scrim) { S.scrim.classList.add("dam-open"); }
        document.body.classList.add("dam-locked");
        openPanel = panel;
        if (focusTarget && focusTarget.focus) {
            window.setTimeout(function () { focusTarget.focus(); }, 60);
        }
    }

    // ── Installazione come app ───────────────────────────────────────────
    var PWA = CFG.pwa || null;
    var installEvent = null;     // evento "beforeinstallprompt" messo da parte

    function store(key, value) {
        try {
            if (value === undefined) { return window.localStorage.getItem(key); }
            window.localStorage.setItem(key, value);
        } catch (err) { /* spazio negato: si prosegue senza ricordare */ }
        return null;
    }

    function isStandalone() {
        return window.matchMedia("(display-mode: standalone)").matches ||
            window.navigator.standalone === true;
    }

    function isIos() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    }

    /** Installabile davvero, oppure installabile a mano come su iPhone. */
    function installable() {
        if (!PWA || isStandalone()) { return false; }
        return !!installEvent || isIos();
    }

    function registerServiceWorker() {
        if (!PWA || !PWA.sw_url || !("serviceWorker" in navigator)) { return; }
        navigator.serviceWorker.register(PWA.sw_url, { scope: PWA.scope })
            .catch(function () {
                // Senza service worker l'admin funziona identico: non si
                // installa e basta. Non vale la pena disturbare l'utente.
            });
    }

    function iosHelp() {
        if (!S.installSheet) {
            S.installSheet = buildSheet(L.installTitle || "Installa");
            var text = el("p", "dam-sheet-hint", L.installIos || "");
            S.installSheet.damBody.appendChild(text);
        }
        showPanel(S.installSheet);
    }

    function install() {
        if (installEvent) {
            installEvent.prompt();
            installEvent.userChoice.then(function () {
                installEvent = null;
                hideInstallBanner();
            });
            return;
        }
        if (isIos()) { iosHelp(); }
    }

    function hideInstallBanner() {
        if (S.installBanner) { S.installBanner.hidden = true; }
        document.body.classList.remove("dam-install-open");
        document.documentElement.style.removeProperty("--dam-install-h");
    }

    function showInstallBanner() {
        if (!PWA || !PWA.prompt || !installable()) { return; }
        if (store("dam-install-dismissed") === "1") { return; }
        if (!document.body.classList.contains("dam-mobile")) { return; }

        if (!S.installBanner) {
            var banner = el("div", "dam-install");
            var body = el("div", "dam-install-text");
            body.appendChild(el("strong", null, L.installTitle || "Installa"));
            body.appendChild(el("span", null, L.installBody || ""));
            banner.appendChild(body);

            var actions = el("div", "dam-install-actions");
            var yes = el("button", "dam-install-yes", L.installNow || "Installa");
            yes.type = "button";
            yes.addEventListener("click", install);
            var no = el("button", "dam-install-no", L.later || "Non ora");
            no.type = "button";
            no.addEventListener("click", function () {
                store("dam-install-dismissed", "1");
                hideInstallBanner();
            });
            actions.appendChild(yes);
            actions.appendChild(no);
            banner.appendChild(actions);

            document.body.appendChild(banner);
            S.installBanner = banner;
        }
        S.installBanner.hidden = false;
        document.body.classList.add("dam-install-open");
        syncInstallBanner();
    }

    /* Anche l'invito occupa spazio vero in fondo: va misurato, altrimenti
     * copre il bottone flottante e l'ultima riga del contenuto. */
    function syncInstallBanner() {
        var banner = S.installBanner;
        if (!banner || banner.hidden) {
            document.documentElement.style.removeProperty("--dam-install-h");
            document.body.classList.remove("dam-install-open");
            return;
        }
        document.documentElement.style.setProperty(
            "--dam-install-h", banner.offsetHeight + "px"
        );
    }

    window.addEventListener("beforeinstallprompt", function (event) {
        // Senza preventDefault Chrome mostra il suo invito, che sul telefono
        // finisce sopra la barra di navigazione.
        event.preventDefault();
        installEvent = event;
        showInstallBanner();
        if (S.installLink) { S.installLink.hidden = false; }
    });

    window.addEventListener("appinstalled", function () {
        installEvent = null;
        store("dam-install-dismissed", "1");
        hideInstallBanner();
        if (S.installLink) { S.installLink.hidden = true; }
    });

    // ── Costruzione della shell ──────────────────────────────────────────
    var S = {};   // elementi della shell

    function buildScrim() {
        var scrim = el("div", "dam-scrim");
        scrim.addEventListener("click", closePanel);
        document.body.appendChild(scrim);
        return scrim;
    }

    function buildAppbar() {
        var bar = el("header", "dam-appbar");
        bar.setAttribute("role", "banner");

        var lead = el("button", "dam-appbar-btn dam-appbar-lead");
        lead.type = "button";
        var back = backHref();
        // Le pagine raggiungibili dalla barra in basso sono destinazioni di
        // primo livello: lì il tasto a sinistra apre il menu, non torna indietro.
        var isTopLevel = KIND === "index" || KIND === "changelist" ||
            (CFG.tabs || []).some(function (tab) {
                return tab.url === window.location.pathname;
            });
        var canGoBack = !isTopLevel;
        if (canGoBack && (back || window.history.length > 1)) {
            lead.textContent = "←";
            lead.setAttribute("aria-label", L.back || "Indietro");
            lead.addEventListener("click", function () {
                if (back) { window.location.href = back; }
                else { window.history.back(); }
            });
        } else {
            lead.textContent = "☰";
            lead.setAttribute("aria-label", L.menu || "Menu");
            lead.addEventListener("click", function () { showPanel(S.drawer, S.drawerSearch); });
            if (!F.drawer) { lead.hidden = true; }
        }
        bar.appendChild(lead);

        var title = el("h1", "dam-appbar-title", pageTitle());
        bar.appendChild(title);

        if (F.drawer) {
            var search = el("button", "dam-appbar-btn dam-appbar-action", "🔍");
            search.type = "button";
            search.setAttribute("aria-label", L.searchMenu || "Cerca");
            search.addEventListener("click", function () { showPanel(S.drawer, S.drawerSearch); });
            bar.appendChild(search);
        }

        document.body.insertBefore(bar, document.body.firstChild);
        return bar;
    }

    function buildTabbar() {
        var tabs = CFG.tabs || [];
        var nav = el("nav", "dam-tabbar");
        nav.setAttribute("aria-label", L.menu || "Menu");

        var active = bestMatch(tabs, function (t) { return t.exact ? null : t.match || t.url; });
        var path = window.location.pathname;

        each(tabs, function (tab) {
            var link = el("a", "dam-tab");
            link.href = tab.url;
            var isActive = tab.exact ? path === tab.url : tab === active;
            if (tab.exact && path === tab.url) { isActive = true; }
            if (isActive) { link.classList.add("dam-active"); }
            link.appendChild(el("span", "dam-tab-icon", tab.icon || "•"));
            link.appendChild(el("span", "dam-tab-label", tab.label || ""));
            nav.appendChild(link);
        });

        if (F.drawer) {
            var menu = el("button", "dam-tab dam-tab-menu");
            menu.type = "button";
            menu.appendChild(el("span", "dam-tab-icon", "☰"));
            menu.appendChild(el("span", "dam-tab-label", L.menu || "Menu"));
            menu.addEventListener("click", function () { showPanel(S.drawer, S.drawerSearch); });
            nav.appendChild(menu);
        }

        if (!nav.children.length) { return null; }
        document.body.appendChild(nav);
        return nav;
    }

    function buildDrawerLink(item) {
        var row = el("div", "dam-row");
        var link = el("a", "dam-link");
        link.href = item.url;
        link.appendChild(el("span", "dam-link-icon", item.icon || "•"));
        link.appendChild(el("span", "dam-link-label", item.label));
        if (CURRENT && CURRENT.url === item.url) { link.classList.add("dam-active"); }
        if (item.add_url) {
            var add = el("a", "dam-link-add", "+");
            add.href = item.add_url;
            add.title = L.add || "Aggiungi";
            add.setAttribute("aria-label", (L.add || "Aggiungi") + " — " + item.label);
            link.appendChild(add);
        }
        row.appendChild(link);
        row.damLabel = (item.label || "").toLowerCase();
        return row;
    }

    function buildThemeRow() {
        var row = el("div", "dam-theme-row");
        row.appendChild(el("span", "dam-link-icon", "🎨"));
        row.appendChild(el("span", null, L.theme || "Tema"));
        var group = el("span", "dam-theme-btns");
        var modes = [["auto", "◑"], ["light", "☀"], ["dark", "☾"]];
        var current = "auto";
        try { current = window.localStorage.getItem("theme") || "auto"; } catch (e) { /* storage negato */ }

        each(modes, function (mode) {
            var btn = el("button", "dam-theme-btn", mode[1]);
            btn.type = "button";
            btn.setAttribute("aria-label", mode[0]);
            if (mode[0] === current) { btn.classList.add("dam-active"); }
            btn.addEventListener("click", function () {
                // Stesse chiavi usate da theme.js di Django: i due sistemi
                // restano allineati e il tema sopravvive al cambio pagina.
                document.documentElement.dataset.theme = mode[0];
                try { window.localStorage.setItem("theme", mode[0]); } catch (e) { /* storage negato */ }
                each(group.children, function (other) { other.classList.remove("dam-active"); });
                btn.classList.add("dam-active");
            });
            group.appendChild(btn);
        });
        row.appendChild(group);
        return row;
    }

    function buildLogout() {
        var existing = document.getElementById("logout-form");
        if (existing) {
            var btn = el("button", "dam-link dam-logout");
            btn.type = "button";
            btn.appendChild(el("span", "dam-link-icon", "🚪"));
            btn.appendChild(el("span", "dam-link-label", L.logout || "Esci"));
            btn.addEventListener("click", function () { existing.submit(); });
            return btn;
        }
        if (!U.logout) { return null; }
        var form = el("form");
        form.method = "post";
        form.action = U.logout;
        var token = cookie("csrftoken");
        if (token) {
            var hidden = el("input");
            hidden.type = "hidden";
            hidden.name = "csrfmiddlewaretoken";
            hidden.value = token;
            form.appendChild(hidden);
        }
        var submit = el("button", "dam-link dam-logout");
        submit.type = "submit";
        submit.appendChild(el("span", "dam-link-icon", "🚪"));
        submit.appendChild(el("span", "dam-link-label", L.logout || "Esci"));
        form.appendChild(submit);
        return form;
    }

    function buildDrawer() {
        var drawer = el("aside", "dam-drawer");
        drawer.setAttribute("role", "dialog");
        drawer.setAttribute("aria-label", L.menu || "Menu");

        var head = el("div", "dam-drawer-head");
        head.appendChild(el("div", "dam-avatar", (CFG.user && CFG.user.initial) || "?"));
        var who = el("div", "dam-drawer-user");
        who.appendChild(el("strong", null, (CFG.user && CFG.user.name) || ""));
        who.appendChild(el("span", null, CFG.title || ""));
        head.appendChild(who);
        var close = el("button", "dam-appbar-btn", "✕");
        close.type = "button";
        close.setAttribute("aria-label", L.close || "Chiudi");
        close.addEventListener("click", closePanel);
        head.appendChild(close);
        drawer.appendChild(head);

        var searchWrap = el("div", "dam-drawer-search");
        var search = el("input");
        search.type = "search";
        search.placeholder = L.searchMenu || "Cerca…";
        search.setAttribute("aria-label", L.searchMenu || "Cerca");
        searchWrap.appendChild(search);
        drawer.appendChild(searchWrap);
        S.drawerSearch = search;

        var body = el("div", "dam-drawer-body");
        var empty = el("p", "dam-empty", L.noResults || "Nessun risultato.");
        empty.hidden = true;

        var sections = [];
        each(CFG.groups, function (group) {
            var section = el("section", "dam-group");
            section.appendChild(el("h2", "dam-group-title", group.name));
            var rows = [];
            each(group.items, function (item) {
                var row = buildDrawerLink(item);
                section.appendChild(row);
                rows.push(row);
            });
            section.damRows = rows;
            body.appendChild(section);
            sections.push(section);
        });
        body.appendChild(empty);
        drawer.appendChild(body);

        search.addEventListener("input", function () {
            var needle = search.value.trim().toLowerCase();
            var found = 0;
            each(sections, function (section) {
                var shown = 0;
                each(section.damRows, function (row) {
                    var hit = !needle || row.damLabel.indexOf(needle) !== -1;
                    row.hidden = !hit;
                    if (hit) { shown += 1; }
                });
                section.hidden = shown === 0;
                found += shown;
            });
            empty.hidden = found !== 0;
        });

        var foot = el("div", "dam-drawer-foot");
        if (U.site) {
            var site = el("a", "dam-link");
            site.href = U.site;
            site.appendChild(el("span", "dam-link-icon", "🌐"));
            site.appendChild(el("span", "dam-link-label", L.site || "Vedi il sito"));
            foot.appendChild(site);
        }
        if (U.password) {
            var pwd = el("a", "dam-link");
            pwd.href = U.password;
            pwd.appendChild(el("span", "dam-link-icon", "🔑"));
            pwd.appendChild(el("span", "dam-link-label", L.password || "Cambia password"));
            foot.appendChild(pwd);
        }
        if (U.reorder) {
            var reorder = el("a", "dam-link");
            reorder.href = U.reorder;
            reorder.appendChild(el("span", "dam-link-icon", "🧩"));
            reorder.appendChild(el("span", "dam-link-label", L.reorder || "Organizza il menu"));
            foot.appendChild(reorder);
        }
        if (PWA) {
            var installLink = el("button", "dam-link");
            installLink.type = "button";
            installLink.appendChild(el("span", "dam-link-icon", "📲"));
            installLink.appendChild(el("span", "dam-link-label", L.install || "Installa l'app"));
            installLink.addEventListener("click", function () { closePanel(); install(); });
            installLink.hidden = !installable();
            foot.appendChild(installLink);
            S.installLink = installLink;
        }
        foot.appendChild(buildThemeRow());
        var logout = buildLogout();
        if (logout) { foot.appendChild(logout); }
        drawer.appendChild(foot);

        document.body.appendChild(drawer);
        return drawer;
    }

    function buildSheet(titleText) {
        var sheet = el("aside", "dam-sheet");
        sheet.setAttribute("role", "dialog");
        sheet.appendChild(el("div", "dam-sheet-grip"));

        var head = el("div", "dam-sheet-head");
        head.appendChild(el("h2", null, titleText));
        var close = el("button", "dam-sheet-close", "✕");
        close.type = "button";
        close.setAttribute("aria-label", L.close || "Chiudi");
        close.addEventListener("click", closePanel);
        head.appendChild(close);
        sheet.appendChild(head);

        var body = el("div", "dam-sheet-body");
        sheet.appendChild(body);
        sheet.damBody = body;

        document.body.appendChild(sheet);
        return sheet;
    }

    // ── Elenchi ──────────────────────────────────────────────────────────
    /** Quanti filtri sono attivi, dedotti dai parametri dell'indirizzo. */
    function activeFilterCount() {
        var ignored = { q: 1, p: 1, o: 1, all: 1, _changelist_filters: 1, _to_field: 1, _popup: 1 };
        var count = 0;
        each((window.location.search || "").replace(/^\?/, "").split("&"), function (pair) {
            if (!pair) { return; }
            var key = decodeURIComponent(pair.split("=")[0]);
            if (!ignored[key]) { count += 1; }
        });
        return count;
    }

    function decorateRows() {
        var table = document.getElementById("result_list");
        if (!table || table.dataset.damRows === "1") { return; }

        var headers = [];
        each(table.querySelectorAll("thead th"), function (th) {
            var span = th.querySelector(".text");
            headers.push(((span || th).textContent || "").replace(/\s+/g, " ").trim());
        });

        each(table.querySelectorAll("tbody tr"), function (row) {
            var titleDone = false;
            each(row.children, function (cell, index) {
                if (cell.classList.contains("action-checkbox")) { return; }
                var value = (cell.textContent || "").trim();
                if (!value) {
                    cell.classList.add("dam-empty-cell");
                    return;
                }
                if (!titleDone) {
                    cell.classList.add("dam-card-title");
                    titleDone = true;
                    return;   // il titolo non porta l'etichetta della colonna
                }
                if (headers[index]) { cell.setAttribute("data-label", headers[index]); }
            });
            if (row.querySelector("a[href]")) { row.classList.add("dam-row-link"); }
        });

        table.addEventListener("click", function (event) {
            if (!document.body.classList.contains("dam-cards")) { return; }
            if (closest(event.target, "a, input, select, button, label, textarea")) { return; }
            var row = closest(event.target, "tr");
            if (!row || !row.classList.contains("dam-row-link")) { return; }
            var link = row.querySelector("th a[href], td a[href]");
            if (link) { window.location.href = link.href; }
        });

        table.dataset.damRows = "1";
    }

    var CL = {};   // riferimenti agli elementi dell'elenco

    function changelistOn() {
        var changelist = document.getElementById("changelist");
        if (!changelist) { return; }

        // 1. Barra con ricerca e bottone filtri, subito sotto la barra in alto.
        if (!CL.toolbar) {
            CL.toolbar = el("div", "dam-toolbar");
            // Da Django 4.1 il form dell'elenco sta dentro
            // .changelist-form-container, quindi non è figlio diretto di
            // #changelist: si inserisce accanto al form, non dentro #changelist.
            var anchor = document.getElementById("changelist-form");
            var host = anchor ? anchor.parentNode : changelist;
            host.insertBefore(CL.toolbar, anchor || host.firstChild);
        }
        CL.toolbar.hidden = false;

        var search = document.getElementById("toolbar") || document.getElementById("changelist-search");
        if (search) { park(search, CL.toolbar); }

        // 2. Filtri e azioni dentro un pannello che sale dal basso.
        // Le azioni di massa restano dov'erano: il JavaScript di Django le
        // cerca dentro #changelist-form, spostarle fuori lo romperebbe.
        // Il foglio accoglie solo i filtri.
        var filters = document.getElementById("changelist-filter");
        if (F.filterSheet && filters) {
            if (!CL.sheet) {
                CL.sheet = buildSheet(L.filters || "Filtri");
                S.sheet = CL.sheet;
            }
            park(filters, CL.sheet.damBody);

            if (!CL.filterBtn) {
                CL.filterBtn = el("button", "dam-filter-btn");
                CL.filterBtn.type = "button";
                CL.filterBtn.textContent = "⚙ " + (L.filters || "Filtri");
                CL.filterBtn.addEventListener("click", function () { showPanel(CL.sheet); });
            }
            CL.filterBtn.dataset.count = String(activeFilterCount());
            CL.toolbar.appendChild(CL.filterBtn);
        }

        // 3. Bottone flottante "aggiungi", preso dagli strumenti dell'oggetto.
        if (F.fab && !CL.fab) {
            var add = document.querySelector(".object-tools .addlink");
            if (add) {
                CL.fab = el("a", "dam-fab");
                CL.fab.href = add.href;
                CL.fab.appendChild(el("span", "dam-fab-plus", "+"));
                CL.fab.appendChild(el("span", null, L.add || "Aggiungi"));
                document.body.appendChild(CL.fab);
            }
        }
        if (CL.fab) {
            CL.fab.hidden = false;
            document.body.classList.add("dam-has-fab");
        }

        wireSelection();

        if (F.cards) {
            decorateRows();
            document.body.classList.add("dam-cards");
        }
    }

    /* Le azioni di massa servono solo dopo aver scelto delle righe: finché
     * non c'è niente di selezionato restano nascoste, poi salgono dal basso. */
    function wireSelection() {
        var form = document.getElementById("changelist-form");
        if (!form || form.dataset.damSelection === "1") { return; }
        if (!form.querySelector("input.action-select")) { return; }

        function sync() {
            var any = !!form.querySelector("input.action-select:checked");
            document.body.classList.toggle("dam-selection", any);
        }
        form.addEventListener("change", function (event) {
            var target = event.target;
            if (target && (target.classList.contains("action-select") || target.id === "action-toggle")) {
                sync();
            }
        });
        form.dataset.damSelection = "1";
        sync();
    }

    function changelistOff() {
        document.body.classList.remove("dam-cards");
        var search = document.getElementById("toolbar") || document.getElementById("changelist-search");
        unpark(search);
        var filters = document.getElementById("changelist-filter");
        unpark(filters);
        if (CL.toolbar) { CL.toolbar.hidden = true; }
        if (CL.fab) { CL.fab.hidden = true; }
        document.body.classList.remove("dam-has-fab", "dam-selection");
        closePanel();
    }

    // ── Moduli: una sola barra di azioni in fondo ────────────────────────
    var FORM = {};

    /* Riserva in fondo al contenuto esattamente lo spazio occupato dalla
     * barra. Un valore fisso sbaglia sempre: la barra cambia altezza con la
     * lingua, con il numero di bottoni e con la tacca del telefono. */
    function syncSubmitRow() {
        var row = FORM.row;
        if (!row || !document.body.classList.contains("dam-mobile")) {
            document.documentElement.style.removeProperty("--dam-submitrow-h");
            return;
        }
        document.documentElement.style.setProperty(
            "--dam-submitrow-h", row.offsetHeight + "px"
        );
    }

    /** L'azione principale: quella che Django marca come predefinita. */
    function primaryAction(row, controls) {
        return row.querySelector("input.default, button.default") ||
            row.querySelector('[name="_save"]') ||
            row.querySelector('[name="_continue"]') ||
            controls[0];
    }

    /* Le pagine di conferma di Django (eliminazione singola, eliminazione
     * di massa) non usano .submit-row: i bottoni "Sì, sono sicuro" e
     * "No, torna indietro" stanno in un <div> qualunque in fondo alla pagina,
     * dove le barre fisse li coprirebbero. Gli si aggiunge la classe di
     * Django, così eredita tutto lo stile della barra azioni. */
    function adoptConfirmRow() {
        if (document.querySelector(".submit-row")) { return null; }
        // Negli elenchi il primo invio è il bottone "Cerca": non è affatto
        // un comando di conferma e non va trasformato in barra.
        if (KIND === "changelist") { return null; }
        var submit = document.querySelector(
            "#content form input[type=submit], #content form button[type=submit]"
        );
        if (!submit) { return null; }
        if (closest(submit, "#toolbar, #changelist-search, .dam-toolbar")) { return null; }
        var row = submit.parentNode;
        if (!row || row.nodeType !== 1 || row === document.body) { return null; }
        row.classList.add("submit-row", "dam-synth-row");
        return row;
    }

    function formOn() {
        var row = document.querySelector(".submit-row") || adoptConfirmRow();
        if (!row) { return; }
        FORM.row = row;
        document.body.classList.add("dam-has-submitrow");
        // Una pagina di conferma è a tutti gli effetti una schermata di
        // lavoro: la barra in basso serve più della navigazione.
        if (KIND === "form" || KIND === "other") { document.body.classList.add("dam-editing"); }

        if (!FORM.ready) {
            var controls = Array.prototype.slice.call(row.querySelectorAll(
                'input[type="submit"], button[type="submit"], a.deletelink, a.closelink'
            ));
            if (!controls.length) { FORM.ready = true; syncSubmitRow(); return; }

            var primary = primaryAction(row, controls);
            primary.classList.add("dam-primary");

            var others = controls.filter(function (c) { return c !== primary; });
            // L'eliminazione va in fondo: è quella da cui si torna indietro peggio.
            others.sort(function (a, b) {
                return (a.classList.contains("deletelink") ? 1 : 0) -
                    (b.classList.contains("deletelink") ? 1 : 0);
            });

            var form = closest(row, "form");
            if (others.length && form && form.id) {
                // Spostare un bottone fuori dal <form> lo scollegherebbe:
                // l'attributo form= lo riaggancia, e così resta un bottone
                // vero (niente copie che perderebbero il proprio name).
                if (!FORM.sheet) { FORM.sheet = buildSheet(L.actions || "Azioni"); }
                each(others, function (control) {
                    if (control.tagName === "INPUT" || control.tagName === "BUTTON") {
                        control.setAttribute("form", form.id);
                    }
                    control.classList.add("dam-sheet-action");
                    park(control, FORM.sheet.damBody);
                    control.addEventListener("click", closePanel);
                });
                var more = el("button", "dam-more", "⋯");
                more.type = "button";
                more.setAttribute("aria-label", L.actions || "Azioni");
                more.setAttribute("aria-haspopup", "dialog");
                more.addEventListener("click", function () { showPanel(FORM.sheet); });
                row.appendChild(more);
                FORM.more = more;
                FORM.others = others;
                document.body.classList.add("dam-actions-sheet");
            }
            FORM.ready = true;
        }

        syncSubmitRow();
        if (!FORM.observer && window.ResizeObserver) {
            FORM.observer = new window.ResizeObserver(syncSubmitRow);
            FORM.observer.observe(row);
        }
    }

    function formOff() {
        document.body.classList.remove("dam-has-submitrow", "dam-editing", "dam-actions-sheet");
        if (FORM.row && FORM.row.classList.contains("dam-synth-row")) {
            FORM.row.classList.remove("submit-row", "dam-synth-row");
        }
        if (FORM.more) { FORM.more.hidden = true; }
        each(FORM.others, function (control) {
            control.removeAttribute("form");
            control.classList.remove("dam-sheet-action");
            unpark(control);
        });
        syncSubmitRow();
    }

    // ── Schermata iniziale ───────────────────────────────────────────────
    /* Se il progetto ha una sua dashboard senza griglia di icone, la
     * costruiamo qui dai dati del menu: così anche un admin personalizzato
     * ottiene la schermata home in stile app. */
    function homeOn() {
        if (document.querySelector(".dam-home")) { return; }
        var main = document.getElementById("content-main") || document.getElementById("content");
        if (!main || !CFG.groups || !CFG.groups.length) { return; }

        if (!S.home) {
            // Una griglia unica: raggruppare per app, con molte app da una
            // voce sola, allungherebbe la pagina senza aiutare nessuno.
            // L'elenco diviso per app resta nel menu laterale.
            var home = el("div", "dam-home");
            var section = el("section", "dam-home-group");
            section.appendChild(el("h2", "dam-home-title", L.allSections || "Tutte le sezioni"));
            var grid = el("div", "dam-mobile-menu");
            each(ITEMS, function (item) {
                var tile = el("a", "dam-tile");
                tile.href = item.url;
                tile.style.setProperty("--dam-color", item.color);
                tile.style.setProperty("--dam-bg", item.background);
                tile.appendChild(el("span", "dam-tile-icon", item.icon || "•"));
                tile.appendChild(el("span", "dam-tile-label", item.label));
                grid.appendChild(tile);
            });
            section.appendChild(grid);
            home.appendChild(section);
            main.appendChild(home);
            S.home = home;
        }
        S.home.hidden = false;

        // L'elenco classico per app diventa un doppione: si nasconde.
        each(main.querySelectorAll(".module"), function (module) {
            if (/(^|\s)app-[\w-]+(\s|$)/.test(module.className)) {
                module.classList.add("dam-hidden-module");
            }
        });
        each(main.querySelectorAll("details"), function (details) {
            if (!details.querySelector(".module:not(.dam-hidden-module)") &&
                details.querySelector(".dam-hidden-module")) {
                details.classList.add("dam-hidden-module");
            }
        });
    }

    function homeOff() {
        if (S.home) { S.home.hidden = true; }
        each(document.querySelectorAll(".dam-hidden-module"), function (node) {
            node.classList.remove("dam-hidden-module");
        });
    }

    // ── Attivazione / disattivazione ─────────────────────────────────────
    var built = false;

    function buildOnce() {
        if (built) { return; }
        built = true;
        if (F.drawer) { S.scrim = buildScrim(); S.drawer = buildDrawer(); }
        else if (F.filterSheet) { S.scrim = buildScrim(); }
        if (F.appbar) { S.appbar = buildAppbar(); }
        if (F.tabbar) { S.tabbar = buildTabbar(); }
    }

    function enterMobile() {
        var body = document.body;

        if (KIND === "login") {
            body.classList.add("dam-mobile", "dam-no-appbar", "dam-no-tabbar");
            return;
        }

        buildOnce();
        body.classList.add("dam-mobile");
        if (F.hideChrome) { body.classList.add("dam-hide-chrome"); }
        if (F.forms) { body.classList.add("dam-forms"); }
        if (!S.appbar) { body.classList.add("dam-no-appbar"); }
        if (!S.tabbar) { body.classList.add("dam-no-tabbar"); }
        if (F.forms) { formOn(); }

        if (KIND === "changelist") { changelistOn(); }
        if (KIND === "index") { homeOn(); }
    }

    function leaveMobile() {
        var body = document.body;
        formOff();
        body.classList.remove(
            "dam-mobile", "dam-hide-chrome", "dam-forms",
            "dam-no-appbar", "dam-no-tabbar"
        );
        if (KIND === "changelist") { changelistOff(); }
        if (KIND === "index") { homeOff(); }
        closePanel();
    }

    function apply() {
        if (mq.matches) { enterMobile(); } else { leaveMobile(); }
    }

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") { closePanel(); }
    });

    function syncBars() { syncSubmitRow(); syncInstallBanner(); }
    window.addEventListener("resize", syncBars);
    window.addEventListener("orientationchange", syncBars);

    registerServiceWorker();
    apply();
    showInstallBanner();
    syncBars();
    if (mq.addEventListener) { mq.addEventListener("change", apply); }
    else if (mq.addListener) { mq.addListener(apply); }
})();
