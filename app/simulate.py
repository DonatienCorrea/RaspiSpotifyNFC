import argparse

from .db import record_event, upsert_tag
from .spotify_service import next_track, play_content, toggle_playback


def dispatch_simulated_value(uid: str, value: str) -> dict:
    if value.startswith("spotify:"):
        tag_type = "content"
        upsert_tag(uid=uid, value=value, tag_type=tag_type, label=f"simulated-{uid}")
        record_event(uid, tag_type, value, source="simulate")
        return play_content(value)

    if value == "action:play_pause":
        upsert_tag(uid=uid, value=value, tag_type="action", label=f"simulated-{uid}")
        record_event(uid, "action", value, source="simulate")
        return toggle_playback()

    if value == "action:next":
        upsert_tag(uid=uid, value=value, tag_type="action", label=f"simulated-{uid}")
        record_event(uid, "action", value, source="simulate")
        return next_track()

    raise ValueError(f"Unsupported simulated tag value: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a tag scan for local testing")
    parser.add_argument("--uid", required=True)
    parser.add_argument("--payload", required=True)
    args = parser.parse_args()

    result = dispatch_simulated_value(args.uid, args.payload)
    print({"uid": args.uid, "payload": args.payload, "result": result})


if __name__ == "__main__":
    main()
