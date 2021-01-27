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

def read_file(station,method,pairing,start_year):
    print(station)
    while True:
        try:
            if method == "main":
                data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\Stations\MainData\%s\%s.csv'%(pairing,station),parse_dates=['DATE'],infer_datetime_format=True,na_values=[" "," M"])
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
#        data = data.loc['1900-01-01':'2019-12-31']        # Extended long term period of record...
        data = data.loc[start_year:'2019-12-31']          # Shorter time period for some stations is acceptable     
        data.reset_index(level=0,inplace=True)

        return data

def fill_file(station_list,region,pairing,start_year):
    main_file = read_file(station_list[0],"main",pairing,start_year)
    main_file = main_file.set_index('DATE')
#    temp = pd.date_range(start = '1900-01-01',end='2019-12-31')
    temp = pd.date_range(start = start_year,end='2019-12-31')   # Shorter time period for some stations is acceptable     

    main_file = main_file.reindex(temp)
    if len(station_list) > 1:
        counter=1
        for runs in station_list[1:]:
            fill_file = read_file(station_list[counter],"fill",pairing,start_year)
            fill_file = fill_file.set_index('DATE')
 #           temp = pd.date_range(start = '1900-01-01',end='2019-12-31')  
            temp = pd.date_range(start = start_year,end='2019-12-31')    # Shorter time period for some stations is acceptable         

            fill_file = fill_file.reindex(temp)
            main_file=merge_file(main_file,fill_file)
            counter += 1

 
    main_file = main_file.reset_index()
    main_file.columns = ['DATE','NAME','PRCP']
    main_file = main_file.set_index('DATE')

    print(main_file)    
    save_csv(main_file,station_list[0],region)      # Saving CSV
    
    miss = main_file.isnull()
    is_nan = miss.any(axis=1)
    nan_rows = main_file[is_nan]
    nan_rows.to_csv('E:\School\RutgersWork\DEP_Precip\Stations\Missing\%s_Missing.csv'%region)
    
    main_file['counter'] = np.where(main_file['PRCP'].isnull(),1,0)
    miss = main_file['counter'].sum()
#        res = main_file.loc[main_file['NAME'] == station].value_counts()
    res = main_file.groupby([main_file.index.year,'NAME']).size().unstack(fill_value=0.0)
    res = res.div(res.sum(axis=1),axis=0).mul(100).round(2)
    res = res.reindex(columns = station_list)
    res.to_csv('E:\School\RutgersWork\DEP_Precip\Stations\Station Statistics\%s_StationPercentage.csv'%region)
    print(res)
    
    
    return region,miss
    
def merge_file(df1,df2):
      mask = df1['PRCP'].isnull()
      df1.loc[mask,:] = df2.loc[mask,:] 
      df1['NAME'] = np.where(df1['PRCP'].isnull(),np.nan,df1['NAME'])
      return df1
    
def save_csv(df,station,region):
    df.to_csv('E:\School\RutgersWork\DEP_Precip\Stations\StationOutput\%s\%s.csv'%(region,station))
    
def main():
    
    pairing = int(input("Which pairing would you like to process? (1 or 2): "))    # This pairing number is set to be matched with another station witihin the region.
    
    if pairing == 1:
#    station_list = [['Sussex','Newton','Sussex Airport','High Point','Layton','Canistear Reservoir']]
        station_list = [['Atlantic City Marina','Atlantic City','Tuckerton','Northfield','Pleasantville'], # Coastal South
                         ['Sussex','Newton','Sussex Airport','High Point','Layton','Canistear Reservoir'],  # Northwest
                         ['New Brunswick','New Brunswick Experimental','New Brunswick(1)','Plainfield'],   # Central
                         ['Charlotteburg','Oak Ridge Reservoir','Dover','Wanaque','Boonton','Greenwood Lake'],      # Need to adjust the stations used for filling in here. Want to compare high elevation Charlotteburg with lower elevation Newark.
                         ['Long Branch','Sandy Hook','Fort Hancock','Toms River','Sea Girt','Freehold-Marlboro','New Brunswick','New Brunswick Experimental','New Brunswick(1)'], # Coastal North
                         ['Indian Mills','Pemberton','Hammonton','Clayton','Vineland','Moorestown']]    # Southwest
        Region_list = ['Coastal South','Northwest','Central','Northeast','Coastal North','Southwest']
        start_year = '1900-01-01'

# Stations to be used for pairing and comparison.
    elif pairing == 2:
        station_list = [['Cape May','Belleplain State Forest'],   # Coastal South
                        ['Flemington','Wertsville','Lambertville'], # Northwest  
                        ['Hightstown','Princeton Water Works','Trenton-Mercer'],  # Central
                        ['Newark Liberty','Paterson'], # Northeast
                        ['Freehold-Marlboro','Lakehurst'], #Coastal North
                        ['Moorestown','Philadelphia Airport']] # Southwest
    
        Region_list = ['Coastal South','Northwest','Central','Northeast','Coastal North','Southwest' ]        
        start_year = '1950-01-01'
    
    count = 0
    region_dict = {}
    for r in Region_list:
        d = {r:station_list[count]}
        region_dict.update(d)
        count += 1
    stats=[]
    print(d)
    for region,station in region_dict.items():
        print(region,station)
        main_station,data = fill_file(station,region,pairing,start_year)
        stats.append([main_station,data])
    print(stats)

if __name__ == "__main__":
    main()  