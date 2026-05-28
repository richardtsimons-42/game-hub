"""HTML Game Hub - Lightweight game server with modern UI."""

import os
import re
import glob
from flask import Flask, jsonify, send_from_directory, render_template, abort

app = Flask(__name__, static_folder="static")

GAMES_DIR = os.environ.get("GAMES_DIR", "/app/games")
ALLOWED_EXTENSIONS = {".html", ".htm"}


def extract_meta(html_content: str) -> dict:
    """Extract title, description, and favicon from HTML."""
    title = "Untitled Game"
    description = ""
    favicon = None

    # Title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        if not title:
            title = "Untitled Game"

    # Description
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html_content, re.IGNORECASE)
    if desc_match:
        description = desc_match.group(1).strip()

    # Favicon
    fav_match = re.search(r'<link[^>]*rel=["\']icon["\'][^>]*href=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    if not fav_match:
        fav_match = re.search(r'<link[^>]*rel=["\']shortcut icon["\'][^>]*href=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    if fav_match:
        favicon = fav_match.group(1).strip()

    return {"title": title, "description": description, "favicon": favicon}


def scan_games() -> list[dict]:
    """Scan the games directory for HTML files."""
    games = []

    if not os.path.isdir(GAMES_DIR):
        os.makedirs(GAMES_DIR, exist_ok=True)
        return games

    patterns = [
        os.path.join(GAMES_DIR, "*.html"),
        os.path.join(GAMES_DIR, "*.htm"),
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))

    # Also scan subdirectories for index.html
    for subdir in glob.glob(os.path.join(GAMES_DIR, "*")):
        if os.path.isdir(subdir):
            idx = os.path.join(subdir, "index.html")
            if os.path.isfile(idx):
                files.append(idx)

    for filepath in sorted(set(files)):
        rel = os.path.relpath(filepath, GAMES_DIR)
        # Normalize path separators
        rel = rel.replace("\\", "/")

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except (IOError, OSError):
            continue

        meta = extract_meta(content)

        # Check for favicon in the same directory
        game_dir = os.path.dirname(filepath)
        favicon_path = os.path.join(game_dir, "favicon.ico")
        if not os.path.isfile(favicon_path):
            favicon_path = os.path.join(game_dir, "icon.png")
        if not os.path.isfile(favicon_path):
            favicon_path = None

        game_dir_name = os.path.basename(os.path.dirname(filepath)) if os.path.dirname(rel) != "." else ""

        games.append({
            "path": rel,
            "title": meta["title"],
            "description": meta["description"] or "A fun HTML game",
            "favicon": "/icons/" + rel.replace("/", "__") if favicon_path else None,
            "has_favicon": favicon_path is not None,
            "directory": game_dir_name,
        })

    # Sort by directory then title
    games.sort(key=lambda g: (g["directory"], g["title"].lower()))
    return games


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/games")
def api_games():
    return jsonify(scan_games())


@app.route("/icons/<path:filename>")
def serve_icon(filename):
    """Generate a colored placeholder icon from the game title."""
    # filename is like "snake.html" or "subdir__index.html"
    title = filename.replace(".html", "").replace(".htm", "").replace("__", "/")
    # Capitalize
    title = title.replace("-", " ").title()

    # Generate a simple SVG icon
    colors = [
        ("#6366f1", "#8b5cf6"),
        ("#ec4899", "#f43f5e"),
        ("#14b8a6", "#06b6d4"),
        ("#f59e0b", "#ef4444"),
        ("#22c55e", "#10b981"),
        ("#3b82f6", "#6366f1"),
        ("#f97316", "#eab308"),
        ("#8b5cf6", "#d946ef"),
    ]
    idx = sum(ord(c) for c in title) % len(colors)
    c1, c2 = colors[idx]

    # Get first letter
    letter = title[0].upper() if title else "?"

    # Clean letter for SVG
    letter = re.sub(r"[^A-Z]", "", letter)
    if not letter:
        letter = "?"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="128" height="128" rx="24" fill="url(#g)"/>
  <text x="64" y="82" text-anchor="middle" font-family="system-ui, sans-serif" font-size="64" font-weight="bold" fill="white">{letter}</text>
</svg>'''

    from flask import Response
    return Response(svg, mimetype="image/svg+xml")


@app.route("/games/<path:filename>")
def serve_game(filename):
    """Serve a game HTML file."""
    safe = os.path.normpath(filename)
    if safe.startswith("..") or "/" in safe.split("\\"):
        abort(403)

    return send_from_directory(GAMES_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
