/* django_admin_mobile
 * Comportamenti mobile:
 *  - Trasforma la tabella del changelist in card impilate (aggiunge attributi
 *    data-label alle celle così il CSS può mostrarli come label).
 *  - Aggiunge un FAB "Filtra" per aprire/chiudere il drawer dei filtri.
 */
(function () {
    var MOBILE = window.matchMedia('(max-width: 1024px)');

    function decorateChangelist() {
        var table = document.querySelector('#result_list');
        if (!table || table.dataset.damDecorated === '1') return;
        var headers = Array.prototype.map.call(
            table.querySelectorAll('thead th'),
            function (th) { return (th.innerText || th.textContent || '').trim(); }
        );
        Array.prototype.forEach.call(table.querySelectorAll('tbody tr'), function (row) {
            Array.prototype.forEach.call(row.children, function (cell, idx) {
                if (headers[idx]) cell.setAttribute('data-label', headers[idx]);
            });
        });
        table.dataset.damDecorated = '1';
        document.body.classList.add('dam-cards');
    }

    function setupFilterDrawer() {
        var filter = document.getElementById('changelist-filter');
        if (!filter || document.querySelector('.dam-filter-fab')) return;
        var fab = document.createElement('button');
        fab.type = 'button';
        fab.className = 'dam-filter-fab';
        fab.textContent = '⚙ Filtri';
        fab.addEventListener('click', function () {
            filter.classList.toggle('dam-open');
        });
        document.body.appendChild(fab);
        document.addEventListener('click', function (e) {
            if (!filter.classList.contains('dam-open')) return;
            if (filter.contains(e.target) || fab.contains(e.target)) return;
            filter.classList.remove('dam-open');
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') filter.classList.remove('dam-open');
        });
    }

    function apply() {
        if (!MOBILE.matches) {
            document.body.classList.remove('dam-cards');
            return;
        }
        decorateChangelist();
        setupFilterDrawer();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', apply);
    } else {
        apply();
    }
    if (MOBILE.addEventListener) MOBILE.addEventListener('change', apply);
    else if (MOBILE.addListener) MOBILE.addListener(apply);
})();
