import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.gridspec import GridSpec

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

    # Setup Streamlit layout
    st.title(f"Panel de Análisis para {ticker}")
    
    # Precio y variaciones
    st.subheader("Precio y Variaciones")
    st.write(f"Precio actual: ${current_price:.2f}")
    st.write(f"Variación diaria: {daily_var:.2f}%", color='green' if daily_var > 0 else 'red')
    st.write(f"Variación semanal: {weekly_var:.2f}%", color='green' if weekly_var > 0 else 'red')
    st.write(f"Variación mensual: {monthly_var:.2f}%", color='green' if monthly_var > 0 else 'red')
    st.write(f"Variación YTD: {ytd_var:.2f}%", color='green' if ytd_var > 0 else 'red')
    st.write(f"Variación anual: {annual_var:.2f}%" if annual_var is not None else "Variación anual: N/A", color='green' if (annual_var is not None and annual_var > 0) else 'red')

    # Gráfico de precios
    st.subheader("Gráfico de Precios")
    plt.figure(figsize=(10, 5))
    hist['Close'].plot(color='cyan')
    plt.title(f"Gráfico de {ticker}")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    st.pyplot(plt)

    # Análisis Fundamental
    st.subheader("Análisis Fundamental")
    st.write(f"P/E Ratio: {pe_ratio:.2f}" if pe_ratio else "P/E Ratio: N/A", color=color_indicator(pe_ratio, 15, 25))
    st.write(f"ROE: {roe:.2f}%" if roe else "ROE: N/A", color=color_indicator(roe, 15, 5))
    st.write(f"EPS: {eps:.2f}" if eps else "EPS: N/A", color=color_indicator(eps, 1, 0))
    st.write(f"Dividend Yield: {dividend_yield:.2f}%" if dividend_yield else "Dividend Yield: N/A", color=color_indicator(dividend_yield, 5, 2))
    st.write(f"Beta: {beta:.2f}" if beta else "Beta: N/A")
    st.write(f"Market Cap: ${market_cap:.2f}T" if market_cap else "Market Cap: N/A")

    # Volumen
    st.subheader("Volumen")
    volume_color = 'green' if current_volume > avg_volume else 'red'
    st.write(f"Volumen: {current_volume/1e3:.0f}K", color=volume_color)  # Volumen en miles
    st.write(f"Volumen promedio: {avg_volume/1e3:.0f}K")  # Volumen promedio en miles

# Input de usuario
ticker = st.text_input("Ingrese el ticker (ej. GGAL.BA):", "GGAL.BA")
if ticker:
    create_panel(ticker)
