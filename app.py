"""
app.py
------
Phase 2: Flask Backend Web Server — Personal Finance Planner
-------------------------------------------------------------
Routes:
    GET  /              -> Serves the main HTML interface
    POST /api/upload    -> Accepts CSV file, parses expenses, returns summary
    POST /api/chat      -> Accepts user question, returns AI agent response
    GET  /api/status    -> Returns current session state (data loaded, message count)
    POST /api/reset     -> Clears conversation history for the current session
    GET  /api/summary   -> Returns the current expense summary as JSON

Run:
    python app.py           (debug mode on port 5000)
    flask run               (production-like)
"""

import os
import csv
import io
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv

from finance_agent import FinanceAgent

# ── Environment & App Setup ───────────────────────────────────────────────────
load_dotenv()

app = Flask(__name__)

# Secret key required for session management
app.secret_key = os.getenv("FLASK_SECRET_KEY", "finance-planner-dev-secret-2024")

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Agent Store ───────────────────────────────────────────────────────────────
# Dictionary mapping session_id -> FinanceAgent instance.
# Each browser session gets its own isolated agent so multiple users
# do not share expense data.
_agents: dict[str, FinanceAgent] = {}


def get_agent() -> FinanceAgent:
    """
    Return the FinanceAgent for the current browser session.
    Creates a new agent if none exists yet.
    """
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        logger.info("New session created: %s", session["session_id"])

    sid = session["session_id"]
    if sid not in _agents:
        _agents[sid] = FinanceAgent()
        logger.info("New FinanceAgent created for session %s", sid)

    return _agents[sid]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_csv_from_file(file_storage) -> tuple[list[dict], str | None]:
    """
    Read an uploaded FileStorage object, validate columns, and return
    a list of parsed expense row dicts.

    Returns:
        (rows, error_message)  — error_message is None on success.
    """
    REQUIRED = {"date", "amount", "category", "description"}

    try:
        content = file_storage.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], "File encoding not supported. Please save your CSV as UTF-8."

    reader = csv.DictReader(io.StringIO(content))

    if reader.fieldnames is None:
        return [], "CSV file appears to be empty."

    normalised_fields = {col.strip().lower() for col in reader.fieldnames}
    missing = REQUIRED - normalised_fields
    if missing:
        return [], (
            f"CSV is missing required columns: {', '.join(sorted(missing))}. "
            "Required columns: date, amount, category, description."
        )

    rows = []
    skipped = 0
    detected_currency = "$"  # default fallback
    currency_found = False

    CURRENCY_MAP = [
        ("₹", "₹"), ("£", "£"), ("€", "€"), ("¥", "¥"),
        ("₩", "₩"), ("₫", "₫"), ("₺", "₺"), ("₴", "₴"),
        ("Fr", "Fr"), ("kr", "kr"), ("$", "$"),
    ]

    for line_num, raw_row in enumerate(reader, start=2):
        row = {k.strip().lower(): (v or "").strip() for k, v in raw_row.items() if k}

        # Parse amount — strip common currency symbols
        raw_amount = row.get("amount", "")

        # Auto-detect currency from first recognisable symbol in the file
        if not currency_found:
            for symbol, label in CURRENCY_MAP:
                if symbol in raw_amount:
                    detected_currency = label
                    currency_found = True
                    break

        try:
            amt_str = (
                raw_amount
                .replace(",", "")
                .replace("$", "")
                .replace("£", "")
                .replace("€", "")
                .replace("₹", "")
                .replace("¥", "")
                .replace("₩", "")
                .replace("₫", "")
                .replace("₺", "")
                .replace("₴", "")
                .replace("Fr", "")
                .replace("kr", "")
                .strip()
            )
            amount = float(amt_str)
        except ValueError:
            logger.warning("Skipping row %d: invalid amount '%s'", line_num, row.get("amount"))
            skipped += 1
            continue

        rows.append(
            {
                "date": None,          # parsed inside FinanceAgent
                "date_str": row["date"],
                "amount": amount,
                "category": row["category"].title(),
                "description": row["description"],
            }
        )

    if not rows:
        return [], "$", f"No valid rows found in CSV. {skipped} rows were skipped due to invalid data."

    return rows, detected_currency, None


