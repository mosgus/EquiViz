// Renders the current portfolio table on portfolio.html and wires edit/save/download actions
// Fetch and render the current portfolio table
document.addEventListener('DOMContentLoaded', () => {
    const tableContainer = document.getElementById('portfolioTable');
    const meta = document.getElementById('portfolioMeta');
    const errorBox = document.getElementById('portfolioError');
    const saveBtn = document.querySelector('.save-btn');
    const editBtn = document.querySelector('.edit-btn');
    const editModal = document.getElementById('editModal');
    const editTextarea = document.getElementById('editTextarea');
    const editSubmit = document.getElementById('editSubmit');
    const editError = document.getElementById('editError');

    const showError = (msg) => {
        if (errorBox) {
            errorBox.textContent = msg;
            errorBox.style.display = 'block';
        }
    };

    const clearError = () => {
        if (errorBox) errorBox.style.display = 'none';
    };

    const renderTable = ({ columns, rows, total_rows, truncated }) => {
        if (!tableContainer) return;
        tableContainer.innerHTML = '';

        const table = document.createElement('table');
        table.className = 'portfolio-grid';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        columns.forEach((col) => {
            const th = document.createElement('th');
            th.textContent = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        rows.forEach((row, idx) => {
            const tr = document.createElement('tr');
            row.forEach((cell, cellIdx) => {
                const td = document.createElement('td');
                const colName = columns[cellIdx];
                td.textContent = cell;
                if (colName === 'Return' || colName === 'Return %') {
                    const num = parseFloat(String(cell).replace(/[^-0-9.]/g, ''));
                    if (!isNaN(num)) {
                        if (num > 0) td.classList.add('pos');
                        else if (num < 0) td.classList.add('neg');
                        else td.classList.add('neutral');
                    }
                }
                tr.appendChild(td);
            });
            if (row[0] === 'Net Total') {
                tr.classList.add('net-row');
            }
            tbody.appendChild(tr);

            // Insert an ... row if truncated and we're after the 5th entry
            if (truncated && idx === 4) {
                const ellipsis = document.createElement('tr');
                const td = document.createElement('td');
                td.colSpan = columns.length;
                td.className = 'ellipsis-row';
                td.textContent = '...';
                ellipsis.appendChild(td);
                tbody.appendChild(ellipsis);
            }
        });
        table.appendChild(tbody);

        tableContainer.appendChild(table);

        if (meta) {
            meta.textContent = truncated
                ? `Showing first 5 and last 5 of ${total_rows} rows`
                : `Showing ${total_rows} row(s)`;
        }
    };

    const loadPortfolio = async () => {
        clearError();
        if (meta) meta.textContent = '';
        if (tableContainer) tableContainer.innerHTML = '';

        try {
            const res = await fetch('/current-portfolio');
            const data = await res.json();
            if (!res.ok || !data.success) {
                showError(data.error || 'Unable to load portfolio.');
                return;
            }
            renderTable(data);
        } catch (err) {
            console.error(err);
            showError('Unable to load portfolio.');
        }
    };

    const downloadPortfolio = async () => {
        try {
            const res = await fetch('/download-current');
            if (!res.ok) {
                const data = await res.json().catch(() => ({}));
                showError(data.error || 'Unable to download portfolio.');
                return;
            }
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            const filename = res.headers.get('Content-Disposition')?.split('filename=')?.[1]?.replace(/"/g, '') || 'portfolio.csv';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
            showError('Unable to download portfolio.');
        }
    };

    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const confirmed = window.confirm('Download CSV file of portfolio?');
            if (!confirmed) return;
            await downloadPortfolio();
        });
    }

    const showEditError = (msg) => {
        if (editError) {
            editError.textContent = msg;
            editError.style.display = 'block';
        } else {
            alert(msg);
        }
    };

    const clearEditError = () => {
        if (editError) editError.style.display = 'none';
    };

    const loadRawPortfolio = async () => {
        clearEditError();
        if (editTextarea) editTextarea.value = '';
        try {
            const res = await fetch('/current-portfolio/raw');
            const data = await res.json();
            if (!res.ok || !data.success) {
                showEditError(data.error || 'Unable to load portfolio.');
                return false;
            }
            if (editTextarea) editTextarea.value = data.text || '';
            return true;
        } catch (err) {
            console.error(err);
            showEditError('Unable to load portfolio.');
            return false;
        }
    };

    const openEditModal = async () => {
        const ok = await loadRawPortfolio();
        if (!ok) return;
        if (editModal) editModal.classList.add('show');
    };

    const closeEditModal = () => {
        if (editModal) editModal.classList.remove('show');
    };

    if (editBtn) {
        editBtn.addEventListener('click', openEditModal);
    }

    if (editModal) {
        editModal.addEventListener('click', (e) => {
            if (e.target === editModal) {
                closeEditModal();
            }
        });
        const closeX = editModal.querySelector('.close');
        if (closeX) {
            closeX.addEventListener('click', closeEditModal);
        }
    }

    const submitEdit = async () => {
        clearEditError();
        const text = editTextarea ? editTextarea.value : '';
        if (!text.trim()) {
            showEditError('Please provide portfolio CSV content.');
            return;
        }
        try {
            const res = await fetch('/update-portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ csv_text: text })
            });
            const data = await res.json();
            if (!res.ok || !data.success) {
                showEditError(data.error || 'Could not update portfolio.');
                return;
            }
            closeEditModal();
            await loadPortfolio();
        } catch (err) {
            console.error(err);
            showEditError('Could not update portfolio.');
        }
    };

    if (editSubmit) {
        editSubmit.addEventListener('click', submitEdit);
    }

    loadPortfolio();
});
