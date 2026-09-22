from flask import Flask, jsonify, redirect, render_template_string, request, url_for

from .config import settings
from .db import get_tag_by_uid, list_tags, record_event, upsert_tag
from .spotify_service import dispatch_tag_value

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TapTune</title>
  <style>
    :root {
      --bg: #f5f7ff;
      --panel: rgba(255,255,255,0.9);
      --panel-border: rgba(148,163,184,0.25);
      --text: #1e293b;
      --muted: #64748b;
      --primary: #6d5efc;
      --primary-dark: #5647e5;
      --accent: #14b8a6;
      --action: #f59e0b;
      --success-bg: #ecfdf5;
      --success-border: #a7f3d0;
      --success-text: #065f46;
      --shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 32px 18px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #eef2ff 0%, var(--bg) 35%, #edf6ff 100%);
      color: var(--text);
    }

    .app-shell {
      width: min(980px, 100%);
      display: grid;
      gap: 22px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 4px 6px;
    }

    .title {
      font-size: clamp(2.2rem, 3vw, 3rem);
      line-height: 1.05;
      font-weight: 800;
      letter-spacing: -0.06em;
      margin: 0;
    }

    .subtitle {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 1rem;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 0.55rem 0.9rem;
      border-radius: 999px;
      background: rgba(109, 94, 252, 0.12);
      color: var(--primary-dark);
      font-weight: 700;
      letter-spacing: 0.02em;
      font-size: 0.8rem;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }

    .form-panel {
      padding: clamp(1.2rem, 3vw, 2rem);
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px;
    }

    .field {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .field label {
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--muted);
    }

    input {
      width: 100%;
      padding: 0.9rem 1rem;
      border-radius: 14px;
      border: 1px solid rgba(148,163,184,0.6);
      background: rgba(255,255,255,0.9);
      color: var(--text);
      font-size: 1rem;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    input:focus {
      outline: none;
      border-color: rgba(109, 94, 252, 0.8);
      box-shadow: 0 0 0 4px rgba(109, 94, 252, 0.12);
    }

    .helper-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 0 0 18px;
    }

    .helper-button {
      border: 1px solid rgba(109, 94, 252, 0.2);
      background: rgba(109, 94, 252, 0.08);
      color: var(--primary-dark);
      border-radius: 999px;
      padding: 0.58rem 0.9rem;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.15s ease, background 0.15s ease;
    }

    .helper-button:hover {
      transform: translateY(-1px);
      background: rgba(109, 94, 252, 0.12);
    }

    .actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 22px;
    }

    .save-button {
      border: none;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
      color: white;
      padding: 0.9rem 1.3rem;
      border-radius: 12px;
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 12px 25px rgba(109, 94, 252, 0.28);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .save-button:hover {
      transform: translateY(-1px);
      box-shadow: 0 16px 28px rgba(109, 94, 252, 0.32);
    }

    .success-banner {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 0.85rem 1rem;
      border: 1px solid var(--success-border);
      border-radius: 12px;
      background: var(--success-bg);
      color: var(--success-text);
      font-weight: 600;
    }

    .tags-panel {
      padding: 1.5rem 1.2rem 1.1rem;
    }

    .section-title {
      margin: 0 0 16px;
      font-size: 1.2rem;
      font-weight: 800;
      letter-spacing: -0.04em;
    }

    .tag-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .tag-card {
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 16px 14px;
      border-radius: 16px;
      background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(248,250,252,0.9));
      border: 1px solid rgba(148,163,184,0.22);
    }

    .tag-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    .pill {
      display: inline-flex;
      align-items: center;
      padding: 0.3rem 0.6rem;
      border-radius: 999px;
      font-weight: 700;
      letter-spacing: 0.04em;
    }

    .pill.content {
      background: rgba(20,184,166,0.12);
      color: #0f766e;
    }

    .pill.action {
      background: rgba(245, 158, 11, 0.12);
      color: #a16207;
    }

    .tag-uid {
      font-weight: 800;
      font-size: 1rem;
      word-break: break-all;
    }

    .tag-value {
      font-size: 0.95rem;
      color: var(--text);
      word-break: break-all;
      line-height: 1.5;
    }

    .tag-label {
      color: var(--muted);
      font-size: 0.9rem;
      font-style: italic;
    }

    .empty-state {
      padding: 1rem 0.5rem;
      text-align: center;
      color: var(--muted);
      background: rgba(148,163,184,0.05);
      border-radius: 14px;
      border: 1px dashed rgba(148,163,184,0.4);
    }

    @media (max-width: 640px) {
      .header {
        flex-direction: column;
        align-items: flex-start;
      }

      .actions {
        justify-content: stretch;
      }

      .save-button {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <header class="header">
      <div>
        <h1 class="title">TapTune</h1>
        <p class="subtitle">Assign playlists and shortcuts to your NFC tags.</p>
      </div>
      <span class="badge">Ready to map</span>
    </header>

    <main class="panel form-panel">
      {% if saved %}
        <div class="success-banner" role="status">✓ Tag saved successfully.</div>
      {% endif %}

      <div class="helper-row">
        <button type="button" class="helper-button" data-value="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M">Spotify playlist</button>
        <button type="button" class="helper-button" data-value="action:play_pause">Play / pause</button>
        <button type="button" class="helper-button" data-value="action:next_track">Next track</button>
      </div>

      <form method="post" action="/assign">
        <div class="form-grid">
          <div class="field">
            <label for="uid">Tag UID</label>
            <input id="uid" name="uid" required placeholder="e.g. 04A7B2F1">
          </div>

          <div class="field">
            <label for="label">Friendly label</label>
            <input id="label" name="label" placeholder="e.g. Morning playlist">
          </div>

          <div class="field" style="grid-column: 1 / -1;">
            <label for="value">Spotify URI / Action</label>
            <input id="value" name="value" required placeholder="spotify:playlist:... or action:play_pause">
          </div>
        </div>

        <div class="actions">
          <button class="save-button" type="submit">Save tag</button>
        </div>
      </form>
    </main>

    <section class="panel tags-panel">
      <h2 class="section-title">Assigned tags</h2>
      <ul class="tag-list">
        {% for tag in tags %}
          <li class="tag-card">
            <div class="tag-meta">
              <span class="pill {{ tag.tag_type }}">{{ tag.tag_type }}</span>
              <span>{{ tag.uid }}</span>
            </div>
            <div class="tag-uid">{{ tag.uid }}</div>
            <div class="tag-value">{{ tag.value }}</div>
            {% if tag.label %}<div class="tag-label">{{ tag.label }}</div>{% endif %}
          </li>
        {% else %}
          <li class="empty-state">No tags assigned yet.</li>
        {% endfor %}
      </ul>
    </section>
  </div>

  <script>
    document.querySelectorAll('[data-value]').forEach((button) => {
      button.addEventListener('click', () => {
        const input = document.getElementById('value');
        input.value = button.dataset.value;
        input.focus();
      });
    });
  </script>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template_string(HTML, tags=list_tags(), saved=request.args.get("saved") == "1")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "app": "TapTune"})

    @app.post("/assign")
    def assign_tag():
        uid = (request.form.get("uid") or "").strip()
        value = (request.form.get("value") or "").strip()
        label = (request.form.get("label") or "").strip() or None

        if not uid or not value:
            return jsonify({"error": "uid and value are required"}), 400

        if value.startswith("spotify:"):
            tag_type = "content"
        elif value.startswith("action:"):
            tag_type = "action"
        else:
            tag_type = "content"

        tag = upsert_tag(uid=uid, value=value, tag_type=tag_type, label=label)
        return redirect(url_for("index", saved=1))

    @app.post("/dispatch")
    def dispatch_tag():
        uid = (request.form.get("uid") or "").strip()
        value = (request.form.get("value") or "").strip()

        if not uid and not value:
            return jsonify({"error": "uid or value required"}), 400

        if uid:
            tag = get_tag_by_uid(uid)
            if not tag:
                return jsonify({"error": "Unknown tag"}), 404
            value = tag["value"]

        record_event(uid or "simulated", "content" if value.startswith("spotify:") else "action", value, source="web")
        result = dispatch_tag_value(value)
        return jsonify({"status": "ok", "result": result})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=False)
