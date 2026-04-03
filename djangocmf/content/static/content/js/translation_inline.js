(function () {
    'use strict';

    // Read prefix from the embedded formset config instead of hardcoding.
    const group      = document.querySelector('.js-inline-admin-formset[data-inline-type="stacked"]');
    const PREFIX     = JSON.parse(group.dataset.inlineFormset).options.prefix;
    const TAB_NAV_ID = 'translation-tab-nav';
    const ADD_BTN_ID = 'translation-add-btn';

    /**
     * Get the maximum number of allowed rows from Django's management form.
     * Django sets MAX_NUM_FORMS to 1000 when no max_num is specified, treat that as unlimited.
     * @returns {number}
     */
    function getMaxNum() {
        const el = document.getElementById('id_' + PREFIX + '-MAX_NUM_FORMS');
        if (!el) return Infinity;
        const val = parseInt(el.value);
        return (isNaN(val) || val >= 1000) ? Infinity : val;
    }

    /**
     * Get display label for a given row index.
     * Reads the selected language name from the language_code <select> element.
     * Falls back to "New Language" when no language is selected yet.
     * @param {number} index - Row index (0-based)
     * @param {boolean} hasData - Whether the row has existing data (has_original)
     * @returns {string}
     */
    function getLangCode(index, hasData) {
        if (!hasData) return 'New Language';
        const el = document.getElementById('id_' + PREFIX + '-' + index + '-language_code');
        if (el && el.selectedOptions.length > 0) {
            return el.selectedOptions[0].text;
        }
        return 'New Language';
    }

    /**
     * Create a nav tab <li> element for a given row index.
     * @param {number} index - Row index (0-based)
     * @param {string} label - Display label for the tab
     * @param {boolean} deletable - Whether to show a delete button on the tab
     * @returns {HTMLElement}
     */
    function createTabItem(index, label, deletable) {
        const li     = document.createElement('li');
        li.className = 'nav-item';

        const a            = document.createElement('a');
        a.className        = 'nav-link';
        a.href             = '#' + PREFIX + '-' + index;
        a.dataset.bsToggle = 'tab';
        a.textContent      = label;

        if (deletable) {
            const del       = document.createElement('span');
            del.className   = 'tab-delete-btn ms-2';
            del.textContent = '×';
            a.appendChild(del);
        }

        li.appendChild(a);
        return li;
    }

    /**
     * Sync tab href attributes with current row IDs.
     * Called after a row is deleted and remaining rows are re-indexed.
     */
    function syncTabHrefs() {
        const rows = group.querySelectorAll('.inline-related:not(.empty-form)');
        const tabs = document.querySelectorAll('#' + TAB_NAV_ID + ' li.nav-item');
        rows.forEach(function (row, i) {
            const li = tabs[i];
            if (!li) return;
            li.querySelector('.nav-link').href = '#' + row.id;
        });
    }

    /**
     * Show or hide the add button based on whether the max form count has been reached.
     */
    function syncAddBtn() {
        const addBtn = document.getElementById(ADD_BTN_ID);
        if (!addBtn) return;
        const maxForms   = document.getElementById('id_' + PREFIX + '-MAX_NUM_FORMS');
        const totalForms = document.getElementById('id_' + PREFIX + '-TOTAL_FORMS');
        if (!maxForms || !totalForms) return;
        const reached = maxForms.value !== '' && (maxForms.value - totalForms.value) <= 0;
        addBtn.classList.toggle('disabled', reached);
    }

    /**
     * Bind delete button click event to a tab <li> element.
     * Triggers Django's native inline delete, removes the tab, syncs hrefs,
     * and activates the first remaining tab if the deleted tab was active.
     * @param {HTMLElement} li - The tab <li> element to bind events to
     */
    function bindTabEvents(li) {
        const delBtn = li.querySelector('.tab-delete-btn');
        if (!delBtn) return;

        delBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const tabs = Array.from(document.querySelectorAll('#' + TAB_NAV_ID + ' li.nav-item'));
            const rows = Array.from(group.querySelectorAll('.inline-related:not(.empty-form)'));
            const pos  = tabs.indexOf(li);
            const row  = rows[pos];
            if (!row) return;

            const nativeDelBtn = row.querySelector('.inline-deletelink');
            if (!nativeDelBtn) return;

            const wasActive = document.querySelector('#' + TAB_NAV_ID + ' .nav-link.active')
                ?.getAttribute('href') === '#' + row.id;
            nativeDelBtn.click();
            li.remove();
            syncTabHrefs();
            syncAddBtn();

            if (wasActive) {
                const firstLink = document.querySelector('#' + TAB_NAV_ID + ' .nav-link');
                if (firstLink) new tabler.Tab(firstLink).show();
            }
        });
    }

    /**
     * Add a new tab for a newly added inline row.
     * Inserts the tab before the add button, binds events, watches for language
     * selection changes to update the tab label, and activates the new tab.
     * @param {number} index - Row index (0-based) of the newly added row
     */
    function addTab(index) {
        const li       = createTabItem(index, getLangCode(index, false), true);
        const nav      = document.getElementById(TAB_NAV_ID);
        const addBtnLi = document.getElementById('translation-add-tab');
        nav.insertBefore(li, addBtnLi);
        bindTabEvents(li);

        // Update tab label when user selects a language.
        const select = document.getElementById('id_' + PREFIX + '-' + index + '-language_code');
        if (select) {
            select.addEventListener('change', function () {
                const tabs     = Array.from(document.querySelectorAll('#' + TAB_NAV_ID + ' li.nav-item'));
                const rows     = Array.from(group.querySelectorAll('.inline-related:not(.empty-form)'));
                const rowEl    = document.getElementById(PREFIX + '-' + index);
                const pos      = rows.indexOf(rowEl);
                const targetLi = tabs[pos];
                if (!targetLi) return;
                const link       = targetLi.querySelector('.nav-link');
                const delBtn     = link.querySelector('.tab-delete-btn');
                link.textContent = this.value ? this.selectedOptions[0].text : 'New Language';
                if (delBtn) link.appendChild(delBtn);
            });
        }

        new tabler.Tab(li.querySelector('.nav-link')).show();
    }

    /**
     * Initialize the tab UI on page load.
     * Builds tabs for all existing inline rows (ordering guaranteed by backend queryset),
     * activates the first tab, and wires up the add button and formset:added event.
     */
    function init() {
        if (!group) return;

        let firstTab = null;
        group.querySelectorAll('.inline-related:not(.empty-form)').forEach(function (row) {
            const index   = parseInt(row.id.split('-').pop());
            const hasData = row.classList.contains('has_original');
            const lang    = getLangCode(index, hasData);

            if (!hasData && lang === 'New Language' && firstTab !== null) return;

            const li       = createTabItem(index, lang, !hasData);
            const addBtnLi = document.getElementById('translation-add-tab');
            document.getElementById(TAB_NAV_ID).insertBefore(li, addBtnLi);
            bindTabEvents(li);
            if (firstTab === null) firstTab = li.querySelector('.nav-link');
        });

        if (firstTab) new tabler.Tab(firstTab).show();

        const addBtn = document.getElementById(ADD_BTN_ID);
        if (addBtn) {
            addBtn.addEventListener('click', function (e) {
                e.preventDefault();
                const currentRows = group.querySelectorAll('.inline-related:not(.empty-form)').length;
                if (currentRows >= getMaxNum()) return;
                const nativeAdd = group.querySelector('.add-row a');
                if (nativeAdd) nativeAdd.click();
            });
        }

        document.addEventListener('formset:added', function (e) {
            if (e.detail.formsetName !== PREFIX) return;
            addTab(parseInt(e.target.id.split('-').pop()));
            syncAddBtn();
        });

        syncAddBtn();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();