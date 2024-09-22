import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.gridspec import GridSpec

# Funciones para calcular indicadores técnicos
def RSI(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def SMA(series, period=50):
    return series.rolling(window=period).mean()

def MACD(series, short_window=12, long_window=26, signal_window=9):
    short_ema = series.ewm(span=short_window, adjust=False).mean()
    long_ema = series.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return macd_line, signal_line

# Función para obtener y calcular variaciones
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1y')

    current_price = hist['Close'][-1]
    daily_var = (hist['Close'][-1] - hist['Close'][-2]) / hist['Close'][-2] * 100
    weekly_var = (hist['Close'][-1] - hist['Close'][-6]) / hist['Close'][-6] * 100
    monthly_var = (hist['Close'][-1] - hist['Close'][-22]) / hist['Close'][-22] * 100
    ytd_var = (hist['Close'][-1] - hist['Close'][hist.index.year == pd.Timestamp.now().year][0]) / hist['Close'][hist.index.year == pd.Timestamp.now().year][0] * 100
    annual_var = (hist['Close'][-1] - hist['Close'][-252]) / hist['Close'][-252] * 100 if len(hist) >= 252 else None

    return hist, current_price, daily_var, weekly_var, monthly_var, ytd_var, annual_var

# Función para obtener datos fundamentales
def get_fundamental_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    pe_ratio = info.get('forwardPE', None)
    roe = info.get('returnOnEquity', None) * 100 if info.get('returnOnEquity', None) is not None else None
    eps = info.get('trailingEps', None)
    dividend_yield = info.get('dividendYield', None) * 100 if info.get('dividendYield', None) is not None else None
    beta = info.get('beta', None)
    market_cap = info.get('marketCap', None) / 1e12 if info.get('marketCap', None) is not None else None

    return pe_ratio, roe, eps, dividend_yield, beta, market_cap

def color_indicator(value, threshold_buy, threshold_sell):
    if value > threshold_buy:
        return 'green'
    elif value < threshold_sell:
        return 'red'
    return 'white'

def create_panel(ticker):
    hist, current_price, daily_var, weekly_var, monthly_var, ytd_var, annual_var = get_stock_data(ticker)
    pe_ratio, roe, eps, dividend_yield, beta, market_cap = get_fundamental_data(ticker)

    avg_volume = hist['Volume'].mean()
    current_volume = hist['Volume'][-1]

    # Cálculo de indicadores técnicos
    rsi = RSI(hist['Close'])
    sma_50 = SMA(hist['Close'], 50)
    sma_200 = SMA(hist['Close'], 200)
    macd_line, signal_line = MACD(hist['Close'])

    # Setup Streamlit layout
    st.title(f"Panel de Análisis para {ticker}")
    
    # Precio y variaciones
    st.subheader("Precio y Variaciones")
    st.write(f"Precio actual: ${current_price:.2f}")
    st.markdown(f"<span style='color:{'green' if daily_var > 0 else 'red'};'>Variación diaria: {daily_var:.2f}%</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{'green' if weekly_var > 0 else 'red'};'>Variación semanal: {weekly_var:.2f}%</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{'green' if monthly_var > 0 else 'red'};'>Variación mensual: {monthly_var:.2f}%</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{'green' if ytd_var > 0 else 'red'};'>Variación YTD: {ytd_var:.2f}%</span>", unsafe_allow_html=True)
    if annual_var is not None:
        st.markdown(f"<span style='color:{'green' if annual_var > 0 else 'red'};'>Variación anual: {annual_var:.2f}%</span>", unsafe_allow_html=True)
    else:
        st.write("Variación anual: N/A")

    # Gráfico de precios
    st.subheader("Gráfico de Precios")
    plt.figure(figsize=(10, 5))
    hist['Close'].plot(color='cyan')
    plt.title(f"Gráfico de {ticker}")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    st.pyplot(plt)

    # Indicadores Técnicos
    st.subheader("Indicadores Técnicos")
    st.markdown(f"<span style='color:{color_indicator(rsi[-1], 70, 30)};'>RSI: {rsi[-1]:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color_indicator(current_price, sma_50[-1], sma_50[-1])};'>SMA 50: ${sma_50[-1]:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color_indicator(current_price, sma_200[-1], sma_200[-1])};'>SMA 200: ${sma_200[-1]:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color_indicator(macd_line[-1] - signal_line[-1], 0, 0)};'>MACD: {macd_line[-1]:.2f}</span>", unsafe_allow_html=True)

    # Análisis Fundamental
    st.subheader("Análisis Fundamental")
    st.markdown(f"<span style='color:{color_indicator(pe_ratio, 15, 25)};'>P/E Ratio: {pe_ratio:.2f}</span>" if pe_ratio else "<span style='color:white;'>P/E Ratio: N/A</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color_indicator(roe, 15, 5)};'>ROE: {roe:.2f}%</span>" if roe else "<span style='color:white;'>ROE: N/A</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color_indicator(eps, 1, 0)};'>EPS: {eps:.2f}</span>" if eps else "<span style='color:white;'>EPS: N/A</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color_indicator(dividend_yield, 5, 2)};'>Dividend Yield: {dividend_yield:.2f}%</span>" if dividend_yield else "<span style='color:white;'>Dividend Yield: N/A</span>", unsafe_allow_html=True)
    st.write(f"<span style='color:white;'>Beta: {beta:.2f}</span>" if beta else "<span style='color:white;'>Beta: N/A</span>", unsafe_allow_html=True)
    st.write(f"<span style='color:white;'>Market Cap: ${market_cap:.2f}T</span>" if market_cap else "<span style='color:white;'>Market Cap: N/A</span>", unsafe_allow_html=True)

    # Volumen
    st.subheader("Volumen")
    volume_color = 'green' if current_volume > avg_volume else 'red'
    st.markdown(f"<span style='color:{volume_color};'>Volumen: {current_volume/1e3:.0f}K</span>", unsafe_allow_html=True)  # Volumen en miles
    st.write(f"Volumen promedio: {avg_volume/1e3:.0f}K")  # Volumen promedio en miles

# Input de usuario
ticker = st.text_input("Ingrese el ticker (ej. GGAL.BA):", "GGAL.BA")
if ticker:
    create_panel(ticker)

