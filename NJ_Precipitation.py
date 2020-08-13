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

def data_analysis(df,station):
    '''
    Reads in a dataframe and a station specified in main.
    This function is where all the general data analysis will take place, 
    but more involved calculations will be sent to other fucnctions for 
    organization.

    '''
    df=df.set_index('DATE')
    total_precip = df.groupby(df.index.year).sum()
    calc = 'Total Precipitation'
   # print(total_precip)
    plotting(total_precip,calc,station)                 # Plotting Total Precip
    
    df.reset_index(level=0,inplace=True)    
    bins = binning(df,station)              # Dividing data into bins and then plotting.
    
    Precip_events(df,station)

def binning(df,station):
    bins = pd.DataFrame(df['DATE'])
    bins['>0.0'] = np.where((df['PRCP'] > 0.0),1,0)
    bins['≥ 0.10'] = np.where((df['PRCP'] >= 0.10),1,0)
    bins['≥ 0.25'] = np.where((df['PRCP'] >= 0.25),1,0)
    bins['≥ 0.50'] = np.where((df['PRCP'] >= 0.50),1,0)
    bins['≥ 1.00'] = np.where((df['PRCP'] >= 1.00),1,0)
    bins['≥ 2.00'] = np.where((df['PRCP'] >= 2.00),1,0)
   

  #  print(bins['Days >0.5'].cumsum())
    bins = bins.set_index('DATE')     
    group = bins.groupby(bins.index.year).cumsum()  # accumulating days above a base value throughout the year
  #  print(group)
    calc = 'Bin Progression'
    plotting(group,calc,station)
    
    yearly_bin = bins.groupby(bins.index.year).sum() # sum of days above base by year
    calc = 'Days Above Base (in)'
#    print(yearly_bin)
    plotting(yearly_bin,calc,station)
    
    # calc = 'Monthly Sum of Days Above x'
    # month_bin = bins.groupby([(bins.index.year),(bins.index.month)]).sum()
    # plotting(month_bin,calc,station)
    # print(month_bin)
    
    
    percent = pd.DataFrame()   # Calculating percentage of precip days above base.
    calc = "Precentage of Precipitation Days At/Above Base (in)"
    yearly_bin = bins.groupby(bins.index.year).sum()
    percent['≥ 0.10'] = (yearly_bin['≥ 0.10']/yearly_bin['>0.0'])*100
    percent['≥ 0.25'] = (yearly_bin['≥ 0.25']/yearly_bin['>0.0'])*100
    percent['≥ 0.50'] = (yearly_bin['≥ 0.50']/yearly_bin['>0.0'])*100
    percent['≥ 1.00'] = (yearly_bin['≥ 1.00']/yearly_bin['>0.0'])*100
    percent['≥ 2.00'] = (yearly_bin['≥ 2.00']/yearly_bin['>0.0'])*100
   # print(percent)
    plotting(percent,calc,station)

def Precip_events(df,station):
    '''
    Reads in DataFrame from the data analysis function.
    
    Creates a new DataFrame with the goal of identifying consecutive 
    precipitation days.

    '''
    events = pd.DataFrame(df['DATE'])
    events['Precip Days'] = np.where((df['PRCP'] > 0.0),1,0)
    #events['Consecutive Above 0.5in'] = np.where((df['PRCP'] > 0.5),1,0)
    events['Count'] = np.where(events['Precip Days'].eq(1),events.groupby(events['Precip Days'].ne(events['Precip Days'].shift()).cumsum()).cumcount() +1,0)
   # events['Count 0.5'] = np.where(events['Consecutive Above 0.5in'].eq(1),events.groupby(events['Consecutive Above 0.5in'].ne(events['Consecutive Above 0.5in'].shift()).cumsum()).cumcount() +1,0)

    events = events.set_index('DATE')     
    group = events.groupby(events.index.year).max().reset_index()    
    print(group)
    calc = "Consecutive Days With Precipitation"
    plotting(group,calc,station)

    
