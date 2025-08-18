
import os
import json
import time
from datetime import date, timedelta
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.db import get_session, init_db
from src.data import TROPICAL_CANDIDATES
from src.weather import get_weather_bundle
from src.places import nightlife_density, lodging_signals, places_heatmap_points
from src.flights import get_flight_quote, google_flights_link
from src.utils.google_maps import make_map_embed, make_heatmap_embed

load_dotenv()

st.set_page_config(page_title="Holiday Planner — Tropical Adventure", page_icon="🏝️", layout="wide")
st.title("Holiday Planner — Tropical Adventure Near Nightlife")

with st.sidebar:
    st.header("Inputs")
    origin = st.text_input("Origin airport (IATA code, e.g. LHR, JFK)", value="LHR")
    start_date = st.date_input("Start date", value=date.today() + timedelta(days=30))
    trip_length = st.number_input("Trip length (days)", min_value=3, max_value=21, value=7, step=1)
    max_budget = st.number_input("Budget cap (approx, in your currency)", min_value=200, value=1500, step=50)
    st.caption("We estimate flight + lodging signals. Exact prices vary by provider & date.")
    st.divider()
    st.header("API Keys Status")
    gmaps_ok = bool(os.getenv("GOOGLE_MAPS_API_KEY"))
    owm_ok = bool(os.getenv("OPENWEATHER_API_KEY"))
    tequila_ok = bool(os.getenv("TEQUILA_API_KEY"))
    st.write(f"Google Maps key: {'✅' if gmaps_ok else '❌'}")
    st.write(f"OpenWeather key: {'✅' if owm_ok else '❌'}")
    st.write(f"Kiwi (Tequila) key: {'✅' if tequila_ok else '⚠️ optional'}")

st.markdown("This tool ranks tropical destinations by **weather suitability**, **nightlife density**, and **cost signals**.")

# Initialize DB
session = get_session()
init_db(session)

# Prepare candidate DataFrame
df = pd.DataFrame(TROPICAL_CANDIDATES)

# Compute metrics
results = []
with st.spinner("Scoring destinations..."):
    for row in df.itertuples():
        dest = {
            "name": row.city,
            "country": row.country,
            "lat": row.lat,
            "lon": row.lon,
            "airport": row.airport
        }
        # Weather bundle
        weather = get_weather_bundle(row.lat, row.lon)
        # Nightlife/amenities density
        places = nightlife_density(row.lat, row.lon, radius_m=2500)
        lodging = lodging_signals(row.lat, row.lon, radius_m=3000)
        # Flight quote (optional if TEQUILA_API_KEY missing)
        flight = get_flight_quote(origin, row.airport, start_date, trip_length)

        # Score
        # Weather score favors 24-33C, humidity <= 80%, low cloudiness, mild winds
        temp = weather.get("temp_max_c")
        humidity = weather.get("humidity")
        cloud = weather.get("clouds")
        wind = weather.get("wind_speed")
        nightlife = places.get("count_total", 0)
        price_index = lodging.get("avg_price_level", None)  # 0-4 scale
        flight_price = flight.get("price", None) if flight else None

        # Simple heuristic scoring
        w_score = 0
        if temp is not None:
            if 24 <= temp <= 33: w_score += 40
            else: w_score += max(0, 40 - abs((temp - 28))*3)
        if humidity is not None:
            w_score += max(0, 20 - max(0, humidity - 80)*0.5)
        if cloud is not None:
            w_score += max(0, 15 - cloud*0.15)
        if wind is not None:
            w_score += max(0, 15 - max(0, wind - 6)*2)

        n_score = min(25, nightlife * 0.2)  # diminishing
        c_score = 0
        if price_index is not None:
            # Lower price_level is better (0-4). Normalize: 25 at 0, 0 at 4.
            c_score += max(0, 25 - (price_index * (25/4)))
        if flight_price is not None and max_budget:
            # Reward if well under budget
            try:
                budget_ratio = float(flight_price) / float(max_budget)
                c_score += max(0, 25 - budget_ratio*25)
            except Exception:
                pass

        total = w_score + n_score + c_score

        results.append({
            **dest,
            **weather,
            **places,
            **lodging,
            **(flight or {}),
            "score": round(total, 2),
        })

res_df = pd.DataFrame(results).sort_values("score", ascending=False).reset_index(drop=True)
st.subheader("Top Picks")
st.dataframe(res_df[["name","country","airport","score","temp_max_c","humidity","clouds","wind_speed","count_bars","count_night_clubs","count_restaurants","avg_price_level","price"]])

# Map pins
st.subheader("Map of Recommended Destinations")
api_key = os.getenv("GOOGLE_MAPS_API_KEY","")
st.components.v1.html(make_map_embed(api_key, res_df.to_dict(orient="records")), height=500)

# Details selector
st.subheader("Destination Details")
choice = st.selectbox("Pick a destination", options=res_df["name"].tolist())
sel = res_df[res_df["name"] == choice].iloc[0].to_dict()
st.write(f"**{sel['name']}, {sel['country']}** — Airport: {sel['airport']}")
st.write(f"Weather: max {sel.get('temp_max_c')}°C, humidity {sel.get('humidity')}%, clouds {sel.get('clouds')}%, wind {sel.get('wind_speed')} m/s")
if sel.get("price"):
    st.write(f"Estimated flight price: ~{sel['price']}")
st.write("Nightlife counts (2.5-3 km radius): bars, clubs, restaurants =", sel.get("count_bars"), sel.get("count_night_clubs"), sel.get("count_restaurants"))

# Heatmap
st.markdown("**Nightlife Heatmap**")
heat_pts = places_heatmap_points(sel["lat"], sel["lon"], radius_m=2500)
st.components.v1.html(make_heatmap_embed(api_key, sel["lat"], sel["lon"], heat_pts), height=500)

# Google Flights link
link = google_flights_link(origin, sel["airport"], start_date, trip_length)
st.markdown(f"[Open in Google Flights]({link})")

st.divider()
st.caption("⚠️ Prices are indicative. Lodging price uses Google Places `price_level` (0-4) as a rough signal. For exact rates, integrate a hotel API.")
