import streamlit as st
import pandas as pd
import math
from pathlib import Path
import yfinance as yf
from datetime import timedelta
from datetime import datetime
from statistics import fmean 

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='stop-loss-analyzer',
    page_icon=':chart_with_downwards_trend:', # This is an emoji shortcode.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_tracker_names():
    """Grab tracker name data from a CSV file.
    https://github.com/paulperry/quant/blob/master/ETFs.csv
    Symbol,Name,Index,Description,Category,Provider"""
    tndftmp = pd.read_csv("trackernames.csv")
    return tndftmp

stock_df = get_tracker_names()

def date_range(start, end):
    res_date = start
    while res_date <= end:
        yield res_date
        res_date += timedelta(days=1)

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
selected_stock_symbol = selected_stock.split()[0]

#download the data
stock_data = yf.download(selected_stock, auto_adjust=True)

#cut out years without prices, '~' is numpy serial 'not'
stock_data = stock_data[(~stock_data["Close"][selected_stock_symbol].isnull())]
stock_data['Year'] = stock_data.index.year
min_value = stock_data.index.min().to_pydatetime()
max_value = stock_data.index.max().to_pydatetime()

from_year, to_year = st.slider(
    'Select a timeframe to analyze.',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value],
    format="DD/MM/YY")
analysis_time=to_year-from_year

 #Filter the data
t_filtered_stock_data = stock_data[
    (stock_data['Year'] <= int(to_year.year))
    & (int(from_year.year) <= stock_data['Year'])]
stock_price=pd.DataFrame()
stock_price["Close"]=t_filtered_stock_data["Close"][selected_stock_symbol]
stock_price["Low"]=t_filtered_stock_data["Low"][selected_stock_symbol]

st.header(selected_stock_symbol+' price over time')

st.line_chart(
    stock_price['Close'],
    y_label='price'
)

holding_time = st.slider("What is the expected holding time in days?",
                         min_value=1,
                         max_value=analysis_time.days,
                         value=30)

stoploss_percent_loss = st.slider("What stop-loss do you want to set in % price loss?",
                         min_value=0.0,
                         max_value=100.0,
                         value=7.0)

def getVal(df,col,row):
    try: return df[col][row]
    except KeyError:
        for i in range(1,30):
            try: return df[col][row+timedelta(days=i)]
            except KeyError:pass

def getSaveDate(df,date):
    for i in range(30):
        val=0
        try: val= df['Close'][date+timedelta(days=i)]
        except KeyError:pass
        if val !=0: return date+timedelta(days=i)
    return None

#st.write(stock_price)
used_abs=0
not_used_abs=0
sim_val_change_percent=[]
sim_nosl_val_change_percent=[]
maxsimstart=to_year-timedelta(days=holding_time)
for simstart in date_range(from_year,maxsimstart):
    safesimstart=getSaveDate(stock_price,simstart)
    safesimend=getSaveDate(stock_price,simstart+timedelta(days=holding_time))
    simstartval =getVal(stock_price,'Close',simstart)
    sellval=simstartval*(1-(stoploss_percent_loss/100))

    sim_nosl_val_change_percent.append(((stock_price['Close'][safesimend]-simstartval)/simstartval)*100)
    if stock_price['Low'][safesimstart:safesimend].min()>sellval:
        not_used_abs+=1
        sim_val_change_percent.append(((stock_price['Close'][safesimend]-simstartval)/simstartval)*100)
        continue
    for curr_val in stock_price['Low'][safesimstart:safesimend]:
        if curr_val<= sellval:
            used_abs+=1
            sim_val_change_percent.append(((curr_val-simstartval)/simstartval)*100)
            break

used_percent=(used_abs/(used_abs+not_used_abs))*100
without_sl_percent=fmean(sim_nosl_val_change_percent)
with_sl_percent=fmean(sim_val_change_percent)

txt_str= f"A {stoploss_percent_loss:.2f} \% stop-loss would have been used in {used_percent:.2f} \% of cases.\n\n"
if without_sl_percent >0:
    without_sl_txt = f"{without_sl_percent:.2f} \% gain"
else: without_sl_txt = f"{without_sl_percent:.2f} \% loss"
if with_sl_percent >0:
    with_sl_txt = f"{with_sl_percent:.2f} \% gain"
else: with_sl_txt = f"{with_sl_percent:.2f} \% loss"
txt_str += "This stop-loss would have turned a "+without_sl_txt +" into a "+ with_sl_txt +" (on average)."
st.write(txt_str)
#st.line_chart(
#    stock_price['Close'],
#    y_label='price'
#)