def plotting(df,calc,station):
    
    c = color_select()
    for i in range(len(c)):
        r,g,b = c[i]
        c[i] = (r / 255., g / 255., b / 255.)
        
    df.reset_index(level=0,inplace=True)
    if calc == 'Total Precipitation':                   # Plotting the total Precipitation per year.
        _,ax = plt.subplots()
        width = 0.70
        df.plot('DATE',y='PRCP',width=width,ax=ax,kind='bar',color=c[4])
        plot_format(ax,station,calc)
        savefig(station,calc)
    if calc == 'Days Above Base (in)':    # sum of days above base by year
        _,ax = plt.subplots()
        width = 0.70
        
        df.plot('DATE',y='≥ 0.10',width=width,ax=ax,kind='bar',color=c[0])
        df.plot('DATE',y='≥ 0.25',width=width,ax=ax,kind='bar',color=c[1])
        df.plot('DATE',y='≥ 0.50',width=width,ax=ax,kind='bar',color=c[2])
        df.plot('DATE',y='≥ 1.00',width=width,ax=ax,kind='bar',color=c[3])
        df.plot('DATE',y='≥ 2.00',width=width,ax=ax,kind='bar',color=c[4])

        plot_format(ax,station,calc)
        savefig(station, calc)


        _,ax2 = plt.subplots()                          # Plotting only the number of days with precip above 0.0.
        calc = 'Days With Precipitation'
        df.plot('DATE',y='>0.0',width=width,ax=ax2,kind='bar',color='blue')
        
        plot_format(ax2,station,calc)
        savefig(station, calc)    
    
    if calc == "Precentage of Precipitation Days At/Above Base (in)":           # Plotting based on binned days calculated as a percentage.
        _,ax = plt.subplots()
        width = 0.70
        
        df.plot('DATE',y='≥ 0.10',width=width,ax=ax,kind='bar',color=c[0])
        df.plot('DATE',y='≥ 0.25',width=width,ax=ax,kind='bar',color=c[1])
        df.plot('DATE',y='≥ 0.50',width=width,ax=ax,kind='bar',color=c[2])
        df.plot('DATE',y='≥ 1.00',width=width,ax=ax,kind='bar',color=c[3])
        df.plot('DATE',y='≥ 2.00',width=width,ax=ax,kind='bar',color=c[4])

        plot_format(ax,station,calc)
        savefig(station, calc)        

    if calc == "Consecutive Days With Precipitation":
        _,ax = plt.subplots()
        width = 0.70
        df.plot('DATE',y='Count',width=width,ax=ax,kind='bar',color=c[4])
        plot_format(ax,station,calc)        
        savefig(station, calc)        

def plot_format(ax,station,calc):
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    
    fmtr = ticker.IndexFormatter(range(1969,2020))
    ax.xaxis.set_major_formatter(fmtr)   
    ylim = ax.get_ylim()
    ymax = round_up(ylim[1],-1)
    ax.set_ylim(0,ymax)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=8)
    ax.set_title('%s: %s'%(station,calc))


    if calc == 'Days Above Base (in)':    # sum of days above base by year
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
        ax.set_ylabel("Days")
    
    elif calc == 'Days With Precipitation':        
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))        
        ax.legend().set_visible(False)
        ax.set_ylabel("Days")
    
    elif calc == 'Total Precipitation':        
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))        
        ax.legend().set_visible(False)
        ax.set_ylabel("Precipitation (in)")
      
    elif calc == "Precentage of Precipitation Days At/Above Base (in)":        
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))        
        ax.set_ylabel("Percentage")
        ax.yaxis.label.set_visible(False)            
        ax.set_ylim([0,100])
        ax.set_title('%s: Precentage of Precipitation Days \n At/Above Base (in)'%(station))
        
    elif calc == "Consecutive Days With Precipitation":
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.legend().set_visible(False)
        ax.set_ylabel("Days")
        ax.set_ylim([0,15])
        ax.set_title('%s: Maximum Consecutive Days \n with Precipitation'%(station))
                
       

      
    ax.tick_params(axis='both', which='major', labelsize=10) 
#  ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=8)
    ax.xaxis.label.set_visible(False)    

def color_select():
    '''
    This function is called to generate colors for graphing.
    Color maps can be found here: 
    https://tableaufriction.blogspot.com/2012/11/finally-you-can-use-tableau-data-colors.html
    '''
    
    tableau20blind = [(0, 107, 164), (255, 128, 14), (171, 171, 171), (89, 89, 89),
             (95, 158, 209), (200, 82, 0), (137, 137, 137), (163, 200, 236),
             (255, 188, 121), (207, 207, 207)]
    color_blind = [(215,25,28),(255,128,14),(89,89,89),(0,107,164)]
    color_blind2=[(166,97,26),(223,194,125),(140,206,129),(128,205,193),(1,133,113)]
    
    return color_blind2

def round_up(n,decimals=0):
    multiplier = 10**decimals
    return math.ceil(n*multiplier)/multiplier

def savefig(station,calc):    
    print("Saving Plot...")
#    plt.savefig("E:\\School\\RutgersWork\\DegreeDayAnalysis\\Plots\\%s\\%s%s%s.svg" %(time,time,base,method),format='svg')  # Need to vary this formatting between graphics.
    plt.savefig("E:\\School\\RutgersWork\\DEP_Precip\\Figures\\%s%s.jpg"%(station,calc[:10]),format='jpg',dpi=600,bbox_inches='tight')    
    plt.savefig("E:\\School\\RutgersWork\\DEP_Precip\\Figures\\%s%s.tif"%(station,calc[:10]),format='tif',dpi=600,bbox_inches='tight')    
    plt.show()
    print("Plot Saved!")  
    
def main():
    station = 'New Brunswick'
    data = read_file(station)
    data_analysis(data,station)

    
if __name__ == "__main__":
    main()  