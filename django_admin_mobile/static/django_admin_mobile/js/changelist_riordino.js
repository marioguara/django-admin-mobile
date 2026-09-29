/* Riordino delle icone trascinando le righe dell'elenco.
 *
 * L'ordine non si scrive più a mano nella colonna «order»: si trascina la
 * riga per la maniglia e i numeri li riscrive questo script. Poi si salva col
 * pulsante che l'elenco di Django ha già — nessun endpoint in più, e finché
 * non si salva si può tornare indietro ricaricando la pagina.
 *
 * Usa i Pointer Events e non il drag-and-drop HTML5, che sul telefono non
 * esiste: la stessa scelta della pagina «Organizza il menu».
 *
 * I numeri assegnati sono quelli che erano già nella pagina, riordinati: così
 * con l'elenco paginato la seconda pagina non finisce a collidere con la prima.
 */
(function () {
    "use strict";

    function avvia() {
        var tabella = document.getElementById("result_list");
        if (!tabella) { return; }
        var corpo = tabella.querySelector("tbody");
        if (!corpo) { return; }

        // Se l'elenco è ordinato per un'altra colonna, trascinare non vuol
        // dire niente: si dice perché e si lascia stare.
        var ordinatoAltrove = /[?&]o=/.test(window.location.search);
        if (ordinatoAltrove) {
            spiega(tabella,
                "L'elenco è ordinato per un'altra colonna: togli l'ordinamento " +
                "(clic sull'intestazione) per poter trascinare le righe.");
            document.querySelectorAll(".dam-riga-presa").forEach(function (p) {
                p.style.opacity = "0.25";
                p.style.cursor = "not-allowed";
            });
            return;
        }

        function righe() {
            return Array.prototype.slice.call(corpo.querySelectorAll("tr"));
        }

        function campiOrdine() {
            return righe().map(function (riga) {
                return riga.querySelector('input[name$="-order"]');
            });
        }

        /* Rinumera i campi «order» secondo il nuovo ordine delle righe.
           Si riusano i valori già presenti nella pagina, riordinati: così con
           l'elenco paginato la seconda pagina non collide con la prima.
           Se però quei valori sono tutti uguali — è il caso appena le voci
           vengono create, tutte a zero — non distinguono niente, e allora si
           parte dal più piccolo e si conta: 0, 1, 2… altrimenti trascinare
           non cambierebbe nulla e il salvataggio non salverebbe l'ordine. */
        function rinumera() {
            var campi = campiOrdine();
            if (!campi.length || campi.some(function (c) { return !c; })) { return false; }

            var valori = campi.map(function (c) { return parseInt(c.value, 10) || 0; });
            var distinti = valori.filter(function (v, i, a) { return a.indexOf(v) === i; });
            if (distinti.length === valori.length) {
                valori.sort(function (a, b) { return a - b; });
            } else {
                var minimo = Math.min.apply(null, valori);
                valori = campi.map(function (_, i) { return minimo + i; });
            }

            var cambiato = false;
            campi.forEach(function (campo, i) {
                if (String(valori[i]) !== campo.value) {
                    campo.value = valori[i];
                    cambiato = true;
                }
            });
            return cambiato;
        }

        var avvisoMostrato = false;
        function ricordaDiSalvare() {
            if (avvisoMostrato) { return; }
            avvisoMostrato = true;
            spiega(tabella, "Ordine cambiato: premi «Salva» in fondo per confermarlo.",
                   "dam-avviso-ordine");
        }

        // ── Trascinamento ───────────────────────────────────────────────
        var inMovimento = null;

        function rigaSopra(y) {
            var tutte = righe();
            for (var i = 0; i < tutte.length; i++) {
                if (tutte[i] === inMovimento) { continue; }
                var box = tutte[i].getBoundingClientRect();
                if (y < box.top + box.height / 2) { return tutte[i]; }
            }
            return null;
        }

        function scorri(y) {
            var margine = 90;
            if (y < margine) { window.scrollBy(0, -12); }
            else if (y > window.innerHeight - margine) { window.scrollBy(0, 12); }
        }

        corpo.addEventListener("pointerdown", function (ev) {
            var presa = ev.target.closest(".dam-riga-presa");
            if (!presa || ev.button > 0) { return; }
            inMovimento = presa.closest("tr");
            if (!inMovimento) { return; }
            inMovimento.classList.add("dam-riga-in-movimento");
            try { presa.setPointerCapture(ev.pointerId); } catch (e) { /* non supportato */ }
            ev.preventDefault();
        });

        corpo.addEventListener("pointermove", function (ev) {
            if (!inMovimento) { return; }
            ev.preventDefault();
            scorri(ev.clientY);
            var bersaglio = rigaSopra(ev.clientY);
            if (bersaglio !== inMovimento) {
                corpo.insertBefore(inMovimento, bersaglio);
            }
        });

        function fine() {
            if (!inMovimento) { return; }
            inMovimento.classList.remove("dam-riga-in-movimento");
            inMovimento.classList.add("dam-riga-appena-spostata");
            var riga = inMovimento;
            window.setTimeout(function () {
                riga.classList.remove("dam-riga-appena-spostata");
            }, 700);
            inMovimento = null;
            if (rinumera()) { ricordaDiSalvare(); }
            rigaAlterna();
        }

        corpo.addEventListener("pointerup", fine);
        corpo.addEventListener("pointercancel", fine);
        window.addEventListener("blur", fine);

        /* L'admin colora le righe alternate con row1/row2: dopo uno spostamento
           i colori resterebbero attaccati alla riga sbagliata. */
        function rigaAlterna() {
            righe().forEach(function (riga, i) {
                riga.classList.remove("row1", "row2");
                riga.classList.add(i % 2 === 0 ? "row1" : "row2");
            });
        }

        // ── Tastiera: le frecce restano l'unica via senza mouse ─────────
        corpo.addEventListener("keydown", function (ev) {
            var presa = ev.target.closest(".dam-riga-presa");
            if (!presa) { return; }
            var riga = presa.closest("tr");
            if (ev.key === "ArrowUp" && riga.previousElementSibling) {
                corpo.insertBefore(riga, riga.previousElementSibling);
            } else if (ev.key === "ArrowDown" && riga.nextElementSibling) {
                corpo.insertBefore(riga.nextElementSibling, riga);
            } else {
                return;
            }
            ev.preventDefault();
            presa.focus();
            if (rinumera()) { ricordaDiSalvare(); }
            rigaAlterna();
        });

        // Le maniglie devono essere raggiungibili da tastiera.
        document.querySelectorAll(".dam-riga-presa").forEach(function (presa) {
            presa.tabIndex = 0;
            presa.setAttribute("role", "button");
            presa.setAttribute("aria-label", "Sposta la voce: frecce su e giù");
        });

        spiega(tabella, "Trascina le righe per la maniglia ⠿ per cambiare l'ordine " +
                        "del menu, poi salva.", "dam-nota-ordine");
    }

    function spiega(tabella, testo, classe) {
        var esistente = classe && document.querySelector("." + classe);
        if (esistente) { esistente.textContent = testo; return; }
        var nota = document.createElement("p");
        nota.className = "dam-nota-riordino " + (classe || "");
        nota.textContent = testo;
        tabella.parentNode.insertBefore(nota, tabella);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", avvia);
    } else {
        avvia();
    }
})();
