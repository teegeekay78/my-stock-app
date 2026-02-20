import streamlit as st
import yfinance as yf
from mftool import Mftool
from google import genai
from google.genai import types
import plotly.express as px
from curl_cffi import requests as curl_requests

# 1. Page Config
st.set_page_config(page_title="India Invest AI", layout="wide")

# 2. AI Client Initialization (2026 SDK)
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"], 
        http_options=types.HttpOptions(api_version='v1')
    )
else:
    st.error("Missing Key in Secrets")
    st.stop()

st.title("🇮🇳 India Invest AI")
t1, t2 = st.tabs(["📈 Stocks", "💰 Mutual Funds"])

# 3. Stock Tab
# Inside your ticker block:
    
with t1:
    ticker = st.text_input("NSE Ticker", value="INFY").upper()
    if ticker:
        try:
            # Create a session that looks like a real browser
            session = curl_requests.Session(impersonate="chrome")
            data = yf.Ticker(f"{ticker}.NS", session=session)
            df = data.history(period="1mo")
            if not df.empty:
                st.metric(f"{ticker}", f"₹{df['Close'].iloc[-1]:.2f}")
                st.line_chart(df['Close'])
                # ... rest of your Consult AI button code ...
        except Exception as e:
            st.error(f"Data Error: {e}")
      
            # Interactive Plotly Chart
            fig = px.line(df, y='Close', title=f"{ticker} 30-Day Trend")
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("🤖 Consult AI Analyst"):
                try:
                    # Professional Technical Prompt
                    prompt = f"""
                    Analyze {ticker} with these recent prices: {df['Close'].tail(10).to_string()}
                    1. Identify the Technical Trend (Bullish/Bearish).
                    2. Suggest Key Support and Resistance levels.
                    3. Give a Recommendation (Buy/Hold/Sell) with technical logic.
                    """
                    
                    with st.spinner("AI is analyzing charts..."):
                        # Correct 2026 method call
                        resp = client.models.generate_content(
                            model="gemini-2.0-flash", 
                            contents=prompt
                        )
                        st.markdown("---")
                        st.markdown("### 🤖 Expert AI Analysis")
                        st.write(resp.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# 4. Mutual Fund Tab
with t2:
    mf = Mftool()
    mf_q = st.text_input("Search Mutual Fund Name")
    if mf_q:
        schemes = mf.get_scheme_codes()
        matches = {k: v for k, v in schemes.items() if mf_q.lower() in v.lower()}
        if matches:
            sel = st.selectbox("Select Scheme", list(matches.values()))
            if st.button("Get Latest NAV"):
                code = [k for k, v in matches.items() if v == sel][0]
                quote = mf.get_scheme_quote(code)
                st.info(f"The latest NAV for {sel} is: {quote['nav']}")
