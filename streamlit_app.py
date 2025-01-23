
import streamlit as st
import pandas as pd
import math
from pathlib import Path
import numpy as np

st.set_page_config(
    page_title='Disruption prediction',
    page_icon=':train:'
)

@st.cache_data
def get_ns_data():
   
    raw_ns_df = pd.read_csv('df_streamlit_updated.csv')
    ns_df = raw_ns_df.rename(columns = {"rdt_id" : "nb_disruptions"})

    ns_df['start_time'] = pd.to_datetime(ns_df['start_time'])
    ns_df['start_time'] = ns_df['start_time'].dt.date

    return ns_df

ns_df = get_ns_data()

''
calender_2024 = pd.read_csv('Calender_2024.csv')

calender_2024['date_date'] = pd.to_datetime(calender_2024['date_date'])
calender_2024['date_date'] = calender_2024['date_date'].dt.date

min_value = calender_2024['date_date'].min()
max_value = calender_2024['date_date'].max()

import datetime

d = st.date_input(
    'Which date are you interested in?',
    min_value=min_value,
    max_value=max_value)
st.write('Selected date is:', d)


provinces = np.sort(ns_df['NUTS_2_0'].unique())


selected_province = st.multiselect(
    'Which province would you like to check?',
    provinces)
    #, ['Noord-Brabant', 'Utrecht', 'Gelderland', 'Groningen',
     #  'Limburg (NL)', 'Drenthe', 'Overijssel', 'Friesland (NL)',
      # 'Noord-Holland', 'Zuid-Holland', 'Zeeland', 'Flevoland'])

if not len(selected_province):
    st.warning("Please select a province!")

filtered_ns_df = ns_df[
        (ns_df['NUTS_2_0'].isin(selected_province))]

stations = np.sort(filtered_ns_df["name_long"].unique())

selected_stations = st.multiselect(
    'Which station are you intrested in?',
    stations)

filtered_ns_df_station = filtered_ns_df[
        (filtered_ns_df['name_long'].isin(selected_stations))]
''
if not len(selected_stations):
    st.warning("Please select a station!")

else:

    filtered_ns_df_station["start_time"] = pd.DatetimeIndex(filtered_ns_df_station["start_time"])

    df_timeseries = filtered_ns_df_station.resample("D", on = "start_time").agg({"nb_disruptions" : "nunique"}).reset_index()


    from prophet import Prophet

    m = Prophet()
    m.fit(df_timeseries.rename(columns={"start_time": "ds", "nb_disruptions": "y"}))

    future = m.make_future_dataframe(periods=500, freq="d")

    forecast = m.predict(future)

    fig1 = m.plot(forecast)


    d = pd.to_datetime(d)
    d = d.strftime("%Y-%m-%d")

    prediction_on_day = round(forecast["yhat"].values[forecast["ds"][forecast["ds"] == d].index][0], 2)


    sentence = f'Predicted number of disruptions in {", ".join(selected_stations)} on {d} is {prediction_on_day}'
    ''
    st.header(sentence)

    ''
