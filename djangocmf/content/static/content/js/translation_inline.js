/**
 * Auto-select the first unused language when a new translation inline row is added.
 * Relies on the Django admin `formset:added` event fired after a new inline row is inserted.
 */
document.addEventListener('formset:added', function (event) {
    const row            = event.target;
    const languageSelect = row.querySelector('select[name$="-language"]');
    if (!languageSelect) return;

    // Collect all language values already selected in other rows
    const used = [...document.querySelectorAll('select[name$="-language"]')]
        .filter(s => s !== languageSelect)
        .map(s => s.value)
        .filter(Boolean);

    // Select the first available unused language
    for (const option of languageSelect.options) {
        if (option.value && !used.includes(option.value)) {
            languageSelect.value = option.value;
            break;
        }
    }
});