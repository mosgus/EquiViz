// Handles upload/select portfolio actions in index.html and calls backend upload/select endpoints
// Handles portfolio file uploads
document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadFileButton');
    const fileInput = document.getElementById('uploadFileInput');
    const errorBox = document.getElementById('uploadError');
    const uploadModal = document.getElementById('uploadModal');
    const selectBtn = document.getElementById('selectSavedButton');
    const selectModal = document.getElementById('selectModal');
    const selectDropdown = document.getElementById('savedPortfolioSelect');
    const selectSubmit = document.getElementById('selectSubmit');
    const selectError = document.getElementById('selectError');

    const showError = (msg) => {
        if (errorBox) {
            errorBox.textContent = msg;
            errorBox.style.display = 'block';
        } else {
            alert(msg);
        }
    };

    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => {
            if (errorBox) errorBox.style.display = 'none';
            fileInput.value = '';
            fileInput.click();
        });

        fileInput.addEventListener('change', async () => {
            const file = fileInput.files[0];
            if (!file) return;

            if (!file.name.toLowerCase().endsWith('.csv')) {
                showError('Please select a CSV file.');
                fileInput.value = '';
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/upload-portfolio', {
                    method: 'POST',
                    body: formData
                });

                const data = await res.json();
                if (!res.ok || !data.success) {
                    showError(data.error || 'Upload failed. Try again.');
                    return;
                }

                if (uploadModal) uploadModal.classList.remove('show');
                window.location.href = "/src/html/portfolio.html";
            } catch (err) {
                console.error(err);
                showError('Could not upload file. Please try again.');
            }
        });
    }

    const showSelectError = (msg) => {
        if (selectError) {
            selectError.textContent = msg;
            selectError.style.display = 'block';
        } else {
            alert(msg);
        }
    };

    const loadSavedPortfolios = async () => {
        if (selectError) selectError.style.display = 'none';
        if (!selectDropdown) return;

        selectDropdown.innerHTML = '<option value=\"\">-- Select --</option>';

        try {
            const res = await fetch('/saved-portfolios');
            const data = await res.json();
            if (!res.ok || !data.success) {
                showSelectError(data.error || 'Could not load saved portfolios.');
                return;
            }

            if (!data.portfolios || data.portfolios.length === 0) {
                showSelectError('No saved portfolios found.');
                return;
            }

            data.portfolios.forEach((name) => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                selectDropdown.appendChild(opt);
            });
        } catch (err) {
            console.error(err);
            showSelectError('Could not load saved portfolios.');
        }
    };

    if (selectBtn && selectModal) {
        selectBtn.addEventListener('click', async () => {
            await loadSavedPortfolios();
            selectModal.classList.add('show');
        });

        selectModal.addEventListener('click', (e) => {
            if (e.target === selectModal) {
                selectModal.classList.remove('show');
            }
        });
    }

    if (selectSubmit && selectDropdown) {
        selectSubmit.addEventListener('click', async () => {
            if (selectError) selectError.style.display = 'none';
            const selected = selectDropdown.value;
            if (!selected) {
                showSelectError('Please choose a portfolio.');
                return;
            }

            try {
                const res = await fetch('/select-portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: selected })
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    showSelectError(data.error || 'Could not load portfolio.');
                    return;
                }
                if (selectModal) selectModal.classList.remove('show');
                if (uploadModal) uploadModal.classList.remove('show');
                window.location.href = "/src/html/portfolio.html";
            } catch (err) {
                console.error(err);
                showSelectError('Could not load portfolio.');
            }
        });
    }
});
