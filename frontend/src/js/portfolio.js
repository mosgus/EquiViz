// static/js/portfolio.js

document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.getElementById('createForm');
    const errorMsg = document.getElementById('errorMessage');

    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 1. Gather data
            const payload = {
                name: document.getElementById('portName').value,
                ticker: document.getElementById('portTicker').value,
                quantity: document.getElementById('portQty').value,
                date: document.getElementById('portDate').value
            };

            try {
                // 2. Send to Python Backend
                const response = await fetch('/create-portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (response.ok) {
                    // Success!
                    console.log("Success:", result.message);

                    // Close the modal (we select it here directly)
                    document.getElementById('createModal').classList.remove('show');

                    createForm.reset();
                    alert("Portfolio Created!");
                    window.location.href = "/src/html/portfolio.html";
                } else {
                    // Error from backend
                    if (errorMsg) {
                        errorMsg.textContent = result.error;
                        errorMsg.style.display = 'block';
                    }
                }

            } catch (err) {
                console.error("Connection Error:", err);
                if (errorMsg) {
                    errorMsg.textContent = "Could not connect to server.";
                    errorMsg.style.display = 'block';
                }
            }
        });
    }
});
