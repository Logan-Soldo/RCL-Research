# -*- coding: utf-8 -*-
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

def read_file(station,station_fill):
    print(station)
    while True:
        try:
            data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\Stations\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True,na_values=[" "," S"," T"," M"]).fillna(0)
            print(data)
     #       data = data.replace('S',0)

        except:
            print("Problem Finding File. Exiting")
            break
        
        data['PRCP'] = data['PRCP'].astype(str)
   #     data = data.PRCP.str.extract(r'(?P<PRCP>[0-9.0-9]*)(?P<STR>[A]{0,1})',expand=True)
        data['PRCP'] =  data['PRCP'].str.extract('([+-.0-9]+)(.*)').rename(columns={0:'PRCP', 1:'UNIT'})

        data['PRCP'] = pd.to_numeric(data.PRCP,errors='coerce')
        data = data.set_index(['DATE'])
     #   data = data.loc['1950-01-01':'2019-12-31']        # 70 year period of record...
        data = data.loc['1900-01-01':'2019-12-31']        # Extended long term period of record...
        data.reset_index(level=0,inplace=True)
        print(data[['DATE','PRCP']])
        return data[['DATE','PRCP']]

def main():
#    station_list = ['New Brunswick']
    station_list = [['Coastal South','Atlantic City'],
                    ['Northwest','Newton'],
                    ['Central'],
                    ['Northeast','Dover'],
                    ['Coastal North'],
                    ['Southwest']]    
#    station_list = ['Northeast']
    
    for station in station_list:
        data = read_file(station)