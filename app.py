import streamlit as st
import yfinance as yf
from mftool import Mftool
from google import genai
from google.genai import types
import plotly.express as px  # <--- Added 'as px' here
from curl_cffi import requests as curl_requests # <--- Added 'as curl_requests' here

st.set_page_config(page_title="India Invest AI", layout="wide")

# AI Client Initialization
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"], 
        http_options=types.HttpOptions(api_version='v1')
    )
else:
    st.error("Check Secrets")
    st.stop()

st.title("🇮🇳 India Invest AI")
t1, t2 = st.tabs(["📈 Stocks", "💰 Mutual Funds"])

with t1:
    ticker = st.text_input("NSE Ticker", value="TATAMOTORS").upper()
    if ticker:
        try:
            # Bypass Yahoo block with a Browser Session
            session = curl_requests.Session(impersonate="chrome")
            data = yf.Ticker(f"{ticker}.NS", session=session)
            df = data.history(period="1mo")
            
            if not df.empty:
                st.metric(f"{ticker}", f"₹{df['Close'].iloc[-1]:.2f}")
                
                # Interactive Chart
                fig = px.line(df, y='Close', title=f"{ticker} 30-Day Trend")
                st.plotly_chart(fig, use_container_width=True)
                
                if st.button("🤖 Consult AI Analyst"):
                    with st.spinner("Analyzing..."):
                        prompt = f"Technical analysis for {ticker}. Prices: {df['Close'].tail(10).to_string()}"
                        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                        st.markdown(resp.text)
            else:
                st.warning("No data found for this ticker.")
        except Exception as e:
            st.error(f"Error: {e}")
