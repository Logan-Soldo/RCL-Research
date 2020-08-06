'''
Written on 08/05/2020 By Logan Soldo
Last Updated on 08/06/2020 By Logan Soldo


The purpose of this program is to analyze and display Precipitation data in NJ.
    Currently this program is only for New Brunswick.

Note: Data is in inches.
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime
import math


def read_file(station):
    while True:
        try:
            data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True)
            data = data.set_index(['DATE'])
            data = data.loc['1969-01-01':'2019-12-31']
            data.reset_index(level=0,inplace=True)
            print(data[['DATE','PRCP','SNOW','SNWD']])
            return data[['DATE','PRCP','SNOW','SNWD']]
        except:
            print("Problem Finding File. Exiting")
            break

def data_analysis(df):
#    df = df[df.columns[3:]]
    df=df.set_index('DATE')
    total_precip = df.groupby(df.index.year).sum()
    calc = 'Total Precipitation'
    print(total_precip)
    plotting(total_precip,calc)
    
    df.reset_index(level=0,inplace=True)
    bins = binning(df)

def binning(df):
    bins = pd.DataFrame(df['DATE'])
    bins['Days >0.5'] = np.where((df['PRCP'] > 0.5),1,0)
    bins['Days >1.0'] = np.where((df['PRCP'] > 1.0),1,0)
    bins['Days >1.5'] = np.where((df['PRCP'] > 1.5),1,0)
    bins['Days >2.0'] = np.where((df['PRCP'] > 2.0),1,0)
    bins['Days >2.5'] = np.where((df['PRCP'] > 2.5),1,0)
   

  #  print(bins['Days >0.5'].cumsum())
    bins = bins.set_index('DATE')     
    group = bins.groupby(bins.index.year).cumsum()  # accumulating days above a base value throughout the year
    print(group)
    calc = 'Bin Progression'
    plotting(group,calc)
    
    yearly_bin = bins.groupby(bins.index.year).sum() # sum of days above base by year
    calc = 'Bins'
    print(yearly_bin)
    plotting(yearly_bin,calc)

def plotting(df,calc):
    df.reset_index(level=0,inplace=True)
    if calc == 'Total Precipitation':
        df.plot('DATE','PRCP',kind='scatter')
    if calc == 'Bins':    # sum of days above base by year
        _,ax = plt.subplots()
        width = 0.70
        
        
        df.plot('DATE',y='Days >0.5',width=width,ax=ax,kind='bar')
        df.plot('DATE',y='Days >1.0',width=width,ax=ax,kind='bar',color='red')
        df.plot('DATE',y='Days >1.5',width=width,ax=ax,kind='bar',color='green')
        df.plot('DATE',y='Days >2.0',width=width,ax=ax,kind='bar',color='yellow')
        df.plot('DATE',y='Days >2.5',width=width,ax=ax,kind='bar',color='purple')


        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))        

        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        
        fmtr = ticker.IndexFormatter(range(1969,2020))
        ax.xaxis.set_major_formatter(fmtr)   
        
        ax.tick_params(axis='both', which='major', labelsize=10)        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.xaxis.label.set_visible(False)
    if calc == 'Bin Progression':
        df.plot('DATE',y=['Days >0.5'],kind='line')
      
        

def main():
    station = 'NewBrunswick'
    data = read_file(station)
    data_analysis(data)

    
if __name__ == "__main__":
    main()  