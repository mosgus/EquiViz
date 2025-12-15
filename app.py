import sys
from pathlib import Path

import csv
import io
from io import TextIOWrapper
import shutil
from typing import List, Dict
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"

# Make sure backend is importable
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.postPort import validate_portfolio_input, save_portfolio, _slugify_name
from backend.getStonks import update_current_portfolio_data

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

    try:
        update_current_portfolio_data()
    except Exception as e:
        return jsonify({"success": False, "error": f"Portfolio saved but failed to initialize data: {e}"}), 500

    return jsonify({
        "success": True,
        "message": message,
        "path": str(saved_path)
    }), 200


@app.route('/upload-portfolio', methods=['POST'])
def upload_portfolio():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected."}), 400

    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.csv'):
        return jsonify({"success": False, "error": "Only CSV files are supported."}), 400

    # Validate CSV header
    try:
        file.stream.seek(0)
        wrapper = TextIOWrapper(file.stream, encoding='utf-8', newline='')
        reader = csv.reader(wrapper)
        header = next(reader, [])
        expected = ["Asset", "Quantity", "Date Acquired"]
        normalized = [h.strip() for h in header]
        if normalized != expected:
            return jsonify({"success": False, "error": "CSV has incorrect format."}), 400
    except Exception:
        return jsonify({"success": False, "error": "CSV has incorrect format."}), 400
    finally:
        file.stream.seek(0)

    dest_dir = BACKEND_DIR / "current_portfolio"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Clear previous uploads
    for item in dest_dir.iterdir():
        if item.is_file():
            item.unlink()

    dest_path = dest_dir / filename
    try:
        file.save(dest_path)
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to save file: {e}"}), 500

    try:
        update_current_portfolio_data()
    except Exception as e:
        return jsonify({"success": False, "error": f"Saved file but failed to fetch stock data: {e}"}), 500

    return jsonify({"success": True, "message": "Portfolio uploaded.", "path": str(dest_path)}), 200


@app.route('/saved-portfolios', methods=['GET'])
def saved_portfolios():
    saved_dir = BACKEND_DIR / "saved_portfolios"
    saved_dir.mkdir(parents=True, exist_ok=True)
    portfolios = []
    for f in saved_dir.glob("*.csv"):
        if f.is_file():
            portfolios.append(f.stem)
    return jsonify({"success": True, "portfolios": portfolios}), 200


@app.route('/select-portfolio', methods=['POST'])
def select_portfolio():
    data = request.json or {}
    name = (data.get('name') or "").strip()
    if not name:
        return jsonify({"success": False, "error": "Portfolio name is required."}), 400

    safe_name = _slugify_name(name)
    if not safe_name:
        return jsonify({"success": False, "error": "Invalid portfolio name."}), 400

    saved_dir = BACKEND_DIR / "saved_portfolios"
    source_file = saved_dir / f"{safe_name}.csv"
    if not source_file.exists():
        return jsonify({"success": False, "error": "Portfolio not found."}), 404

    dest_dir = BACKEND_DIR / "current_portfolio"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for item in dest_dir.iterdir():
        if item.is_file():
            item.unlink()

    dest_path = dest_dir / source_file.name
    try:
        shutil.copy2(source_file, dest_path)
        update_current_portfolio_data()
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to load portfolio: {e}"}), 500

    return jsonify({"success": True, "message": "Portfolio loaded.", "path": str(dest_path)}), 200


def _load_current_portfolio() -> Dict:
    current_dir = BACKEND_DIR / "current_portfolio"
    if not current_dir.exists():
        raise FileNotFoundError("No current portfolio found.")

    csv_files = list(current_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No current portfolio found.")

    csv_path = csv_files[0]
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("Portfolio file is empty.")

    header = rows[0]
    data_rows = rows[1:]
    return {"columns": header, "rows": data_rows}


def _current_csv_path() -> Path:
    current_dir = BACKEND_DIR / "current_portfolio"
    current_dir.mkdir(parents=True, exist_ok=True)
    csv_files = list(current_dir.glob("*.csv"))
    if csv_files:
        return csv_files[0]
    return current_dir / "current_portfolio.csv"


def _validate_rows(rows: list) -> list:
    validated = []
    for idx, row in enumerate(rows, start=1):
        if len(row) != 3:
            raise ValueError(f"Row {idx}: expected 3 columns (Asset, Quantity, Date Acquired).")
        asset, qty, date_str = [c.strip() for c in row]
        if not asset:
            raise ValueError(f"Row {idx}: Asset is required.")
        if len(asset) > 8:
            raise ValueError(f"Row {idx}: Asset ticker too long.")
        try:
            qty_int = int(qty)
            if qty_int <= 0:
                raise ValueError
        except Exception:
            raise ValueError(f"Row {idx}: Quantity must be a positive integer.")
        try:
            date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
            if date_val > datetime.utcnow().date():
                raise ValueError
        except Exception:
            raise ValueError(f"Row {idx}: Date must be YYYY-MM-DD and not in the future.")
        validated.append([asset.upper(), str(qty_int), date_str])
    return validated


@app.route('/current-portfolio/raw', methods=['GET'])
def current_portfolio_raw():
    try:
        csv_path = _current_csv_path()
        if not csv_path.exists():
            return jsonify({"success": False, "error": "No current portfolio found."}), 404
        content = csv_path.read_text(encoding='utf-8')
        return jsonify({"success": True, "text": content, "filename": csv_path.name}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to load portfolio: {e}"}), 500


@app.route('/update-portfolio', methods=['POST'])
def update_portfolio():
    data = request.json or {}
    csv_text = data.get("csv_text", "")
    if not csv_text.strip():
        return jsonify({"success": False, "error": "No data provided."}), 400

    try:
        reader = csv.reader(io.StringIO(csv_text))
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    except Exception:
        return jsonify({"success": False, "error": "Could not parse CSV."}), 400

    if not rows:
        return jsonify({"success": False, "error": "Portfolio is empty."}), 400

    header = [h.strip() for h in rows[0]]
    expected = ["Asset", "Quantity", "Date Acquired"]
    if header != expected:
        return jsonify({"success": False, "error": "Header must be: Asset,Quantity,Date Acquired"}), 400

    try:
        validated_rows = _validate_rows(rows[1:])
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

    csv_path = _current_csv_path()
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(expected)
            writer.writerows(validated_rows)
        update_current_portfolio_data()
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to update portfolio: {e}"}), 500

    return jsonify({"success": True, "message": "Portfolio updated."}), 200


@app.route('/current-portfolio', methods=['GET'])
def current_portfolio():
    try:
        table = _load_current_portfolio()
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to load portfolio: {e}"}), 500

    rows = table["rows"]
    total = len(rows)
    if total <= 10:
        display_rows = rows
    else:
        display_rows = rows[:5] + rows[-5:]

    return jsonify({
        "success": True,
        "columns": table["columns"],
        "rows": display_rows,
        "total_rows": total,
        "truncated": total > 10
    }), 200


@app.route('/download-current', methods=['GET'])
def download_current():
    try:
        current_dir = BACKEND_DIR / "current_portfolio"
        csv_files = list(current_dir.glob("*.csv"))
        if not csv_files:
            return jsonify({"success": False, "error": "No current portfolio found."}), 404
        csv_path = csv_files[0]
    except Exception:
        return jsonify({"success": False, "error": "No current portfolio found."}), 404

    try:
        return send_file(csv_path, as_attachment=True, download_name=csv_path.name)
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to download portfolio: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
