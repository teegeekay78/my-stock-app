import streamlit as st
import yfinance as yf
from mftool import Mftool
import pandas as pd
import plotly.expressions as px
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="India Invest Pro AI", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { max-width: 500px; margin: 0 auto; }
    .stButton button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1E1E1E; color: white; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇮🇳 India Invest Pro")
st.caption("NSE Stock Analysis & Mutual Fund NAV Tracker")

# --- SIDEBAR: API KEY ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your free key at [aistudio.google.com](https://aistudio.google.com/)")

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Stock Analyst", "💰 Mutual Funds"])

# --- TAB 1: STOCKS (NSE) ---
with tab1:
    ticker = st.text_input("NSE Ticker", value="TATAMOTORS").upper()
    if ticker:
        # 1. Fetch data
        df = yf.Ticker(f"{ticker}.NS").history(period="1mo")
        
        if not df.empty:
            # 2. Display Price & Chart (Always visible)
            st.metric(f"{ticker}", f"₹{df['Close'].iloc[-1]:.2f}")
            st.line_chart(df['Close']) 
            
            # 3. The Consult AI Button (Aligned with the chart)
            if st.button("🤖 Consult AI"):
                try:
                    # The prompt with your new technical analysis instructions
                    prompt = f"""
                    Analyze {ticker} using these prices: {df['Close'].tail(10).to_string()}
                    1. Trend: Bullish/Bearish?
                    2. Support/Resistance levels?
                    3. Buy/Sell/Hold recommendation with logic.
                    """
                    
                    # Show a spinner so the user knows the AI is thinking
                    with st.spinner("Analyzing markets..."):
                        resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                        st.markdown("### 🤖 AI Technical Report")
                        st.write(resp.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
        else:
            st.warning("No data found. Please check the ticker symbol.")
# --- TAB 2: MUTUAL FUNDS ---
with tab2:
    mf = Mftool()
    mf_query = st.text_input("Search Fund Name (e.g. 'SBI Small Cap')")
    
    if mf_query:
        all_funds = mf.get_scheme_codes()
        matches = {k: v for k, v in all_funds.items() if mf_query.lower() in v.lower()}
        
        if matches:
            selected_name = st.selectbox("Pick Scheme", list(matches.values()))
            code = [k for k, v in matches.items() if v == selected_name][0]
            
            if st.button("Check NAV"):
                details = mf.get_scheme_details(code)
                quote = mf.get_scheme_quote(code)
                st.markdown(f"### {details['scheme_name']}")
                st.metric("Latest NAV", f"₹{quote['nav']}")
                st.info(f"**Category:** {details['scheme_category']}")
        else:
            st.info("No funds found with that name.")
