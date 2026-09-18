/* Riordino delle voci di menu.
 *
 * Due modi, entrambi sempre disponibili:
 *  - trascinamento con la maniglia (funziona con dito, penna e mouse, perché
 *    usa i Pointer Events invece del drag-and-drop HTML5, che sul telefono
 *    non esiste);
 *  - frecce su/giù, che restano l'unica via da tastiera e da lettore di
 *    schermo.
 *
 * L'ordine viene inviato dal DOM: i campi nascosti "entry" si serializzano
 * nell'ordine in cui stanno nella pagina, quindi spostare la riga è già
 * salvare l'ordine.
 */
(function () {
    "use strict";

    var list = document.getElementById("dam-reorder");
    if (!list) { return; }

    function rows() {
        return Array.prototype.slice.call(list.querySelectorAll(".dam-sortable"));
    }

    function refreshArrows() {
        var all = rows();
        all.forEach(function (row, index) {
            var up = row.querySelector('.dam-move[data-dir="-1"]');
            var down = row.querySelector('.dam-move[data-dir="1"]');
            if (up) { up.disabled = index === 0; }
            if (down) { down.disabled = index === all.length - 1; }
        });
    }

    function flash(row) {
        row.classList.add("dam-just-moved");
        window.setTimeout(function () { row.classList.remove("dam-just-moved"); }, 600);
    }

    // ── Frecce ───────────────────────────────────────────────────────────
    list.addEventListener("click", function (event) {
        var button = event.target.closest(".dam-move");
        if (!button || button.disabled) { return; }
        var row = button.closest(".dam-sortable");
        var direction = parseInt(button.dataset.dir, 10);
        if (direction < 0 && row.previousElementSibling) {
            list.insertBefore(row, row.previousElementSibling);
        } else if (direction > 0 && row.nextElementSibling) {
            list.insertBefore(row.nextElementSibling, row);
        }
        refreshArrows();
        flash(row);
        // Il fuoco resta sul bottone spostato, così si può premere più volte.
        button.focus();
        row.scrollIntoView({ block: "nearest" });
    });

    // ── Trascinamento ────────────────────────────────────────────────────
    var dragging = null;

    /** La riga sopra cui inserire, dato il punto verticale del dito. */
    function rowBefore(y) {
        var all = rows();
        for (var i = 0; i < all.length; i++) {
            if (all[i] === dragging) { continue; }
            var box = all[i].getBoundingClientRect();
            if (y < box.top + box.height / 2) { return all[i]; }
        }
        return null;
    }

    /** Scorre la pagina quando il dito arriva ai bordi dello schermo. */
    function autoScroll(y) {
        var margin = 90;
        if (y < margin) { window.scrollBy(0, -12); }
        else if (y > window.innerHeight - margin) { window.scrollBy(0, 12); }
    }

    list.addEventListener("pointerdown", function (event) {
        var grip = event.target.closest(".dam-grip");
        if (!grip || event.button > 0) { return; }
        dragging = grip.closest(".dam-sortable");
        if (!dragging) { return; }
        dragging.classList.add("dam-dragging");
        try { grip.setPointerCapture(event.pointerId); } catch (e) { /* non supportato */ }
        event.preventDefault();
    });

    list.addEventListener("pointermove", function (event) {
        if (!dragging) { return; }
        event.preventDefault();
        autoScroll(event.clientY);
        var target = rowBefore(event.clientY);
        if (target !== dragging) {
            list.insertBefore(dragging, target);
        }
    });

    function endDrag() {
        if (!dragging) { return; }
        dragging.classList.remove("dam-dragging");
        flash(dragging);
        dragging = null;
        refreshArrows();
    }

    list.addEventListener("pointerup", endDrag);
    list.addEventListener("pointercancel", endDrag);
    window.addEventListener("blur", endDrag);

    refreshArrows();
})();
