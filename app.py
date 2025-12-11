from flask import Flask, request, jsonify, send_file, redirect, url_for
import logging
import os
import secrets

app = Flask(__name__)

# ---- Misconfig: verbose logging to a world-readable file ----
LOG_FILE = "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

# ---- Flag & secret key ----
FLAG = os.environ.get("FLAG", "flag{a05_misconfigured_logging_ctf_by_kohar}")
SECRET_API_KEY = "k_" + secrets.token_hex(16)

# Multiple decoy API keys – look very similar to real one
DECOY_KEYS = [
    "k_" + secrets.token_hex(16),
    "k_" + secrets.token_hex(16),
    "k_" + secrets.token_hex(16),
]

# Demo “QA” login for the public login page
DEMO_USER = "tester@kohar-ctf.local"
DEMO_PASS = "TestPassword123!"

# Admin login JUST for the fake admin panel
ADMIN_USER = "admin"
ADMIN_PASS = "abc123"


# --------- UI FRAMEWORK ---------

BASE_HTML_TOP = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kohar's Security Misconfiguration CTF</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f4f4f7; margin:0; padding:0; }
    header { background:#222; color:#fff; padding:10px 20px; }
    header h1 { margin:0; font-size:20px; }
    nav a { color:#fff; margin-right:15px; text-decoration:none; }
    nav a:hover { text-decoration:underline; }
    .container { max-width:900px; margin:20px auto; background:#fff;
                 padding:20px 25px; border-radius:8px; box-shadow:0 0 6px rgba(0,0,0,0.1); }
    .btn { background:#007bff; color:#fff; border:none; padding:8px 14px; border-radius:4px; cursor:pointer; }
    .btn:hover { background:#0056b3; }
    input, textarea { width:100%; padding:8px; margin:6px 0 12px; border-radius:4px; border:1px solid #ccc; }
    table { border-collapse: collapse; width:100%; margin-top:10px; }
    th, td { border:1px solid #ccc; padding:6px 8px; font-size:14px; }
    th { background:#f0f0f0; }
    footer { text-align:center; color:#777; font-size:12px; margin:20px 0; }
  </style>
</head>
<body>
<header>
  <h1>Kohar's Security Misconfiguration CTF Portal</h1>
  <nav>
    <a href="/">Home</a>
    <a href="/login">Login</a>
    <a href="/admin">Admin</a>
    <a href="/docs">API Docs</a>
    <a href="/ticket">Support Ticket</a>
    <a href="/hint">Hints!</a>
  </nav>
</header>
<div class="container">
"""

BASE_HTML_BOTTOM = """
</div>
<footer>Kohar's Security Misconfiguration CTF</footer>
</body>
</html>
"""


@app.route("/")
def index():
    body = """
    <h2>Hello and good luck</h2>
    <p>This is my <strong>Security Misconfiguration CTF</strong>.</p>
    <p>Extract the hidden flag through investigation and exploitation.</p>
    <p>There's def a security issue somewhere... You just gotta find it</p>
    """
    return BASE_HTML_TOP + body + BASE_HTML_BOTTOM


# --------- PUBLIC LOGIN (NO REAL POWER) ---------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Intentional misconfig: log credentials
        logger.info(
            f"Login attempt user={username!r} password={password!r} from {request.remote_addr}"
        )

        if username == DEMO_USER and password == DEMO_PASS:
            return redirect(url_for("dashboard"))

        return BASE_HTML_TOP + "<p>Invalid username or password.</p>" + BASE_HTML_BOTTOM

    body = f"""
    <h2>Login</h2>
    <p>Demo QA Account:</p>
    <ul>
        <li>Email: <code>{DEMO_USER}</code></li>
        <li>Password: <code>{DEMO_PASS}</code></li>
    </ul>
    <form method="POST">
        <label>Email:</label>
        <input name="username" placeholder="you@kohar-ctf.local">
        <label>Password:</label>
        <input name="password" type="password" placeholder="Password">
        <button class="btn" type="submit">Login</button>
    </form>
    """
    return BASE_HTML_TOP + body + BASE_HTML_BOTTOM

@app.route("/hint")
def hint():
    body = """
    <h2>Hint</h2>
    <p>If normal pages do not provide enough information, consider what systems
    typically do with errors, logins, API calls, or other events.</p>

    <p>Sometimes internal components produce very <strong>verbose logs</strong>.
    These logs may be intended for maintenance, but not always secured correctly.</p>

    <p>Try exploring the application structure or using common techniques to
    discover <em>unlisted</em> or <em>internal-only</em> paths.</p>
    """
    return BASE_HTML_TOP + body + BASE_HTML_BOTTOM


@app.route("/dashboard")
def dashboard():
    body = """
    <h2>Dashboard</h2>
    <p>Welcome to Kohar Labs. I don't think this page will help...</p>
    <p>Try investigating API logs or documentation for further clues.</p>
    """
    return BASE_HTML_TOP + body + BASE_HTML_BOTTOM


# --------- FAKE ADMIN PANEL (DECOYS ONLY) ---------

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Simple, separate login just for admin panel
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        logger.info(
            f"Admin login attempt user={username!r} password={password!r} from {request.remote_addr}"
        )

        if username == ADMIN_USER and password == ADMIN_PASS:
            # Show decoy API keys, not the real one
            keys_rows = "".join(
                f"<tr><td>service-{i}</td><td>{key}</td><td>active</td></tr>"
                for i, key in enumerate(DECOY_KEYS, start=1)
            )
            body = f"""
            <h2>Admin Control Panel</h2>
            <p>API key management for internal services.</p>
            <table>
              <tr><th>Service</th><th>API Key</th><th>Status</th></tr>
              {keys_rows}
            </table>
            <p style="margin-top:15px;color:#888;">
              Note: Legacy keys rotated automatically. Logs will contain more details.
            </p>
            """
            # Log that admin viewed these (noise)
            logger.info(
                f"Admin viewed API key list: {[k for k in DECOY_KEYS]!r} from {request.remote_addr}"
            )
            return BASE_HTML_TOP + body + BASE_HTML_BOTTOM

        # Fail
        return BASE_HTML_TOP + "<p>Invalid admin credentials.</p>" + BASE_HTML_BOTTOM

    # GET = login form
    body = """
    <h2>Admin Login</h2>
    <p>Authorized personnel only.</p>
    <form method="POST">
        <label>Username:</label>
        <input name="username" placeholder="admin">
        <label>Password:</label>
        <input name="password" type="password" placeholder="********">
        <button class="btn" type="submit">Login</button>
    </form>
    """
    return BASE_HTML_TOP + body + BASE_HTML_BOTTOM


# --------- API DOCS & TICKET ---------

@app.route("/docs")
def docs():
    body = """
    <h2>Kohar's API Documentation</h2>
    <h3>GET /api/data</h3>
    <p>This endpoint returns internal challenge data including, potentially, secrets.</p>
    <p>Requires HTTP header <code>X-API-KEY</code> with a valid authentication key.</p>
    <pre>
curl -H "X-API-KEY: &lt;your-key&gt;" http://HOST:5000/api/data
    </pre>
    <p>Keys are distributed to authorized systems only or maybe leaked????</p>
    """
    return BASE_HTML_TOP + body + BASE_HTML_BOTTOM


@app.route("/ticket", methods=["GET", "POST"])
def ticket():
    if request.method == "POST":
        email = request.form.get("email", "")
        subject = request.form.get("subject", "")
        description = request.form.get("description", "")

        # Misconfigured logging: logs everything
        logger.info(
            f"Ticket submitted email={email!r} subject={subject!r} "
            f"description={description!r} ip={request.remote_addr}"
        )

        return BASE_HTML_TOP + "<p>Ticket submitted successfully.</p>" + BASE_HTML_BOTTOM

    body = """
    <h2>Submit Support Ticket</h2>
    <p>Enter an issue and it may or may not help. Maybe if you login it may help?</p>
    <form method="POST">
        <label>Your email:</label>
        <input name="email">

        <label>Subject:</label>
        <input name="subject">

        <label>Description:</label>
        <textarea name="description" rows="5"></textarea>

        <button class="btn" type="submit">Submit Ticket</button>
    </form>
    """
    return BASE_HTML_TOP + body + BASE_HTML_BOTTOM


# --------- REAL API ENDPOINT ---------

@app.route("/api/data")
def api_data():
    headers_dict = dict(request.headers)
    logger.debug(f"/api/data request from {request.remote_addr} headers={headers_dict!r}")

    api_key = request.headers.get("X-API-KEY", "")

    if api_key == SECRET_API_KEY:
        return jsonify({
            "message": "Valid API key accepted.",
            "challenge_status": "operational",
            "flag": FLAG
        })

    # Make invalid attempts noisy; if they hit a decoy, make it extra noisy
    if api_key in DECOY_KEYS:
        logger.warning(
            f"Deprecated API key used: {api_key!r} from {request.remote_addr} "
            f"(key marked as revoked in admin panel)"
        )
    else:
        logger.warning(f"Invalid API key attempt: {api_key!r} from {request.remote_addr}")

    return jsonify({"error": "Invalid API key"}), 403


# --------- MISCONFIGURED LOG EXPOSURE ---------

@app.route("/_internal/maintenance/logs")
def debug_logs():
    """
    Forgotten internal maintenance endpoint.
    No authentication, reveals sensitive logs.
    """
    if not os.path.exists(LOG_FILE):
        return "Log file not found", 404
    return send_file(LOG_FILE, mimetype="text/plain")


# --------- STARTUP SEED LOGS ---------

if __name__ == "__main__":
    logger.info("Kohar Labs system startup sequence initiated.")
    logger.warning("Deprecated authentication module still active.")

    # Log some decoy key usage to create noise
    for i, key in enumerate(DECOY_KEYS, start=1):
        logger.info(
            f"Legacy service srv-{i} called /api/data with X-API-KEY={key!r} "
            f"from 10.0.0.{i} (status=403, key_revoked=True)"
        )

    # Log ONE real key usage – this is the true leak
    logger.info(
        f"Kohar System Agent accessed /api/data using X-API-KEY={SECRET_API_KEY!r} "
        f"from 10.0.0.250 (status=200)"
    )

    # Use PORT env var if provided (Render/other PaaS)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
