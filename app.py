import streamlit as st
import yfinance as yf
from mftool import Mftool
from google import genai
from google.genai import types

st set_page_config(page_title="India Invest AI")

if "GEMINI_API_KEY" in st secrets:
    client = genai Client(api_key=st secrets["GEMINI_API_KEY"], http_options=types HttpOptions(api_version='v1'))
else:
    st error("Missing Key")
    st stop()

st title("🇮🇳 India Invest AI")
t1, t2 = st tabs(["📈 Stocks", "💰 Mutual Funds"])

with t1:
    ticker = st text_input("NSE Ticker", value="TATAMOTORS") upper()
    if ticker:
        df = yf Ticker(f"{ticker} NS") history(period="1mo")
        if not df empty:
            st metric(f"{ticker}", f"₹{df['Close'] iloc[-1]: 2f}")
            if st button("🤖 Consult AI"):
                try:
                    prompt = f"Analyze {ticker}: {df['Close'] tail(5) to_string()}"
                    resp = client models generate_content(model="gemini-2 0-flash", contents=prompt)
                    st write(resp text)
                except Exception as e:
                    st error(f"AI Error: {e}")

with t2:
    mf = Mftool()
    mf_q = st text_input("Search MF")
    if mf_q:
        schemes = mf get_scheme_codes()
        matches = {k: v for k, v in schemes items() if mf_q lower() in v lower()}
        if matches:
            sel = st selectbox("Select", list(matches values()))
            if st button("Show NAV"):
                code = [k for k, v in matches items() if v == sel][0]
                st write(f"NAV: {mf get_scheme_quote(code)['nav']}")
