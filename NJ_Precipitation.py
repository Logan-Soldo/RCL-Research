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
from scipy.stats import linregress
from scipy.stats import stats

def read_file(station):
    while True:
        try:
            data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True)
            data = data.set_index(['DATE'])
            data = data.loc['1950-01-01':'2019-12-31']
            data = data.fillna(0)
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
    
    # Precip_events(df,station)
    
   # rolling_mean(df,station)
    
    month_to_season_LUT(df,station)

    dry_intervals(df,station)
    
    cumulative_precip(df,station)
    
def rolling_mean(df,station):
    _,ax = plt.subplots()
    rolling = pd.DataFrame(df['DATE'])

    rolling['90 Day'] = df['PRCP'].rolling(window = 90).mean()
    print(rolling)
    rolling.reset_index(level=0,inplace=True)
    
    stats_calc = '90 Day'     
    #rolling = statistics(rolling,stats_calc)    # Broken, needs work.
    
    
    rolling.plot('DATE',y='90 Day',ax=ax,kind = 'line')
   # rolling.plot(y='y_reg')
    

def binning(df,station):
    bins = pd.DataFrame(df['DATE'])
    bins['>0.0'] = np.where((df['PRCP'] > 0.0),1,0)
    bins['≥ 0.10'] = np.where((df['PRCP'] >= 0.10),1,0)
    bins['≥ 0.25'] = np.where((df['PRCP'] >= 0.25),1,0)
    bins['≥ 0.50'] = np.where((df['PRCP'] >= 0.50),1,0)
    bins['≥ 1.00'] = np.where((df['PRCP'] >= 1.00),1,0)
    bins['≥ 2.00'] = np.where((df['PRCP'] >= 2.00),1,0)
   

    bins = bins.set_index('DATE')     
    group = bins.groupby(bins.index.year).cumsum()  # accumulating days above a base value throughout the year
    calc = 'Bin Progression'
    plotting(group,calc,station)
    
    yearly_bin = bins.groupby(bins.index.year).sum() # sum of days above base by year
    calc = 'Days Above Base (in)'
    plotting(yearly_bin,calc,station)

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
    events['Count'] = np.where(events['Precip Days'].eq(1),events.groupby(events['Precip Days'].ne(events['Precip Days'].shift()).cumsum()).cumcount() +1,np.nan)
    events2 = pd.DataFrame(df['DATE'])
    events2 = events.assign(
        key1=events.groupby(events["Count"].isnull())["Count"].transform("cumcount").cumsum()
    ).groupby("DATE")["Count"].max().dropna().reset_index()
    
    events2 = events2.set_index('DATE')     
    group = events2.groupby(events2.index.year).mean().reset_index()    
    print(group)
    calc = "Consecutive Days With Precipitation"
    plotting(group,calc,station)

def dry_intervals(df,station):
    '''
    This function was provided by Natalie Teale 
    and originally written in MatLab. It is HEAVILY modified here for use of Pandas.
    '''
    dry_intervals = pd.DataFrame(df[['DATE','PRCP']])
    _,ax = plt.subplots()

    for base in [0.5,0.25,0.0]:
        dry_intervals['Precip Days'] = np.where((dry_intervals['PRCP'] > base),1,0)     # Changing minimum depth to end "dry spell"
        dry_intervals['Count'] = np.where(dry_intervals['Precip Days'].eq(0),
                                          dry_intervals.groupby(dry_intervals['Precip Days'].ne(dry_intervals['Precip Days'].
                                                                                                shift()).cumsum()).cumcount() +1,np.nan)
        dry_intervals['dry_spells'] = np.where((dry_intervals['Count'].isnull()),1,0)
        dry_intervals['dry_count'] = np.where(dry_intervals['dry_spells'].eq(0),
                                          dry_intervals.groupby(dry_intervals['dry_spells'].ne(dry_intervals['dry_spells'].
                                                                                                shift()).cumsum()).cumcount() +1,np.nan)
        key1 = dry_intervals.assign(
            key1=dry_intervals.groupby(dry_intervals["dry_count"].isnull())["dry_count"].transform("cumcount").cumsum()
        ).groupby("key1")["dry_count"].max()
        key2 = dry_intervals.assign(
            key1=dry_intervals.groupby(dry_intervals["dry_count"].isnull())["dry_count"].transform("cumcount").cumsum()
        ).groupby("key1")["DATE"].max().dropna()
    
        dry_spell = pd.concat([key2,key1],axis=1).reset_index().dropna()
        dry_spell = dry_spell.drop(columns='key1')
        
        
        dry_spell.plot(x='DATE',y='dry_count',ax=ax,kind='hist',alpha=0.7)
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(365))
    # ax.xaxis.set_minor_locator(ticker.MultipleLocator(100))
    
    # fmtr = ticker.IndexFormatter(range(1950,2021))
    # ax.xaxis.set_major_formatter(fmtr) 
    # plt.tight_layout() 
