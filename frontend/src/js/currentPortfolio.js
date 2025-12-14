// Fetch and render the current portfolio table
document.addEventListener('DOMContentLoaded', () => {
    const tableContainer = document.getElementById('portfolioTable');
    const meta = document.getElementById('portfolioMeta');
    const errorBox = document.getElementById('portfolioError');

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
            row.forEach((cell) => {
                const td = document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);

            // Insert an ellipsis row if truncated and we're after the 5th entry
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
                : `Showing ${total_rows} rows`;
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

    loadPortfolio();
});
