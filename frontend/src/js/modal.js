// static/js/modal.js

document.addEventListener('DOMContentLoaded', () => {
    const modalConfig = [
        { trigger: '.port_butt', modalId: 'createModal' },
        { trigger: '.upload_butt', modalId: 'uploadModal' },
        { trigger: '#selectSavedButton', modalId: 'selectModal' },
    ];

    const errorMsg = document.getElementById('errorMessage');

    const openModal = (modal) => {
        if (modal) {
            modal.classList.add('show');
            if (errorMsg) errorMsg.style.display = 'none';
        }
    };

    const closeModal = (modal) => {
        if (modal) modal.classList.remove('show');
    };

    modalConfig.forEach(({ trigger, modalId }) => {
        const btn = document.querySelector(trigger);
        const modal = document.getElementById(modalId);

        if (btn && modal) {
            btn.addEventListener('click', () => openModal(modal));

            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    closeModal(modal);
                }
            });
        }
    });

    document.querySelectorAll('.close').forEach((closeBtn) => {
        closeBtn.addEventListener('click', () => {
            const modal = closeBtn.closest('.modal');
            closeModal(modal);
        });
    });
});
