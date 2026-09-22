from flask import Flask, jsonify, render_template_string, request

from .config import settings
from .db import get_tag_by_uid, list_tags, record_event, upsert_tag
from .spotify_service import dispatch_tag_value

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>TapTune</title>
</head>
<body>
  <h1>TapTune</h1>
  <form method="post" action="/assign">
    <label>Tag UID<br><input name="uid" required></label><br>
    <label>Label<br><input name="label"></label><br>
    <label>Spotify URI / Action<br><input name="value" required placeholder="spotify:playlist:... or action:play_pause"></label><br>
    <button type="submit">Save tag</button>
  </form>

  <h2>Assigned tags</h2>
  <ul>
    {% for tag in tags %}
      <li>{{ tag.uid }} — {{ tag.value }}{% if tag.label %} ({{ tag.label }}){% endif %}</li>
    {% else %}
      <li>No tags assigned yet.</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template_string(HTML, tags=list_tags())

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
        return jsonify({"ok": True, "tag": tag})

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
