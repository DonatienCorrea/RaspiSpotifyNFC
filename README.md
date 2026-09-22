# TapTune

TapTune is a Raspberry Pi + RC522 NFC reader project that lets a household tap physical tags to trigger Spotify playback and simple control actions.

## v1 goals

- Tap a tag to play or resume a Spotify playlist/album/track
- Tap control tags to play/pause or skip to next track
- Manage tag assignments from a small local web UI on the Pi
- Persist tag-to-content mappings in SQLite so the system is easy to maintain
- Support a simulated NFC input path for testing without hardware

## Architecture

- `app/config.py`: environment/config loading using `.env`
- `app/db.py`: SQLite access layer for tags and resume data
- `app/nfc_reader.py`: NFC abstraction with RC522 and simulated input mode
- `app/spotify_service.py`: Spotipy-backed playback and control operations
- `app/web.py`: Flask admin UI for assigning and listing tags
- `app/main.py`: app entry point

## Local development

1. Create a virtual environment:
   `python3 -m venv .venv`
2. Activate it:
   `source .venv/bin/activate`
3. Install the base dependencies:
   `pip install -r requirements.txt`
4. On the Pi, install the hardware-specific NFC packages too:
   `pip install -r requirements-pi.txt`
5. Copy the example environment file:
   `cp .env.example .env`
6. Fill in your Spotify credentials and refresh token when you want live playback.
7. If no Spotify credentials are present, the app runs in a safe fake mode so the full tag flow can still be tested locally.
8. Initialize the SQLite database and start the app:
   `python -m app.main`

## Simulated NFC test flow

You can test the tag dispatch path without wiring up hardware:

```bash
python -m app.simulate --uid 01AABBCC --payload "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"
python -m app.simulate --uid 02AABBCC --payload "action:play_pause"
```

This exercises the same handler that a physical tag scan uses.

## Device deployment notes

- Target OS: Raspberry Pi OS Lite
- Target hardware: Raspberry Pi 5 + RC522 over SPI
- Service management: `systemd` with auto-restart
- Spotify access: shared household Premium account via refresh token
- No status LEDs or audio feedback in v1; errors are logged and viewed via SSH

## GitHub Pages

A simple landing page for the project is included in `docs/index.html` and is ready to be used with GitHub Pages.

To enable it in GitHub:

1. Open the repository on GitHub.
2. Go to Settings → Pages.
3. Source: Deploy from a branch.
4. Branch: `master` and folder: `/docs`.
5. Save.

## Future fast-follows

- Bluetooth speaker support
- LED/audio feedback
- Volume control tags
- Public installer or shareable packaging
