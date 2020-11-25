"""
Creating a program to compare datasets and fill in...

This is tailored to be used with NJ_Precipitation.py, 
    but it can be used as a template for any dataset.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
from datetime import datetime
import math
from scipy.stats import linregress
from scipy.stats import stats

def read_file(station,method):
    print(station)
    while True:
        try:
            if method == "main":
                data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\Stations\MainData\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True,na_values=[" "," S"," T"," M"])
            elif method =="fill":
                data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\Stations\Fill_In\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True,na_values=[" "," S"," T"," M"])

        except:
            print("Problem Finding File. Exiting")
            break
        
        data['PRCP'] = data['PRCP'].astype(str)
        data['PRCP'] =  data['PRCP'].str.extract('([+-.0-9]+)(.*)').rename(columns={0:'PRCP', 1:'UNIT'})

        data['PRCP'] = pd.to_numeric(data.PRCP,errors='coerce')
        data = data.set_index(['DATE'])
        data = data.loc['1900-01-01':'2019-12-31']        # Extended long term period of record...
        data.reset_index(level=0,inplace=True)
   #     print(data)
        return data

def fill_file(station_list):
    main_file = read_file(station_list[0],"main")
    main_file = main_file.set_index('DATE')
    temp = pd.date_range(start = '1900-01-01',end='2019-12-31')
    main_file = main_file.reindex(temp)
#    print(main_file)
    if len(station_list) > 1:
        fill_file = read_file(station_list[1],"fill")
        fill_file = fill_file.set_index('DATE')
        temp = pd.date_range(start = '1900-01-01',end='2019-12-31')        
        fill_file = fill_file.reindex(temp)
     #   print(fill_file)
        
        mask = main_file['PRCP'].isnull()
        main_file.loc[mask,:] = fill_file.loc[mask,:]
 
    main_file = main_file.reset_index()
    main_file.columns = ['DATE','NAME','PRCP']
    main_file = main_file.set_index('DATE')
   # print(main_file)
    
    save_csv(main_file,station_list[0])

    main_file['counter'] = np.where(main_file['PRCP'].isnull(),1,0)
#    main_file['filled'] = np.where(main_file['NAME'])
    print(main_file)
    miss = main_file['counter'].sum()
 #   print(station_list[0],miss)
    return station_list[0],miss
    

def save_csv(df,station):
    df.to_csv('E:\School\RutgersWork\DEP_Precip\Stations\%s.csv'%station)
def main():
#    station_list = ['New Brunswick']
    station_list = [['Coastal South','Atlantic City'],
                    ['Northwest','Newton'],
                    ['Central','New Brunswick'],
                    ['Northeast','Dover'],
                    ['Coastal North','New Brunswick'],
                    ['Southwest','Pemberton']]    
  #  station_list = [['Coastal South','Atlantic City']]
    stats=[]
    for station in station_list:
        main_station,data = fill_file(station)
        stats.append([main_station,data])
    print(stats)

if __name__ == "__main__":
    main()  