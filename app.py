import streamlit as st
import yfinance as yf
from mftool import Mftool
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types
# --- PAGE CONFIG ---
st.set_page_config(page_title="India Invest AI", layout="centered")

# --- INITIALIZE AI CLIENT ---
if "GEMINI_API_KEY" in st.secrets:
client = genai.Client(
api_key=st.secrets["GEMINI_API_KEY"],
http_options=types.HttpOptions(api_version='v1')
)
else:
st.error("Missing GEMINI_API_KEY in Secrets.")
st.stop()

st.title("🇮🇳 India Invest AI")
tab1, tab2 = st.tabs(["📈 Stocks", "💰 Mutual Funds"])

# --- CUSTOM CSS FOR MOBILE ---
st.markdown("""
    <style>
    .main { max-width: 500px; margin: 0 auto; }
    .stButton button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# st.title("🇮🇳 India Invest AI")
# st.caption("Stocks (NSE) & Mutual Funds Assistant")

tab1, tab2 = st.tabs(["📈 Stocks", "💰 Mutual Funds"])

# --- TAB 1: STOCKS (NSE) ---
with tab1:
ticker = st.text_input("Enter NSE Ticker", value="TATAMOTORS").upper()
if ticker:
symbol = f"{ticker}.NS"
try:
df = yf.Ticker(symbol).history(period="1mo")
if not df.empty:
st.metric(f"{ticker} Price", f"₹{df['Close'].iloc[-1]:.2f}")
fig = px.line(df, y='Close', title=f"{ticker} - 30 Days")
st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: MUTUAL FUNDS ---
with tab2:

mf = Mftool()
mf_query = st.text_input("Search Mutual Fund")
if mf_query:
schemes = mf.get_scheme_codes()
matches = {k: v for k, v in schemes.items() if mf_query.lower() in v.lower()}
if matches:
selected = st.selectbox("Select Scheme", list(matches.values()))
code = [k for k, v in matches.items() if v == selected][0]
if st.button("Show NAV"):
nav = mf.get_scheme_quote(code)
st.metric("Current NAV", f"₹{nav['nav']}")
