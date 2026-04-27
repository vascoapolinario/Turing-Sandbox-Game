# Turing Machine Sandbox – Web Version

This directory contains the **web-only** build of Turing Machine Sandbox, packaged with [pygbag](https://pygame-web.github.io/) to run entirely in the browser.

## Features available in the web version

- **Levels** – All built-in levels and custom levels (stored in browser localStorage)
- **Sandbox** – Free build mode
- **Settings** – Sandbox alphabet customisation
- **Saves** – Turing machine saves and level progress are stored in browser localStorage
- **Custom levels** – Create and play custom levels; stored in browser localStorage
- **Help** – In-game help popup

## Features not available in the web version

The following online-only features have been removed:

- **Accounts / Authentication** – No login, registration or account management
- **Workshop** – Browse/upload/download community levels and machines
- **Leaderboard** – No score submission or viewing
- **Multiplayer** – No lobby or co-op play
- **Discord Rich Presence** – Not applicable in a browser context

## Building and running locally

```bash
pip install pygbag
pygbag web/
```

Then open `http://localhost:8000` in your browser.

## Notes on saves and persistence

All saves use the **browser localStorage** API through pygbag's Emscripten/JavaScript bridge.  
Data is stored per-origin and will persist across browser sessions unless the user clears site data.
