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
    ticker = st.text_input("Enter NSE Ticker", value="RELIANCE").upper()
    
    if ticker:
        symbol = f"{ticker}.NS"
        stock_data = yf.Ticker(symbol)
        
        try:
            # Fetch 1 month for the chart, but we will use 10 days for AI
            df = stock_data.history(period="1mo")
            
            if df.empty:
                st.error("Ticker not found. Please use NSE symbols like 'INFY' or 'TCS'.")
            else:
                curr_price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                change_pct = ((curr_price - prev_close) / prev_close) * 100
                
                # Metrics Row
                col1, col2 = st.columns(2)
                col1.metric("Current Price", f"₹{curr_price:.2f}")
                col2.metric("Day Change", f"{change_pct:.2f}%")
                
                # Interactive Chart
                fig = px.area(df, y='Close', title=f"{ticker} Trend (1 Month)")
                fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
                st.plotly_chart(fig, use_container_width=True)

                # AI Analysis Button
                if st.button(f"🔍 Run Technical Analysis for {ticker}"):
                    if not api_key:
                        st.warning("Please enter your Gemini API Key in the sidebar.")
                    else:
                        try:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-pro')
                            
                            # Using your specific prompt template
                            recent_prices = df['Close'].tail(10).to_string()
                            professional_prompt = f"""
                            You are an expert SEBI-registered technical analyst. 
                            Analyze the following NSE stock ticker: {ticker}
                            Recent Close Prices: {recent_prices}

                            Provide a structured report including:
                            1. **Technical Trend**: (Bullish, Bearish, or Sideways)
                            2. **Key Levels**: Identify immediate Support and Resistance.
                            3. **Indicators**: Comment on price action vs the 5-day and 10-day averages.
                            4. **Recommendation**: (Strong Buy, Buy, Hold, or Sell) with a brief logic.
                            5. **Risk Note**: One specific risk for this stock.

                            Keep the tone professional and concise. Use bullet points.
                            """
                            
                            with st.spinner('Calculating technical levels...'):
                                response = model.generate_content(professional_prompt)
                                st.markdown("---")
                                st.subheader("📈 Professional Analysis Report")
                                st.write(response.text)
                                st.warning("**Disclaimer:** This is an AI-generated simulation. I am an AI, not a SEBI-registered advisor. Use this for educational purposes only.")
                        except Exception as e:
                            st.error(f"Analysis Error: {e}")

        except Exception as e:
            st.error("Error connecting to market data.")

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