# #    dry_spells = 
#     plt.show()

def cumulative_precip(df,station):
    '''
    This function counts how many days it takes to get to precip of x magnitude.

    '''
   # cumsum = pd.DataFrame(df['DATE'])
    df = df.set_index('DATE')
    cumsum = df.groupby(df.index.year)["PRCP"].cumsum()
    cumsum = cumsum.reset_index()
    cumsum['Day'] = cumsum['DATE'].dt.dayofyear
    df2 = cumsum[['DATE','PRCP','Day']]                 # Copying pandas dataframe instead of using a pandas series. VERY IMPORTANT.
    df2 = df2.set_index('DATE')
    
    df2['1in'] = df2[df2['PRCP'] >= 1.0]['Day']
    df2['5in'] = df2[df2['PRCP'] >= 5.0]['Day']
    df2['10in'] = df2[df2['PRCP'] >= 10.0]['Day']
    df2['20in'] = df2[df2['PRCP'] >= 20.0]['Day']
    df2['40in'] = df2[df2['PRCP'] >= 40.0]['Day']
    
    df2 = df2.groupby(df2.index.year).first().reset_index()
    df2=df2.drop(columns=['PRCP','Day'])
    print(df2)
    calc = 'Days to Accumulate x in'
    plotting(df2,calc,station)

    
def plotting(df,calc,station):
    
    c = color_select()
    for i in range(len(c)):
        r,g,b = c[i]
        c[i] = (r / 255., g / 255., b / 255.)
        
    df.reset_index(level=0,inplace=True)
    if calc == 'Total Precipitation':                   # Plotting the total Precipitation per year.
        _,ax = plt.subplots()
        width = 0.70
        stat_calc = 'PRCP'
#        lin_r = stats.pearsonr(x,df['PRCP'])
        df= statistics(df,stat_calc)

        
        df['PRCP'].plot(ax=ax,width=width,kind='bar',color=c[4])
        df['y_reg_pre'].plot(ax=ax,color="black",linewidth="1.5",linestyle="dashed")
        df['y_reg_post'].plot(ax=ax,color="black",linewidth="1.5",linestyle="dashed")
        
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
        stat_calc = ">0.0"
        df = statistics(df,stat_calc)
        
        df['y_reg_pre'].plot(ax=ax2,color='black',linewidth="1.5",linestyle="dashed")
        df['y_reg_post'].plot(ax=ax2,color='black',linewidth="1.5",linestyle="dashed")
        df['>0.0'].plot(ax=ax2,kind='bar',width=width,color='blue')
        
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

    if calc == "Seasonal Precipitation Totals":
        fig,axes = plt.subplots(2, 2,constrained_layout=True)
        fig.suptitle('%s: %s'%(station,calc))
        #_,ax = plt.subplots()
        width = 0.70
      #  df.plot('DATE',y=['DJF','MAM','JJA','SON'],width=width,ax=ax,kind='bar',color=[c[0],c[1],c[2],c[3]])
        # df.plot('DATE',y='DJF',width=width,ax=axes[0,0],kind='bar',color='gray')
        # df.plot('DATE',y='MAM',width=width,ax=axes[0,1],kind='bar',color='gray')
        # df.plot('DATE',y='JJA',width=width,ax=axes[1,0],kind='bar',color='gray')
        # df.plot('DATE',y='SON',width=width,ax=axes[1,1],kind='bar',color='gray')
        df.plot('DATE',y='JFM',width=width,ax=axes[0,0],kind='bar',color='gray')
        df.plot('DATE',y='AMJ',width=width,ax=axes[0,1],kind='bar',color='gray')
        df.plot('DATE',y='JAS',width=width,ax=axes[1,0],kind='bar',color='gray')
        df.plot('DATE',y='OND',width=width,ax=axes[1,1],kind='bar',color='gray')
        for i,ax in enumerate(fig.axes):
            calc = ['JFM','AMJ','JAS','OND']
            plot_format(ax,station,calc[i])
        savefig(station,calc)

    if calc == 'Days to Accumulate x in':
        fig,axes = plt.subplots(2, 2,constrained_layout=True)
        fig.suptitle('%s: %s'%(station,calc))
        width = 0.70
        df.plot(x='DATE',y='1in',kind= 'bar',ax=axes[0,0],color='blue')
        df.plot(x='DATE',y='5in',kind= 'bar',ax=axes[0,1],color='blue')
        df.plot(x='DATE',y='10in',kind= 'bar',ax=axes[1,0],color='blue')
        df.plot(x='DATE',y='20in',kind= 'bar',ax=axes[1,1],color='blue')
      #  df.plot(x='DATE',y='40in',kind= 'bar',ax=axes[1,1],color='blue')
        for i,ax in enumerate(fig.axes):
            calc = ['1in','5in','10in','20in']#,'40in']
            plot_format(ax,station,calc[i])


