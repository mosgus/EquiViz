import sys
from pathlib import Path

from flask import Flask, request, jsonify, render_template, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"

# Make sure backend is importable
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.postPort import validate_portfolio_input

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

    # Logic to actually SAVE the portfolio to a database/file would go here

    return jsonify({"success": True, "message": message}), 200


# Serve favicon for browsers that request /favicon.ico (and iOS touch icons)
@app.route('/favicon.ico')
def favicon():
    # prefer .ico for browser compatibility
    ico_path = FRONTEND_DIR / "assets" / "favicon.ico"
    return send_from_directory(ico_path.parent, ico_path.name)


@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-precomposed.png')
def apple_icon():
    png_path = FRONTEND_DIR / "assets" / "favicon.png"
    return send_from_directory(png_path.parent, png_path.name)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
