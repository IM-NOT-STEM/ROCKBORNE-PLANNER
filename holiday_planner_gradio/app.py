import os
import urllib.parse
import gradio as gr

"""
Minimal Holiday Planner using Google Maps Embed API inside a Gradio app.

Features:
- User enters a destination (city, island, or coordinates).
- User selects a nightlife/amenity category.
- App renders a live Google Map (embedded) showing matching places near the destination.

Setup:
- Set an environment variable GOOGLE_MAPS_API_KEY with a valid Maps Embed API key.
- Or create a .env file and load it (see README).
"""

DEFAULT_DEST = "Cancún, Mexico"
CATEGORIES = [
    "nightclubs",
    "restaurants",
    "bars",
    "live music",
    "beach clubs",
    "cafes"
]

def build_embed_url(destination: str, category: str, zoom: int = 13, maptype: str = "roadmap") -> str:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return ""

    # Build a search query like: "nightclubs near Cancún, Mexico"
    q = f"{category} near {destination}".strip()
    q_enc = urllib.parse.quote(q)

    base = "https://www.google.com/maps/embed/v1/search"
    url = f"{base}?key={api_key}&q={q_enc}&zoom={zoom}&maptype={maptype}"
    return url

def make_iframe(url: str, height: int = 600) -> str:
    if not url:
        return "<div style='color:red;padding:1rem'>Error: Missing GOOGLE_MAPS_API_KEY environment variable.</div>"
    return f"""
    <iframe
      width="100%"
      height="{height}"
      frameborder="0" style="border:0"
      referrerpolicy="no-referrer-when-downgrade"
      allowfullscreen
      src="{url}">
    </iframe>
    """

def generate_map(dest, category, zoom, maptype, iframe_height):
    url = build_embed_url(dest or DEFAULT_DEST, category, zoom, maptype)
    return make_iframe(url, iframe_height)

with gr.Blocks(title="Holiday Planner • Nightlife Map") as demo:
    gr.Markdown("# Holiday Planner")
    gr.Markdown("Type a tropical destination and pick a category to find nearby nightlife spots on the map.")

    with gr.Row():
        dest = gr.Textbox(label="Destination", value=DEFAULT_DEST, placeholder="e.g., Phuket, Thailand")
        category = gr.Dropdown(CATEGORIES, value="nightclubs", label="Category")
    with gr.Row():
        zoom = gr.Slider(3, 20, value=13, step=1, label="Zoom")
        maptype = gr.Dropdown(["roadmap", "satellite", "terrain", "hybrid"], value="roadmap", label="Map Type")
        iframe_height = gr.Slider(300, 900, value=600, step=10, label="Map Height (px)")

    out = gr.HTML(label="Map")
    run_btn = gr.Button("Show on Map", variant="primary")

    run_btn.click(fn=generate_map, inputs=[dest, category, zoom, maptype, iframe_height], outputs=out)

if __name__ == "__main__":
    # Optionally load .env if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    demo.launch()