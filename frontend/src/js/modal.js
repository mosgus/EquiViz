// static/js/modal.js

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('createModal');
    const createBtn = document.querySelector('.port_butt');
    const closeBtn = document.querySelector('.close');
    const errorMsg = document.getElementById('errorMessage');

    if (createBtn) {
        createBtn.addEventListener('click', () => {
            modal.classList.add('show');
            if (errorMsg) errorMsg.style.display = 'none'; // Reset error state
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('show');
        });
    }

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
});