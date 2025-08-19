# Holiday Planner (Minimal) — Gradio + Google Maps Embed API

A super simple, fully working website you can run in PyCharm. Enter a destination (e.g., "Phuket, Thailand") and pick a category (nightclubs, bars, restaurants, etc.). The app embeds a live Google Map using the Maps **Embed API** and shows matching places.

## Quick Start

### 1) Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Add your Google Maps API key
- Copy `.env.example` to `.env`
- Replace the value with your own key (already filled for convenience in the example file)
- **Do not commit your real `.env`**

Alternatively, set an environment variable:
- Windows PowerShell:
```powershell
$env:GOOGLE_MAPS_API_KEY="YOUR_KEY_HERE"
```
- macOS/Linux:
```bash
export GOOGLE_MAPS_API_KEY="YOUR_KEY_HERE"
```

### 4) Run the app
```bash
python app.py
```
Gradio will print a local URL. Open it in your browser.

## Notes

- This project uses the **Google Maps Embed API** to keep things as simple as possible. If you need more control (custom pins, drawing layers, client side routing), you can later switch to the **Maps JavaScript API** with the Places Library and render it in a custom HTML component or a small frontend.
- The interface is intentionally minimal — perfect for a baseline that you can extend (e.g., presets for popular tropical destinations, saved favorites, etc.).
- If the map area shows an error, confirm your API key is enabled for the **Maps Embed API** in Google Cloud Console and that billing is set up.
- To deploy, you can use `gradio deploy` or run on any Python host that exposes the port.

## Project Structure
```
holiday_planner_gradio/
├─ app.py
├─ requirements.txt
├─ .env.example
└─ README.md
```

## PyCharm Tips
- Open the folder as a project
- Configure the Python interpreter to use `.venv`
- Create a Run/Debug configuration for `app.py`