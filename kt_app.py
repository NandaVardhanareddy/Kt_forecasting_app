import numpy as np
import streamlit as st
import pandas as pd
import pickle
import tensorflow as tf
import keras
import math as m
from decimal import Decimal, getcontext


def make_forecast(sequence,model1,forecast_number):
    test_forecasts = []

    first_eval_batch = sequence
    current_batch = first_eval_batch.reshape((1, 5, 1))

    for i in range(forecast_number):
        # get the prediction value for the first batch
        current_pred = model1.predict(current_batch)[0]
    
        # append the prediction into the array
        test_forecasts.append(current_pred) 
    
        # use the prediction to update the batch and remove the first value
        current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)
        
    return test_forecasts
def convert_input_to_float_sequence(input_str):
    try:
        # Split the input string by commas and convert each element to float
        sequence = [float(value.strip()) for value in input_str.split(',')]
        return sequence
    except ValueError:
        return None 


def main():

    st.title('Solar Calculator & Clearness Index Forecast')
    model = tf.keras.models.load_model('D:\\KT\\forecast_KT_model1.h5')


    # taking input for calculations

    latitude = st.number_input('LATITUDE', step=0.01)
    longitude = st.number_input('LONGITUDE', step=0.01)
    julian_day = st.number_input('JULIAN DAY', step=1)
    hours_before_solar_noon = st.number_input('Hours before solar noon', step=0.01)
    wall_azimuth_angle = st.number_input('Wall Azimuth Angle', step=0.01)
    wall_area = st.number_input('Wall Area', step=0.01)
    surface_slope = st.number_input('surface slope',step=0.01)
    surface_orientation = st.number_input('surafce orientation(south = 0,west = +90)',step=0.01)

    

    # Angle calculations
    sh = 15*hours_before_solar_noon
    sd = (23.45)*(m.sin(m.radians(360*(julian_day - 81)/365)))
    se = m.degrees(m.asin(m.cos(m.radians(latitude)) *m.cos(m.radians(sd)) * m.cos(m.radians(sh)) + m.sin(m.radians( latitude)) * m.sin(m.radians(sd))))
    c = 90-se
    a = abs(1/(m.sin(m.radians(se))))
    od = 0.174 + 0.035*(m.sin(m.radians(360*(julian_day-100)/365)))
    sdf = 0.095 + 0.04*(m.sin(m.radians(360*(julian_day-100)/365)))

    # Radiation calculations
    p = 1370*(1 + 0.034*m.cos(360*julian_day/365)) #Extra Terrestrial Solar Insolation
    gd = p*m.exp((-1)*od*sdf) #Clear Sky Radiation
    aoi = m.cos(m.radians(se))*m.cos(m.radians(wall_azimuth_angle)) #Angle of incidence
    br = gd*aoi #Beam Radiation
    dr = gd*sdf #Diffused Radiation
    avg_pk_hr = 4.814 ## for kgp avg Peak Sun Hours
    tr_d = (br+dr)*avg_pk_hr #Total Radiation Per Day
    te = tr_d*wall_area #Total Energy

    #for a wall
    brw = gd*(m.cos(m.radians(surface_slope))+m.tan(m.radians(se))*m.cos(m.radians(surface_orientation)))
    trw = (brw*4.814 + dr*10)*wall_area

    if st.button('Results'):
        table1_data = {
            "Variable": ["Solar Hour Angle", "Solar Declination", "Solar Elevation", "Collector Tilt Angle", "Air Mass Ratio", "Optical Depth", "Sky Diffuse Factor"],
            "Value": [sh, sd, se, c, a, od, sdf]
        }

        table1_df = pd.DataFrame(table1_data)

        # Create DataFrame for the second table
        table2_data = {
            "Variable": ["Extra Terrestrial Solar Insolation", "Clear Sky Radiation", "Angle of incidence", "Beam Radiation", "Diffused Radiation", "avg Peak Sun Hours", "Total Radiation Per Day", "Total Energy",'Beam Radiation for a wall','Total Radiation per day for a wall'],
            "Value": [p, gd, aoi, br, dr, avg_pk_hr, tr_d, te,brw,trw]
        }

        table2_df = pd.DataFrame(table2_data)
        st.subheader("Table 1: Solar Data")
        st.table(table1_df)

        
        st.subheader("Table 2: Radiation")
        st.table(table2_df)


    st.write('Enter the past 5 days clearness index values:')
    d5 = st.number_input('Enter a kt value between 0 and 1(day -5)', step=0.01)
    d4 = st.number_input('Enter a kt value between 0 and 1(day -4)', step=0.01)
    d3 = st.number_input('Enter a kt value between 0 and 1(day -3)', step=0.01)
    d2 = st.number_input('Enter a kt value between 0 and 1(day -2)', step=0.01)
    d1 = st.number_input('Enter a kt value between 0 and 1(day -1)', step=0.01)
    input_sequence = np.array([d5, d4, d3, d2, d1]).reshape(5, 1)
    forecast_days = st.slider("Select the number of forecast days", 0, 15, value=5)
    if st.button('Forecast'):
        forecasted_values = make_forecast(input_sequence,model, forecast_days)
        st.write(f"Forecasted Clearness Index for the next {forecast_days} days:")
        df = pd.DataFrame({'Day': np.arange(1, forecast_days + 1), 'Clearness Index': forecasted_values})
        st.dataframe(df)
    


if __name__ == '__main__':
    main()