def plot_format(ax,station,calc):
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    
    fmtr = ticker.IndexFormatter(range(1950,2021))
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
        ax.set_ylim([90,ymax])

    elif calc == 'Total Precipitation':        
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax.tick_params(axis='x',labelrotation=90)      
        ax.legend().set_visible(False)
        ax.set_ylabel("Precipitation (in)")
        ax.set_ylim([25,ymax])
      
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
    elif (calc == "JFM") or (calc == "AMJ") or (calc == "JAS") or (calc == "OND"):
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))         
        ax.set_ylim([0,30])
        ax.legend().set_visible(False)
        ax.set_ylabel('Precipitation (in)')
        ax.set_title('%s'%calc)
    elif (calc =='1in') or (calc =='5in') or (calc =='10in') or (calc =='20in'):#,'40in']
        tick_calc = ymax/5
        minor_TC= tick_calc/4
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_calc))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_TC))  
   #     ax.set_ylim([1,365])
        ax.set_title('%s'%calc)
        ax.legend().set_visible(False)
        ax.set_ylabel('Days')
       

      
    ax.tick_params(axis='both', which='major', labelsize=10) 
#  ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=8)
    ax.xaxis.label.set_visible(False)    

def statistics(df,stat_calc):

        x=df['DATE'].values
        # regress = linregress(x,df[stat_calc])           # problem with using datetime
        # regress_pre = linregress(x[:50],df[stat_calc][:50])
        # regress_post = linregress(x[49:],df[stat_calc][49:])
        # print(regress_pre)
        
        lin_m,lin_b,r_value,p_value,stderr = linregress(x[:50],df[stat_calc][:50])
        df['y_reg_pre'] = np.where((df['DATE'] <= 1999),lin_m*x+lin_b,np.nan)
        
        
        lin_m,lin_b,r_value,p_value,stderr = linregress(x[49:],df[stat_calc][49:])     
        df['y_reg_post'] = np.where((df['DATE'] >= 1999),lin_m*x+lin_b,np.nan)
     
        print(df)
        return df#,pval


def month_to_season_LUT(df,station):
    df=df.set_index('DATE')
#     month_to_season_lu = np.array([
#     None,
#     'DJF', 'DJF',
#     'MAM', 'MAM', 'MAM',
#     'JJA', 'JJA', 'JJA',
#     'SON', 'SON', 'SON',
#     'DJF'
# ])
    
    month_to_season_lu = np.array([
    None,
    'JFM', 'JFM',
    'JFM', 'AMJ', 'AMJ',
    'AMJ', 'JAS', 'JAS',
    'JAS', 'OND', 'OND',
    'OND'
])
    grp_ary = month_to_season_lu[df.index.month]
    
    season = df.groupby([df.index.year,grp_ary])['PRCP'].sum()
    unstack = season.unstack()
    print(unstack)
    calc = "Seasonal Precipitation Totals"
    plotting(unstack,calc,station)


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