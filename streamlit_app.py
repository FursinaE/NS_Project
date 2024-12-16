
import streamlit as st
import pandas as pd
import math
from pathlib import Path
import numpy as np

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Disruption prediction',
    page_icon=':train:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv('df_streamlit_updated.csv')

    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.rename(columns = {"rdt_id" : "nb_disruptions"})

    # Convert years from string to integers
    gdp_df['start_time'] = pd.to_datetime(gdp_df['start_time'])
    gdp_df['start_time'] = gdp_df['start_time'].dt.date

    return gdp_df

gdp_df = get_gdp_data()



# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :train: Prediction of number of disruptions by NS

'''

# Add some spacing
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


provinces = np.sort(gdp_df['NUTS_2_0'].unique())


selected_province = st.multiselect(
    'Which province would you like to check?',
    provinces)
    #, ['Noord-Brabant', 'Utrecht', 'Gelderland', 'Groningen',
     #  'Limburg (NL)', 'Drenthe', 'Overijssel', 'Friesland (NL)',
      # 'Noord-Holland', 'Zuid-Holland', 'Zeeland', 'Flevoland'])

if not len(selected_province):
    st.warning("Please select a province!")

filtered_gdp_df = gdp_df[
        (gdp_df['NUTS_2_0'].isin(selected_province))]

stations = np.sort(filtered_gdp_df["name_long"].unique())

selected_stations = st.multiselect(
    'Which station are you intrested in?',
    stations)

filtered_gdp_df_station = filtered_gdp_df[
        (filtered_gdp_df['name_long'].isin(selected_stations))]
''
if not len(selected_stations):
    st.warning("Please select a station!")

else:
    # Filter the data
    #filtered_gdp_df = gdp_df[
     #   (gdp_df['NUTS_2_0'].isin(selected_province))
    # & (gdp_df['Year'] <= to_year)
        # & (from_year <= gdp_df['Year'])
    # ]

    filtered_gdp_df_station["start_time"] = pd.DatetimeIndex(filtered_gdp_df_station["start_time"])

    df_timeseries = filtered_gdp_df_station.resample("D", on = "start_time").agg({"nb_disruptions" : "nunique"}).reset_index()


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
