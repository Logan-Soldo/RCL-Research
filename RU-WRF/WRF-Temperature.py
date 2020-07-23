'''
Written on 07/23/2020 By Logan Soldo
This program borrows HEAVILY from an RUCOOL tutorial 
    by Lori Garzio at Rutgers University (https://github.com/rucool/wind-energy-tutorials)
    
This script accesses RU-WRF temperature point data through THREDDS and extracts the data
to a csv file. The stations used for this script are hardcoded in, 
but can be changed in Main function to fit the user's needs.
'''
# import the required packages for data access and plotting
import datetime as dt
import xarray as xr
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import time


def read_data(lat,lon,station):
    # data url
    wrf_file = 'http://tds.marine.rutgers.edu/thredds/dodsC/cool/ruwrf/wrf_4_1_3km_processed/WRF_4.1_3km_Processed_Dataset_Best'    
    # save file directory - change this to a local directory
    save_dir = 'E:/School/RutgersWork/DegreeDayAnalysis/RU-WRF/Testing'
    loc = dict(lon=lon, lat=lat)   
    # open the dataset
    ds = xr.open_dataset(wrf_file, mask_and_scale=False)    
    # start and end times for plotting
    start_time = dt.datetime(2019, 1, 1, 0, 0, 0)
    end_time = dt.datetime(2019, 12, 31, 23, 0, 0)    
    # subset based on time
    ds = ds.sel(time=slice(start_time, end_time))    
    # grab the time, latitude, and longitude variables
    tm = ds['time']
    lon = ds['XLONG']
    lat = ds['XLAT']    
    # calculate the sum of the absolute value distance between the model location and buoy location
    a = abs(lat - loc['lat']) + abs(lon - loc['lon'])    
    # find the indices of the minimum value in the array calculated above
    i, j = np.unravel_index(a.argmin(), a.shape)   
    # get the data for Air Temperature at 2m at the first timestamp in the time array
    #t = tm[0]  # grab the first timestamp
    data_lst = []
    for idx, t in enumerate(tm.values):
        T2 = ds.T2.sel(time=t)[i,j]
        varname = T2.long_name
    
    # convert K to F
        T2 = T2.values * 9 / 5 - 459.67
        
        data_lst.append([t,T2])
    data_df = pd.DataFrame(data_lst)
    to_daily(data_df,save_dir,station)
  #  save_csv(data_df,save_dir,station)

def to_daily(df,save_dir,station):
 #   print(df.dtypes)
    df.index= pd.to_datetime(df[0])
    df = df.drop(0,axis=1)
    mean_dat = df.resample('D').mean()
    max_dat = df.resample('D').max()
    min_dat = df.resample('D').min()
    daily = pd.concat([max_dat,min_dat,mean_dat],axis=1)
    daily = daily.reset_index()
    daily.columns = ['Date','max','min','average']
    print(daily)
    save_csv(daily,save_dir,station)
def save_csv(df,save_dir,station):
    df.to_csv(save_dir + '/%s.csv'%station)
def main():    
    # Station Location
    d = {'CreamRidge':[40.118553, -74.525634],
         'Howell':[40.192056, -74.196238 ],
         'SeaGirt':[40.120448, -74.032816],
         'Wall':[40.155004, -74.072705 ]}
    for i,j in d.items():
        start = time.time()
        lon = j[0]
        lat = j[1]
        read_data(lon,lat,i)
        end = time.time()
        elapsed = (start-end)/60
        print("%s finished in %s minutes"%(i,elapsed))
if __name__ == "__main__": 
    main() 
        
        
        
# coordinates = [[40.120448, -74.032816]]

# for i in range(len(coordinates)):
#     lat = coordinates[i][0]
#     lon = coordinates[i][1]
#     read_data(lat,lon,i)
    


    