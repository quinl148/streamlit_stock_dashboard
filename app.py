import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

st.title("Stock Dashboard")

ticker = st.sidebar.text_input('Enter Ticker Symbol:', value="MSFT")
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')


# Ensure valid date selection
if start_date >= end_date:
    st.error("End date must be after start date")
else:
    # Download stock data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        st.error("No data found. Check the ticker symbol and date range.")
    else:
        # Fix multi-index issue
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)  # Keep only first level of column names

        # Plot stock price data
        fig = px.line(data, x=data.index, y="Adj Close", title=ticker)
        st.plotly_chart(fig)

pricing_data, fundamental_data, news =  st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

with pricing_data:
    st.header('Price Movements')
    data2 = data
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1 
    data2.dropna(inplace= True)
    st.write(data2)
    annual_return = data2['% Change'].mean()*252*100
    st.write('Annual Return is ',round(annual_return, 2), '%')
    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write('Standard Deviation is ', round(stdev*100, 2), '%')
    st.write('Risk Adj. Return is ', round(annual_return / (stdev * 100), 2))


from alpha_vantage.fundamentaldata import FundamentalData
with fundamental_data:
    key = 'Q1IVP3VQWU9V2JLU'
    fd = FundamentalData(key, output_format = 'pandas')
    st.subheader('Balance Sheet')
    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)
    st.subheader('Income Statement')
    income_statement = fd.get_income_statement_annual(ticker)[0]
    is1 = income_statement.T[2:]
    is1.columns = list(income_statement.T.iloc[0])
    st.write(is1)
    st.subheader('Cash Flow Statement')
    cash_flow = fd.get_cash_flow_annual(ticker)[0]
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)

from stocknews import StockNews

with news:
    st.header(f'News of {ticker}')
    sn = StockNews(ticker, save_news=False)
    df_news = sn.read_rss()
    
    if not df_news.empty:  # Check if df_news has data
        df_news.reset_index(drop=True, inplace=True)  # Reset index if necessary
        
        for i in range(min(10, len(df_news))):  # Ensure you don't exceed the number of rows
            st.subheader(f'News {i+1}')
            st.write(df_news['published'][i])
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            title_sentiment = df_news['sentiment_title'][i]
            st.write(f'Title Sentiment: {title_sentiment}')
            news_sentiment = df_news['sentiment_summary'][i]
            st.write(f'News Sentiment: {news_sentiment}')
    else:
        st.write("No news available.")
