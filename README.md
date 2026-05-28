# 🎮 Game Hub

A modern, mobile-friendly HTML game hub that auto-discovers and hosts HTML games from a folder.

## Features

- **Auto-discovery** — Drop `.html` files in the `games/` folder and they appear instantly
- **Modern UI** — Dark theme with glassmorphism, animated background, and smooth card animations
- **Mobile-friendly** — Responsive grid layout with touch controls
- **Game icons** — Auto-generated colored SVG icons (or use `favicon.ico` in game folders)
- **Search** — Filter games by name or description
- **Fullscreen** — One-click fullscreen for immersive gameplay

## Quick Start

```bash
docker compose up -d --build
```

Open `http://localhost:8082` in your browser.

## Adding Games

Place `.html` game files in the `games/` folder:

```
games/
  mygame.html
  subfolder/
    index.html
```

Each game reads its title from `<title>` and description from `<meta name="description">`.

## Tech Stack

- **Backend:** Python / Flask
- **Frontend:** Vanilla HTML/CSS/JS
- **Container:** Docker
