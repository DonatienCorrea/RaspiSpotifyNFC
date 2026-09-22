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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --paper: #f4f1e8;
      --paper-deep: #e8e3d5;
      --ink: #182027;
      --muted: #5c635f;
      --line: #c9c5b9;
      --blue: #1945e8;
      --blue-dark: #1232aa;
      --orange: #f06328;
      --green: #20734f;
      --white: #fbfaf5;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      padding: 0 0 88px;
      font-family: "DM Sans", sans-serif;
      line-height: 1.55;
      background: var(--paper);
      color: var(--ink);
      -webkit-font-smoothing: antialiased;
    }

    .app-shell {
      width: min(1160px, calc(100% - 64px));
      margin: 0 auto;
      display: grid;
      gap: 0;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      min-height: 82px;
      padding: 0;
      border-bottom: 1px solid var(--line);
    }

    .title {
      font-family: "Space Grotesk", sans-serif;
      font-size: clamp(2.8rem, 7vw, 6.5rem);
      line-height: .9;
      font-weight: 600;
      letter-spacing: -0.065em;
      margin: 0;
    }

    .subtitle {
      margin: 18px 0 0;
      color: var(--muted);
      font-size: 1.1rem;
      max-width: 500px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 0;
      border-radius: 0;
      background: transparent;
      color: var(--blue);
      font: 500 11px "DM Mono", monospace;
      letter-spacing: .13em;
      text-transform: uppercase;
    }

    .panel {
      background: transparent;
      border: 0;
      border-radius: 0;
      box-shadow: none;
      backdrop-filter: none;
    }

    .form-panel {
      padding: 92px 0 110px;
      border-bottom: 1px solid var(--line);
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px 28px;
      max-width: 780px;
    }

    .field {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .field:last-child {
      grid-column: 1 / -1;
    }

    .field label {
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--muted);
      font: 500 11px "DM Mono", monospace;
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    input {
      width: 100%;
      padding: 0.9rem 0.85rem;
      border-radius: 0;
      border: 1px solid var(--ink);
      background: var(--white);
      color: var(--ink);
      font: 500 13px "DM Mono", monospace;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    input:focus {
      outline: none;
      border-color: var(--blue);
      box-shadow: 4px 4px 0 var(--orange);
    }

    .helper-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin: 0 0 30px;
    }

    .helper-button {
      border: 1px solid var(--ink);
      background: transparent;
      color: var(--ink);
      border-radius: 0;
      padding: 0.65rem 0.8rem;
      font: 600 12px "DM Sans", sans-serif;
      cursor: pointer;
      transition: transform .2s ease, background-color .2s ease, color .2s ease;
    }

    .helper-button:hover {
      transform: translateY(-2px);
      background: var(--ink);
      color: var(--white);
    }

    .actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 28px;
    }

    .save-button {
      border: 1px solid transparent;
      background: var(--blue);
      color: var(--white);
      padding: 14px 18px;
      border-radius: 0;
      font: 700 13px "DM Sans", sans-serif;
      cursor: pointer;
      transition: transform .2s ease, background-color .2s ease;
    }

    .save-button:hover {
      transform: translateY(-2px);
      background: var(--blue-dark);
    }

    .success-banner {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 0.85rem 1rem;
      border: 1px solid var(--green);
      border-radius: 0;
      background: transparent;
      color: var(--green);
      font: 500 12px "DM Mono", monospace;
      margin-bottom: 26px;
    }

    .tags-panel {
      padding: 80px 0 0;
    }

    .section-title {
      margin: 0 0 24px;
      font: 600 clamp(2rem, 4vw, 3.4rem)/.95 "Space Grotesk", sans-serif;
      letter-spacing: -.065em;
    }

    .tag-list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 0;
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .tag-card {
      display: grid;
      grid-template-columns: 120px minmax(0, 1fr) minmax(0, 1.5fr) minmax(120px, .7fr);
      align-items: center;
      gap: 18px;
      padding: 18px 0;
      border-radius: 0;
      background: transparent;
      border-top: 1px solid var(--line);
    }

    .tag-meta {
      display: flex;
      justify-content: flex-start;
      align-items: center;
      gap: 8px;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      font-family: "DM Mono", monospace;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      padding: 0.28rem 0.45rem;
      border-radius: 0;
      font: 500 10px "DM Mono", monospace;
      letter-spacing: 0.04em;
    }

    .pill.content {
      background: transparent;
      color: var(--green);
      border: 1px solid var(--green);
    }

    .pill.action {
      background: transparent;
      color: var(--orange);
      border: 1px solid var(--orange);
    }

    .tag-uid {
      font: 600 16px "Space Grotesk", sans-serif;
      font-size: 1rem;
      word-break: break-all;
    }

    .tag-value {
      font-size: 0.95rem;
      color: var(--ink);
      word-break: break-word;
      font: 12px "DM Mono", monospace;
      line-height: 1.5;
    }

    .tag-label {
      color: var(--muted);
      font-size: 0.9rem;
    }

    .empty-state {
      padding: 1.2rem 0.5rem;
      text-align: center;
      color: var(--muted);
      background: var(--paper-deep);
      border-radius: 0;
      border: 1px dashed var(--line);
      grid-column: 1 / -1;
    }

    @media (max-width: 640px) {
      .app-shell { width: calc(100% - 32px); }
      .header {
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        padding: 28px 0;
      }

      .actions {
        justify-content: stretch;
      }

      .save-button {
        width: 100%;
      }

      .tag-card {
        grid-template-columns: 1fr;
        gap: 8px;
      }

      .tag-meta {
        justify-content: space-between;
      }
    }

    button:focus-visible, input:focus-visible {
      outline: 3px solid var(--orange);
      outline-offset: 4px;
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        transition-duration: .01ms !important;
      }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <header class="header">
      <div>
        <span class="badge">Tag assignment / field guide</span>
        <h1 class="title">TapTune</h1>
        <p class="subtitle">Assign playlists and shortcuts to your NFC tags.</p>
      </div>
      <span class="badge">Physical input → playback</span>
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

          <div class="field">
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
