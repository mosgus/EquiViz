import sys
from pathlib import Path

from flask import Flask, request, jsonify, render_template, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"

# Make sure backend is importable
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.postPort import validate_portfolio_input, save_portfolio

# Serve templates and static assets from /frontend
app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path=""  # allow /css/... and /assets/... URLs
)


# Route to serve  HTML file
@app.route('/')
def home():
    return render_template('index.html')


# API endpoint JavaScript will talk to
@app.route('/create-portfolio', methods=['POST'])
def create_portfolio():
    data = request.json

    # Run the validation logic from postPort.py
    is_valid, message = validate_portfolio_input(data)

    if not is_valid:
        # Return error (400 Bad Request)
        return jsonify({"success": False, "error": message}), 400

    try:
        saved_path = save_portfolio(data)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to save current_portfolio: {e}"}), 500

    return jsonify({
        "success": True,
        "message": message,
        "path": str(saved_path)
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
