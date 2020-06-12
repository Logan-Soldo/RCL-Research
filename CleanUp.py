import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option("display.max_rows", 40)   
pd.set_option("display.min_rows",20) 
pd.set_option('display.max_columns', 8)
#pd.set_option('display.min_columns', 10)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)   

def read_data():
    data = pd.read_excel('E:\School\RutgersWork\TRANSCOM\Mesowest_Network_elements_June11_2020.xlsx')   # Reading in the raw file
    
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
  #  print(clean_data)
    return clean_data

def read_inventory():
    inv_df = pd.read_excel('E:\School\RutgersWork\TRANSCOM\TRANSCOM_mesonet_inventory.xlsx')
   # print(inv_df)
    return inv_df

def sort_df(df1,df2):
    merge = pd.merge(df1,df2, on=['NAME'],how='inner')
    merge['NETWORK_UPPER'] = merge['Network'].str.upper()
    merge['COUNTY_UPPER'] = merge['County'].str.upper()
    merge = merge.sort_values(['NETWORK_UPPER','COUNTY_UPPER'],ignore_index=True)
    merge = merge[['Network','STID','NAME','Milepost','County','STATE','LATITUDE','LONGITUDE','ELEVATION','Station type/location',
                          'Solar_Radiation','Wind_Gust','Wind_Cardinal_Direction',
                          'Peak Wind Direction','Precip_Accum','Wind_Direction','Fuel_Moisture','Fuel_Temp','Peak_Wind_Speed',
                          'Dew_Point_Temperature','Air_Temp','Wind_Speed','Relative_Humidity','Heat_Index','Soil_Moisture',
                          'Pressure_Value','Soil_Temp']]
    print(merge)
    to_excel(merge)
def to_excel(df):
    df.to_excel('TRANSCOM_elements_cleanup.xlsx')
    

def main():
    df1 = read_data()
    df2 = read_inventory()
    sort_df(df1,df2)
    
if __name__ == "__main__":
    main()  