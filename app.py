import streamlit as st
import yfinance as yf
from mftool import Mftool
import pandas as pd
import plotly.express as px
from google import genai  # Use the NEW stable library

# --- PAGE CONFIG ---
st.set_page_config(page_title="India Invest AI", layout="centered")

# --- INITIALIZE AI CLIENT ---
if "GEMINI_API_KEY" in st.secrets:
    # The new client automatically uses the correct stable API version
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Error: GEMINI_API_KEY not found in Streamlit Secrets.")
    st.stop()

# --- CUSTOM CSS FOR MOBILE ---
st.markdown("""
    <style>
    .main { max-width: 500px; margin: 0 auto; }
    .stButton button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇮🇳 India Invest AI")
st.caption("Stocks (NSE) & Mutual Funds Assistant")

tab1, tab2 = st.tabs(["📈 Stocks", "💰 Mutual Funds"])

# --- TAB 1: STOCKS (NSE) ---
with tab1:
    ticker_input = st.text_input("Enter NSE Ticker", value="TATAMOTORS").upper()
    
    if ticker_input:
        symbol = f"{ticker_input}.NS"
        stock = yf.Ticker(symbol)
        
        try:
            df = stock.history(period="1mo")
            if df.empty:
                st.error("Ticker not found. Try 'RELIANCE' or 'TCS'.")
            else:
                current_price = df['Close'].iloc[-1]
                change = current_price - df['Close'].iloc[0]
                
                st.metric(label=f"{ticker_input} Price", value=f"₹{current_price:.2f}", delta=f"{change:.2f} (1M)")
                
                fig = px.line(df, y='Close', title=f"{ticker_input} - Last 30 Days")
                fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
                st.plotly_chart(fig, use_container_width=True)

                if st.button("🤖 Consult Gemini AI"):
                    try:
                        recent_data = df[['Close']].tail(30).to_string()
                        prompt = f"Act as an Indian Stock Expert. Analyze these 30-day prices for {ticker_input}: {recent_data}. Suggest Buy/Hold/Sell in 3 bullets."
                        
                        with st.spinner('AI is analyzing...'):
                            # Updated call for the new SDK
                            response = client.models.generate_content(
                                model="gemini-1.5-flash", 
                                contents=prompt
                            )
                            st.subheader("AI Analysis")
                            st.write(response.text)
                            st.caption("Disclaimer: For educational purposes only.")
                    except Exception as e:
                        st.error(f"AI Error: {e}")

        except Exception as e:
            st.error("Could not fetch stock data.")

# --- TAB 2: MUTUAL FUNDS ---
with tab2:
    mf = Mftool()
    mf_search = st.text_input("Search Mutual Fund (e.g., Parag Parikh)")
    if mf_search:
        all_schemes = mf.get_scheme_codes()
        matches = {k: v for k, v in all_schemes.items() if mf_search.lower() in v.lower()}
        if matches:
            selected_scheme_name = st.selectbox("Select Exact Scheme", list(matches.values()))
            scheme_code = [k for k, v in matches.items() if v == selected_scheme_name][0]
            if st.button("Get NAV Details"):
                nav_data = mf.get_scheme_quote(scheme_code)
                st.metric("Current NAV", f"₹{nav_data['nav']}")
