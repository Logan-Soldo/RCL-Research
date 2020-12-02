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
                data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\Stations\MainData\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True,na_values=[" "," M"])
            elif method =="fill":
                data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\Stations\Fill_In\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True,na_values=[" "," M"])
            data = data.replace(' T',0)
        except:
            print("Problem Finding File. Exiting")
            break
        data['PRCP'] = np.where(data['PRCP']==" S",0,data['PRCP'])
        data['PRCP'] = np.where(data['PRCP'] == " T",0,data['PRCP'])
        
        data['PRCP'] = data['PRCP'].astype(str)
        data['PRCP'] = data['PRCP'].str.extract('([+-.0-9]+)(.*)').rename(columns={0:'PRCP', 1:'UNIT'})
        

        data['PRCP'] = pd.to_numeric(data.PRCP,errors='coerce')
        data = data.set_index(['DATE'])
        data = data.loc['1900-01-01':'2019-12-31']        # Extended long term period of record...
        
        data.reset_index(level=0,inplace=True)

        return data

def fill_file(station_list):
    main_file = read_file(station_list[0],"main")
    main_file = main_file.set_index('DATE')
    temp = pd.date_range(start = '1900-01-01',end='2019-12-31')
    main_file = main_file.reindex(temp)
#    print(main_file)
    if len(station_list) > 1:
        counter=1
        for runs in station_list[1:]:
            fill_file = read_file(station_list[counter],"fill")
            fill_file = fill_file.set_index('DATE')
            temp = pd.date_range(start = '1900-01-01',end='2019-12-31')        
            fill_file = fill_file.reindex(temp)
         #   print(fill_file)
            main_file=merge_file(main_file,fill_file)
            counter += 1

 
    main_file = main_file.reset_index()
    main_file.columns = ['DATE','NAME','PRCP']
    main_file = main_file.set_index('DATE')
   # print(main_file)
    
    save_csv(main_file,station_list[0])
    miss = main_file.isnull()
    is_nan = miss.any(axis=1)
    nan_rows = main_file[is_nan]
    nan_rows.to_csv('E:\School\RutgersWork\DEP_Precip\Stations\Missing\%s_Missing.csv'%station_list[0])
    
    main_file['counter'] = np.where(main_file['PRCP'].isnull(),1,0)
#    main_file['filled'] = np.where(main_file['NAME'])
#    print(main_file)
    miss = main_file['counter'].sum()
    
    

 #   print(station_list[0],miss)
    return station_list[0],miss
    
def merge_file(df1,df2):
        mask = df1['PRCP'].isnull()
        df1.loc[mask,:] = df2.loc[mask,:] 
        df1['NAME'] = np.where(df1['PRCP'].isnull(),np.nan,df1['NAME'])
        return df1
def save_csv(df,station):
    df.to_csv('E:\School\RutgersWork\DEP_Precip\Stations\%s.csv'%station)
def main():
#    station_list = [['Northwest','Newton','Sussex Airport','High Point','Layton','Canistear Reservoir']]
    station_list = [['Atlantic City Marina','Atlantic City','Tuckerton','Northfield','Pleasantville'],
                    ['Sussex','Newton','Sussex Airport','High Point','Layton','Canistear Reservoir'],
                    ['New Brunswick','New Brunswick Experimental','New Brunswick(1)','Plainfield'],
                    ['Charlotteburg','Dover','Wanaque','Boonton','Newark Liberty','Paterson'],
                    ['Long Branch','Sandy Hook','Fort Hancock','Toms River','Freehold','New Brunswick','New Brunswick Experimental','New Brunswick(1)'],
                    ['Indian Mills','Pemberton','Hammonton','Clayton','Vineland','Moorestown']]    
    
    Region_list = ['Coastal South','Northwest','Central','Northeast','Coastal North','Southwest']
    stats=[]
    for station in station_list:
        main_station,data = fill_file(station)
        stats.append([main_station,data])
    print(stats)

if __name__ == "__main__":
    main()  