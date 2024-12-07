import streamlit as st
import pandas as pd
import math
from pathlib import Path
import yfinance as yf

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='stop-loss-analyzer',
    page_icon=':chart_with_downwards_trend:', # This is an emoji shortcode.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_tracker_names():
    """Grab GDP data from a CSV file."""
    #https://github.com/paulperry/quant/blob/master/ETFs.csv
    tndftmp = pd.read_csv("trackernames.csv")
    # Symbol,Name,Index,Description,Category,Provider
    return tndftmp

stock_df = get_tracker_names()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :chart_with_downwards_trend: Stop-Loss Analyzer
'''

#stock symbols and names
stock_df['symbol_and_name'] = stock_df['Symbol'] +"   "+ stock_df['Name']
stock_names = stock_df['symbol_and_name']
# good defaults: ['ACWI','IVV', 'VWO']
default_index = int(stock_df['Symbol'][stock_df['Symbol']=='ACWI'].index[0])
selected_stock = st.selectbox(
    'Which etf would you like to analyze?',
    stock_names,
    index=default_index)

stock_data = yf.download(selected_stock, auto_adjust=True)
st.write(stock_data)

stock_data['Year'] = stock_data.index.year
min_value = stock_data['Year'].min()
max_value = stock_data['Year'].max()

from_year, to_year = st.slider(
    'Select a timeframe to analyze.',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

 #Filter the data
filtered_stock_data = stock_data[
    (stock_data['Year'] <= to_year)
    & (from_year <= stock_data['Year'])]
st.write(filtered_stock_data)

#st.header('GDP over time', divider='gray')

#st.line_chart(
#    filtered_gdp_df,
#    x='Year',
#    y='GDP',
#    color='Country Code',
#)

#first_year = gdp_df[gdp_df['Year'] == from_year]
#last_year = gdp_df[gdp_df['Year'] == to_year]

