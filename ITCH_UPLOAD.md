# Publish this game on itch.io

This repo is ready to ship both a browser (HTML5) build and a macOS download. Pick whichever you want (or upload both!), then push with itch.io's CLI (butler).

## 1) macOS downloadable build (recommended now)

Already created in this session:
- builds/dps_saket-macos.zip (contains `dps_saket-macos.app`)

If you need to rebuild locally:
1. Ensure dependencies are installed:
   - Python 3.10+ recommended
   - `pip install -r requirements.txt` plus `pip install pyinstaller pygame_gui`
2. Run the build script:
   - `bash scripts/build_macos.sh`
3. Zip appears at `builds/dps_saket-macos.zip`.

Upload to itch with butler:
- Install butler (macOS): `brew install itch-tools/tap/butler` (or download from https://itch.io/docs/butler/)
- First-time login: `butler login`
- Create your game page on itch.io, note your username and game slug.
- Push the macOS build (replace USER/GAME):
  - `butler push builds/dps_saket-macos.zip USER/GAME:mac`

Tips:
- On first run, macOS may show “App is damaged or can’t be opened” due to signing/notarization. As an indie build, advise players to right-click → Open once, or you can codesign/notarize if you have an Apple Developer account.

## 2) Browser (HTML5) build with pygbag

We tried to build with `pygbag` but hit a local SSL certificate issue when fetching the web template. You can fix the certificate bundle on macOS Python and try again.

Fix certificates:
- Run the macOS helper that ships with python.org frameworks:
  - Open Finder → Applications → Python 3.x → "Install Certificates.command"
  - Or run it directly in Terminal, e.g.:
    - `/Applications/Python\ 3.13/Install\ Certificates.command`

Build once certs are fixed:
- `python3 -m pygbag --build start_screen.py`
- The output should be under `build/web` (or `dist/web`).
- Zip the contents of that folder (all files including index.html) into `builds/dps_saket-web.zip`.
- Push to itch (HTML5 channel):
  - `butler push builds/dps_saket-web.zip USER/GAME:html5`

Notes for web:
- We updated `start_screen.py` to avoid subprocess calls in browsers and run stages via dynamic import instead. This is required in the WebAssembly environment.
- Audio can be delayed until the first input due to browser policies. That’s expected.
- If fonts/sounds fail to load, ensure paths remain relative and included by pygbag.

## Page setup tips on itch.io
- Set Kind of project: HTML (for the web build) or Downloadable (for macOS zip).
- For HTML build, enable “This game will be played in the browser” and set a viewport size like 1280x720.
- Add screenshots and a short description. Include basic controls in the page body.
- If you upload both builds, create separate channels (e.g., html5, mac, windows, linux) and mark one as default.

## Troubleshooting
- Pygame window not opening on macOS: check Privacy & Security (allow app), or run from Terminal to see logs.
- Missing assets: ensure `stage 1`, `stage 2`, `fonts`, and `hearts` are bundled. Our PyInstaller command includes these.
- Web build hangs at “packing application”: that was the SSL template fetch. Re-run after fixing certs.