def _error(message: str, status: int = 400):
    """Return a JSON error response."""
    logger.warning("API error %d: %s", status, message)
    return jsonify({"success": False, "error": message}), status


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main HTML interface."""
    logger.info("Serving index page")
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    """
    Handle CSV file uploads.

    Accepts: multipart/form-data with field name 'file'
    Returns JSON:
        success: true  -> { success, message, expense_count, summary }
        success: false -> { success, error }
    """
    # ── Validate request ─────────────────────────────────────────────
    if "file" not in request.files:
        return _error("No file field in request. Send file as form-data field named 'file'.")

    file = request.files["file"]

    if file.filename == "":
        return _error("No file selected.")

    filename = file.filename.lower()
    if not filename.endswith(".csv"):
        return _error("Only CSV (.csv) files are accepted.")

    logger.info("Upload request received: %s", file.filename)

    # ── Save file to uploads folder ──────────────────────────────────
    safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    file.seek(0)
    file.save(save_path)
    logger.info("File saved: %s", save_path)

    # ── Parse CSV ────────────────────────────────────────────────────
    file.seek(0)
    rows, currency_symbol, err = _parse_csv_from_file(file)
    if err:
        return _error(err)

    # ── Load into agent ──────────────────────────────────────────────
    agent = get_agent()
    result = agent.load_from_rows(rows, currency_symbol=currency_symbol)

    if not result["success"]:
        return _error(result["message"])

    logger.info(
        "Session %s: loaded %d expenses from '%s'",
        session.get("session_id"), result["expense_count"], file.filename,
    )

    return jsonify(
        {
            "success": True,
            "message": result["message"],
            "expense_count": result["expense_count"],
            "summary": result["summary"],
            "currency_symbol": currency_symbol,
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Process a user question and return the AI agent's response.

    Accepts JSON: { "message": "your question here" }
    Returns JSON:
        success: true  -> { success, response, message_count }
        success: false -> { success, error }
    """
    # ── Validate request ─────────────────────────────────────────────
    data = request.get_json(silent=True)
    if not data:
        return _error("Request body must be JSON with a 'message' field.")

    question = data.get("message", "").strip()
    if not question:
        return _error("'message' field is empty.")

    if len(question) > 2000:
        return _error("Message too long. Please keep questions under 2000 characters.")

    logger.info("Chat request — Q: %.80s...", question)

    # ── Ask the agent ─────────────────────────────────────────────────
    agent = get_agent()

    if not agent.expenses:
        return jsonify(
            {
                "success": False,
                "error": "no_data",
                "message": "Please upload a CSV expense file first before asking questions.",
            }
        ), 400

    try:
        answer = agent.ask_agent(question)
        message_count = len(agent.conversation_history) // 2  # pairs of user/assistant

        logger.info("Chat response — %d chars, turn %d", len(answer), message_count)

        return jsonify(
            {
                "success": True,
                "response": answer,
                "message_count": message_count,
            }
        )

    except RuntimeError as exc:
        return _error(f"AI error: {exc}", status=502)

    except Exception as exc:
        logger.exception("Unexpected error in /api/chat")
        return _error(f"Unexpected server error: {exc}", status=500)


@app.route("/api/status", methods=["GET"])
def status():
    """
    Return current session state.

    Returns JSON: { data_loaded, expense_count, message_count, date_range }
    """
    agent = get_agent()
    s = agent.get_summary()

    return jsonify(
        {
            "data_loaded": bool(agent.expenses),
            "expense_count": s.get("expense_count", 0),
            "message_count": len(agent.conversation_history) // 2,
            "date_range": s.get("date_range", ""),
            "total_amount": s.get("total_amount", 0),
            "currency_symbol": agent.currency_symbol,
        }
    )


@app.route("/api/summary", methods=["GET"])
def summary():
    """
    Return the full expense summary JSON for the current session.
    """
    agent = get_agent()

    if not agent.expenses:
        return _error("No expense data loaded yet.", 404)

    return jsonify({"success": True, "summary": agent.get_summary()})


@app.route("/api/reset", methods=["POST"])
def reset():
    """
    Clear conversation history for the current session (keeps expense data).
    """
    agent = get_agent()
    agent.reset_conversation()
    logger.info("Session %s: conversation reset", session.get("session_id"))
    return jsonify({"success": True, "message": "Conversation history cleared."})


# ── Error Handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed."}), 405


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"success": False, "error": "File too large. Maximum size is 5 MB."}), 413


@app.errorhandler(500)
def internal_error(e):
    logger.exception("Internal server error")
    return jsonify({"success": False, "error": "Internal server error."}), 500


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Personal Finance Planner - Flask Backend (Phase 2)")
    print("=" * 60)
    print(f"  Upload folder : {UPLOAD_FOLDER}")
    print(f"  Server        : http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
