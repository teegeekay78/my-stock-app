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
with t2:
    st.subheader("💰 Indian Mutual Fund Explorer")
    
    # 1. Use caching to prevent empty loads
    @st.cache_data(ttl=3600) # Cache data for 1 hour
    def get_mf_list():
        mf_tool = Mftool()
        return mf_tool.get_scheme_codes()

    try:
        schemes = get_mf_list()
        
        # 2. Search Box
        mf_q = st.text_input("Search for a Fund (e.g., 'SBI Bluechip' or 'Parag Parikh')")
        
        if mf_q:
            # Filter the cached list
            matches = {k: v for k, v in schemes.items() if mf_q.lower() in v.lower()}
            
            if matches:
                sel = st.selectbox("Select the exact scheme", list(matches.values()))
                
                if st.button("📊 Show Latest NAV"):
                    # Find the code for the selected name
                    code = [k for k, v in matches.items() if v == sel][0]
                    
                    # Get fresh data for the specific fund
                    mf_engine = Mftool()
                    quote = mf_engine.get_scheme_quote(code)
                    
                    st.success(f"**{sel}**")
                    st.metric("Latest NAV", f"₹{quote['nav']}")
                    st.caption(f"Last Updated: {quote['last_updated']}")
            else:
                st.warning("No matching funds found. Try a different keyword.")
        else:
            st.info("Enter a fund name above to see latest prices.")
            
    except Exception as e:
        st.error(f"Could not connect to AMFI servers: {e}")
