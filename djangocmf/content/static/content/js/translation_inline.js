(function () {
    'use strict';

    const group      = document.querySelector('.js-inline-admin-formset[data-inline-type="stacked"]');
    const PREFIX     = JSON.parse(group.dataset.inlineFormset).options.prefix;
    const TAB_NAV_ID = 'translation-tab-nav';
    const ADD_BTN_ID = 'translation-add-btn';
    const nav        = document.getElementById(TAB_NAV_ID);

    /**
     * Return the maximum number of allowed rows.
     * When USE_I18N is disabled, only one translation is allowed.
     * Django sets MAX_NUM_FORMS to 1000 when no max_num is configured — treat that as unlimited.
     * @returns {number}
     */
    function getMaxNum() {
        if (nav && nav.dataset.useI18n === 'false') return 1;
        const el = document.getElementById('id_' + PREFIX + '-MAX_NUM_FORMS');
        if (!el) return Infinity;
        const val = parseInt(el.value);
        return (isNaN(val) || val >= 1000) ? Infinity : val;
    }

    /**
     * Return the display label for a row.
     * Reads the current selected option text from the language_code <select>.
     * Falls back to "New Language" when no language is selected.
     * @param {number} index
     * @returns {string}
     */
    function getLabel(index) {
        const el = document.getElementById('id_' + PREFIX + '-' + index + '-language_code');
        return (el && el.value) ? el.selectedOptions[0].text : 'New Language';
    }

    /**
     * Create a nav tab <li> element for a given row index.
     * @param {number} index
     * @param {string} label
     * @param {boolean} deletable - Whether to render a delete button on the tab
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
     * Sync tab href attributes after rows are re-indexed following a deletion.
     */
    function syncTabHrefs() {
        const rows = group.querySelectorAll('.inline-related:not(.empty-form)');
        const tabs = nav.querySelectorAll('li.nav-item:not(#translation-add-tab)');
        rows.forEach(function (row, i) {
            const li = tabs[i];
            if (li) li.querySelector('.nav-link').href = '#' + row.id;
        });
    }

    /**
     * Show or hide the add button based on whether the row limit has been reached.
     * With extra=0, TOTAL_FORMS exactly equals the number of real rows, so no adjustment needed.
     */
    function syncAddBtn() {
        const addBtnLi = document.getElementById('translation-add-tab');
        if (!addBtnLi) return;

        if (nav.dataset.useI18n === 'false') {
            addBtnLi.style.display = 'none';
            return;
        }

        const totalForms = document.getElementById('id_' + PREFIX + '-TOTAL_FORMS');
        if (!totalForms) return;
        addBtnLi.style.display = parseInt(totalForms.value) >= getMaxNum() ? 'none' : '';
    }

    /**
     * Bind a change listener on the language_code select for a given row index.
     * Keeps the corresponding nav tab label in sync with the selected language.
     * @param {number} index
     */
    function bindLabelSync(index) {
        const select = document.getElementById('id_' + PREFIX + '-' + index + '-language_code');
        if (!select) return;
        select.addEventListener('change', function () {
            const rows     = Array.from(group.querySelectorAll('.inline-related:not(.empty-form)'));
            const tabs     = Array.from(nav.querySelectorAll('li.nav-item:not(#translation-add-tab)'));
            const pos      = rows.indexOf(document.getElementById(PREFIX + '-' + index));
            const targetLi = tabs[pos];
            if (!targetLi) return;
            const link       = targetLi.querySelector('.nav-link');
            const delBtn     = link.querySelector('.tab-delete-btn');
            link.textContent = this.value ? this.selectedOptions[0].text : 'New Language';
            if (delBtn) link.appendChild(delBtn);
        });
    }

    /**
     * Bind the delete button on a tab <li>.
     * Triggers Django's native inline delete, removes the tab, re-syncs hrefs,
     * and activates the first remaining tab if the deleted one was active.
     * @param {HTMLElement} li
     */
    function bindTabEvents(li) {
        const delBtn = li.querySelector('.tab-delete-btn');
        if (!delBtn) return;

        delBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const tabs = Array.from(nav.querySelectorAll('li.nav-item:not(#translation-add-tab)'));
            const rows = Array.from(group.querySelectorAll('.inline-related:not(.empty-form)'));
            const row  = rows[tabs.indexOf(li)];
            if (!row) return;

            const nativeDelBtn = row.querySelector('.inline-deletelink');
            if (!nativeDelBtn) return;

            // Destroy all HugeRTE instances before Django re-indexes the rows.
            group.querySelectorAll('textarea.hugerte-editor').forEach(function (textarea) {
                const editor = hugerte.get(textarea.id);
                if (editor) editor.remove();
            });

            const wasActive = nav.querySelector('.nav-link.active')?.getAttribute('href') === '#' + row.id;
            nativeDelBtn.click();
            li.remove();
            syncTabHrefs();
            syncAddBtn();

            // Re-initialize HugeRTE for all remaining visible tabs.
            nav.querySelectorAll('li.nav-item:not(#translation-add-tab) .nav-link').forEach(function (link) {
                const rowId    = link.getAttribute('href').replace('#', '');
                const textarea = document.querySelector('#' + rowId + ' textarea.hugerte-editor');
                if (textarea) initHugerte(textarea);
            });

            if (wasActive) {
                const firstLink = nav.querySelector('li.nav-item:not(#translation-add-tab) .nav-link');
                if (firstLink) new tabler.Tab(firstLink).show();
            }
        });
    }

    /**
     * Add a tab for a newly added inline row.
     * Inserts the tab before the add button, binds events, watches for language
     * selection changes to update the label, and activates the new tab.
     * HugeRTE is initialized only after the tab becomes visible.
     * @param {number} index
     */
    function addTab(index) {
        const addBtnLi = document.getElementById('translation-add-tab');
        const li       = createTabItem(index, gettext('New Language'), true);
        nav.insertBefore(li, addBtnLi);
        bindTabEvents(li);
        bindLabelSync(index);

        const tabLink = li.querySelector('.nav-link');

        // Initialize HugeRTE after the tab is visible to avoid rendering into a hidden element.
        tabLink.addEventListener('shown.bs.tab', function () {
            const textarea = document.getElementById('id_' + PREFIX + '-' + index + '-content');
            if (!textarea) return;
            const editor = hugerte.get(textarea.id);
            if (editor) {
                editor.show();
            } else {
                initHugerte(textarea);
            }
        }, {once: true});

        new tabler.Tab(tabLink).show();
    }

    /**
     * Initialize the tab UI on page load.
     * Builds tabs for all existing rows, activates the first tab,
     * and wires up the add button and formset:added event.
     */
    function init() {
        if (!group) return;

        let firstTab = null;
        group.querySelectorAll('.inline-related:not(.empty-form)').forEach(function (row) {
            const index     = parseInt(row.id.split('-').pop());
            const hasData   = row.classList.contains('has_original');
            const label     = getLabel(index);
            const useI18n   = nav.dataset.useI18n === 'true';
            const deletable = useI18n && !hasData;

            const addBtnLi = document.getElementById('translation-add-tab');
            const li       = createTabItem(index, label, deletable);
            nav.insertBefore(li, addBtnLi);
            bindTabEvents(li);
            bindLabelSync(index);
            if (firstTab === null) firstTab = li.querySelector('.nav-link');
        });

        if (firstTab) new tabler.Tab(firstTab).show();

        // For tabs rendered on page load, HugeRTE initializes while the tab is hidden
        // and marks itself hidden. Call show() each time a tab becomes visible.
        nav.querySelectorAll('li.nav-item:not(#translation-add-tab) .nav-link').forEach(function (link) {
            link.addEventListener('shown.bs.tab', function () {
                const rowId    = this.getAttribute('href').replace('#', '');
                const textarea = document.querySelector('#' + rowId + ' textarea.hugerte-editor');
                if (!textarea) return;
                const editor = hugerte.get(textarea.id);
                if (editor) editor.show();
            });
        });

        const addBtn = document.getElementById(ADD_BTN_ID);
        if (addBtn) {
            addBtn.addEventListener('click', function (e) {
                e.preventDefault();
                const totalForms = document.getElementById('id_' + PREFIX + '-TOTAL_FORMS');
                if (!totalForms) return;
                if (parseInt(totalForms.value) >= getMaxNum()) return;
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

        // Auto-add the first empty tab when creating a new object (no saved translations yet).
        // Skipped if rows already exist in the DOM, which happens when the form is re-rendered
        // after a validation error — in that case the existing rows should not be duplicated.
        // setTimeout is required because Django's formset JS binds the click handler on .add-row a
        // synchronously after this script runs. Without the delay, the click fires before the
        // handler is attached and nothing happens. setTimeout(fn, 0) defers execution until the
        // current call stack is fully cleared, by which point all scripts have finished initializing.
        const initialForms    = document.getElementById('id_' + PREFIX + '-INITIAL_FORMS');
        const hasExistingRows = group.querySelectorAll('.inline-related:not(.empty-form)').length > 0;
        if (initialForms && parseInt(initialForms.value) === 0 && !hasExistingRows) {
            setTimeout(function () {
                const nativeAdd = group.querySelector('.add-row a');
                if (nativeAdd) nativeAdd.click();
            }, 0);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();