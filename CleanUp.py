import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option("display.max_rows", 40)   
pd.set_option("display.min_rows",20) 
pd.set_option('display.max_columns', 10)
#pd.set_option('display.min_columns', 10)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)   


data = pd.read_excel('E:\School\RutgersWork\TRANSCOM\RAWS_elements_example_June9_2020.xlsx')   # Reading in the raw file

# Listing only the columns that are needed.
column_list = ['STID/__text','NAME/__text','STATE/__text','LATITUDE/__text','LONGITUDE/__text','ELEVATION/__text',
               'OBSERVATIONS/solar_radiation_value_1/value/__text','OBSERVATIONS/wind_gust_value_1/value/__text',
               'OBSERVATIONS/wind_cardinal_direction_value_1d/value/__text','OBSERVATIONS/peak_wind_direction_value_1/value/__text',
               'OBSERVATIONS/precip_accum_value_1/value/__text','OBSERVATIONS/wind_direction_value_1/value/__text',
               'OBSERVATIONS/fuel_moisture_value_1/value/__text','OBSERVATIONS/fuel_temp_value_1/value/__text',
               'OBSERVATIONS/peak_wind_speed_value_1/value/__text','OBSERVATIONS/dew_point_temperature_value_1d/value/__text',
               'OBSERVATIONS/air_temp_value_1/value/__text','OBSERVATIONS/wind_speed_value_1/value/__text',
               'OBSERVATIONS/relative_humidity_value_1/value/__text','OBSERVATIONS/heat_index_value_1d/value/__text',
               'OBSERVATIONS/soil_moisture_value_1/value/__text','OBSERVATIONS/pressure_value_1/value/__text',
               'OBSERVATIONS/soil_temp_value_1/value/__text']


clean_data = data[column_list]       #Selecting the columns that are needed.

clean_data.columns = ['STID','NAME','STATE','LATITUDE','LONGITUDE','ELEVATION','Solar_Radiation','Wind_Gust','Wind_Cardinal_Direction',
                      'Peak Wind Direction','Precip_Accum','Wind_Direction','Fuel_Moisture','Fuel_Temp','Peak_Wind_Speed',
                      'Dew_Point_Temperature','Air_Temp','Wind_Speed','Relative_Humidity','Heat_Index','Soil_Moisture',
                      'Pressure_Value','Soil_Temp']
print(clean_data)
clean_data.to_excel('RAWS_elements_cleanup_test.xlsx')