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
    print(station)
    while True:
        try:
            data = pd.read_csv('E:\School\RutgersWork\DEP_Precip\Stations\%s.csv'%(station),parse_dates=['DATE'],infer_datetime_format=True,na_values=" ").fillna(0)
        #    print(data)
            data['PRCP'] = pd.to_numeric(data.PRCP,errors='coerce')
            data = data.set_index(['DATE'])
            data = data.loc['1950-01-01':'2019-12-31']        # 70 year period of record...
  #          data = data.loc['1900-01-01':'2019-12-31']        # Extended long term period of record...
            data.reset_index(level=0,inplace=True)
            print(data[['DATE','PRCP']])
            return data[['DATE','PRCP']]
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
    print(total_precip)
    calc = 'Total Precipitation'

    plotting(total_precip,calc,station)                 # Plotting Total Precip
    
    df.reset_index(level=0,inplace=True)   
    
    # bins = binning(df,station)              # Dividing data into bins and then plotting. Calculations are the number of days above x.
   
    # month_to_season_LUT(df,station,calc)    # For seasonal calculations
    
    # dry_intervals(df,station)
    
 #   cumulative_precip(df,station)           # Number of days to reach x threshold. (Currently slow to run)
 
    
    
    
  # # # # # # # # # # Precip_events(df,station)
    
  # # # # # # # # # # rolling_mean(df,station)
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
    '''
    Calculating the number of days above a threshold.
    Also has precentage of days above a threshold in a year. 
        This is not needed but is included.

    '''
    bins = pd.DataFrame(df['DATE'])
    bins['>0.0'] = np.where((df['PRCP'] > 0.0),1,0)
    bins['≥ 0.10'] = np.where((df['PRCP'] >= 0.10),1,0)
    bins['≥ 0.25'] = np.where((df['PRCP'] >= 0.25),1,0)
    bins['≥ 0.50'] = np.where((df['PRCP'] >= 0.50),1,0)
    bins['≥ 1.00'] = np.where((df['PRCP'] >= 1.00),1,0)
    bins['≥ 2.00'] = np.where((df['PRCP'] >= 2.00),1,0)
   
    calc = 'Days With Precipitiation'
    month_to_season_LUT(bins,station,calc)
    
    
    bins = bins.set_index('DATE')     
    group = bins.groupby(bins.index.year).cumsum()  # accumulating days above a base value throughout the year
    calc = 'Bin Progression'
    plotting(group,calc,station)
    
    yearly_bin = bins.groupby(bins.index.year).sum() # sum of days above base by year
    calc = 'Days Above Base (in)'
    plotting(yearly_bin,calc,station)



   #  percent = pd.DataFrame()   # Calculating percentage of precip days above base.
   #  calc = "Precentage of Precipitation Days At/Above Base (in)"
   #  yearly_bin = bins.groupby(bins.index.year).sum()
   #  percent['≥ 0.10'] = (yearly_bin['≥ 0.10']/yearly_bin['>0.0'])*100
   #  percent['≥ 0.25'] = (yearly_bin['≥ 0.25']/yearly_bin['>0.0'])*100
   #  percent['≥ 0.50'] = (yearly_bin['≥ 0.50']/yearly_bin['>0.0'])*100
   #  percent['≥ 1.00'] = (yearly_bin['≥ 1.00']/yearly_bin['>0.0'])*100
   #  percent['≥ 2.00'] = (yearly_bin['≥ 2.00']/yearly_bin['>0.0'])*100
   # # print(percent)
   #  plotting(percent,calc,station)

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
    dry_df = pd.DataFrame(df['DATE'])
    dry_df = dry_df.set_index('DATE')
    #print(dry_df)
    dry_list = []
    calc = "Dry Intervals"
 #   _,ax = plt.subplots()
    base_list = [0.5,0.25,0.1,0.0]
    base_string =['0.50in','0.25in','0.10in','0.00in']
    for base in base_list:
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
    
        dry_spell = pd.concat([key2,key1],axis=1).reset_index()
        dry_spell = dry_spell.drop(columns='key1')
        dry_spell = dry_spell.set_index('DATE')
        dry_list.append(dry_spell)
    dry_df = pd.concat(dry_list,axis=1)
    dry_df.columns = base_string
        
    print(dry_df)
    plotting(dry_df,calc,station)
    #dry_spell.plot(x='DATE',y='dry_count',ax=ax,kind='hist',alpha=0.7)


def cumulative_precip(df,station):
    '''
    This function counts how many days it takes to get to precip of x magnitude.

    '''
    calc = "Days to Accumulate x in"
    depth_list = [0.5,1.0,2.0,4.0,10.0,20.0]        # various threshold depths to reach.
    columns = ["0.5in","1.0in","2.0in","4.0in","10.0in","20.0in"]        # various threshold depths to reach.

    df_j = pd.DataFrame(df['DATE'])         # creating an empty dataframe with DATE as the index
    for d in depth_list:
        j_list = []                         # starting an empty list for each threshold depth
        count1 = 0                          # adding in a 365 day counter assuming it does not take more than a year to accumulate.
        count2 = 366
        for i in df['DATE']:                # looping through i values after looping through Precipitation values from count1 to count2
            j_sum = 0                       # reset sums
            j_count = 0
            for j in df['PRCP'][count1:count2]:  
                j_count = j_count + 1
                j_sum = j_sum + j
                if j_sum >= d:              # Checking if value is greater than threshold.
                    j_list.append(j_count)
                    break                   # break out of loop when value is reached.
            count1 += 1
            count2 += 1
        
        df_j[d] = pd.DataFrame(j_list)          # Putting list into a dataframe with dates as the index knowing they are the same length
#    df_j.to_csv("E:\\School\\RutgersWork\\DEP_Precip\\temp.csv")
    df_join = df_j.set_index('DATE')    
    df_daymean = df_join.groupby(df_join.index.dayofyear).mean()        # Grouping by day of the year and taking the mean.
    df_upper_dev = df_daymean + df_join.groupby(df_join.index.dayofyear).std()
    df_lower_dev = df_daymean - df_join.groupby(df_join.index.dayofyear).std()

    df_daymean.columns = columns
    df_upper_dev.columns = ["Up 0.5in","Up 1.0in","Up 2.0in","Up 4.0in","Up 10.0in","Up 20.0in"]
    df_lower_dev.columns = ["Low 0.5in","Low 1.0in","Low 2.0in","Low 4.0in","Low 10.0in","Low 20.0in"]
    
    
    df_CumPrecip = pd.DataFrame([df_daymean['0.5in'],df_upper_dev['Up 0.5in'],df_lower_dev['Low 0.5in'],
                                                    df_daymean['1.0in'],df_upper_dev['Up 1.0in'],df_lower_dev['Low 1.0in'],
                                                    df_daymean['2.0in'],df_upper_dev['Up 2.0in'],df_lower_dev['Low 2.0in'],
                                                    df_daymean['4.0in'],df_upper_dev['Up 4.0in'],df_lower_dev['Low 4.0in'],
                                                    df_daymean['10.0in'],df_upper_dev['Up 10.0in'],df_lower_dev['Low 10.0in'],
                                                    df_daymean['20.0in'],df_upper_dev['Up 20.0in'],df_lower_dev['Low 20.0in']]).transpose()

    df_CumPrecip.to_csv("E:\\School\\RutgersWork\\DEP_Precip\\temp.csv")    
    
    plotting(df_CumPrecip,calc,station)
    
def plotting(df,calc,station):
    '''
    All functions that require plots come here for plotting. 
    They must bring in a DataFrame, the calculation string and station name.
    
    Formatting of the table is conducted in the "plot format" section.
    '''
    
    c = color_select()
    for i in range(len(c)):
        r,g,b = c[i]
        c[i] = (r / 255., g / 255., b / 255.)
        
    df.reset_index(level=0,inplace=True)
    start_year = df.DATE.min()
    end_year = df.DATE.max()
    year_range = (start_year,end_year)
    
    if calc == 'Total Precipitation':                   # Plotting the total Precipitation per year.
        width = 0.70
        stat_calc = 'PRCP'
#        lin_r = stats.pearsonr(x,df['PRCP'])
        reg = statistics(df,stat_calc,station,calc,year_range)
        _,ax = plt.subplots()
        df['PRCP'].plot(ax=ax,width=width,kind='bar',color=c[4])
        print(df)
         #   print(slope_df)
        reg = reg.reset_index(drop=True)
        reg.plot(ax=ax,color="black",linewidth="0.40",linestyle="dashed")

        plot_format(ax,station,calc,year_range)
        
        savefig(station,calc)



    if calc == 'Days Above Base (in)':    # sum of days above base by year
        _,ax = plt.subplots()
        width = 0.70
        
        df.plot('DATE',y='≥ 0.10',width=width,ax=ax,kind='bar',color=c[0])
        df.plot('DATE',y='≥ 0.25',width=width,ax=ax,kind='bar',color=c[1])
        df.plot('DATE',y='≥ 0.50',width=width,ax=ax,kind='bar',color=c[2])
        df.plot('DATE',y='≥ 1.00',width=width,ax=ax,kind='bar',color=c[3])
        df.plot('DATE',y='≥ 2.00',width=width,ax=ax,kind='bar',color=c[4])
        
        plot_format(ax,station,calc,year_range)
        savefig(station, calc)

        stat_calc = "≥ 0.10"
        reg = statistics(df,stat_calc,station,calc,year_range)

        fig,ax2 = plt.subplots()                          # Plotting only the number of days with precip above 0.0.
        calc = 'Days With Precipitation'
        
        reg = reg.reset_index(drop=True)
        reg.plot(ax=ax2,color="black",linewidth="0.40",linestyle="dashed")

        df['≥ 0.10'].plot(ax=ax2,kind='bar',width=width,color='blue')
        
        plot_format(ax2,station,calc,year_range)
        savefig(station, calc)    
    
    if calc == "Precentage of Precipitation Days At/Above Base (in)":           # Plotting based on binned days calculated as a percentage.
        _,ax = plt.subplots()
        width = 0.70
        
        df.plot('DATE',y='≥ 0.10',width=width,ax=ax,kind='bar',color=c[0])
        df.plot('DATE',y='≥ 0.25',width=width,ax=ax,kind='bar',color=c[1])
        df.plot('DATE',y='≥ 0.50',width=width,ax=ax,kind='bar',color=c[2])
        df.plot('DATE',y='≥ 1.00',width=width,ax=ax,kind='bar',color=c[3])
        df.plot('DATE',y='≥ 2.00',width=width,ax=ax,kind='bar',color=c[4])

        plot_format(ax,station,calc,year_range)
        savefig(station, calc)        

    if calc == "Consecutive Days With Precipitation":
        _,ax = plt.subplots()
        width = 0.70
        df.plot('DATE',y='Count',width=width,ax=ax,kind='bar',color=c[4])
        plot_format(ax,station,calc,year_range)        
        savefig(station, calc)

    if calc == "Seasonal Precipitation Totals" or calc == "Seasonal Days With Precipitation":
        supcalc = calc
        temp_calc = ['DJF','MAM','JJA','SON']
        reg_list = []
        for i in temp_calc:
            reg = statistics(df,i,station,calc,year_range)
            reg = reg.reset_index(drop=True)
            reg_list.append(reg)

        fig,axes = plt.subplots(2, 2,constrained_layout=True)
        fig.suptitle('%s: %s ≥ 0.1in'%(station,calc))
        width = 0.70
        df.plot('DATE',y='DJF',width=width,ax=axes[0,0],kind='bar',color='black',label = 'Dec-Jan-Feb',alpha=0.50)
        df.plot('DATE',y='MAM',width=width,ax=axes[0,1],kind='bar',color='black',label = 'Mar-Apr-May',alpha=0.50)
        df.plot('DATE',y='JJA',width=width,ax=axes[1,0],kind='bar',color='black',label = 'Jun-Jul-Aug',alpha=0.50)
        df.plot('DATE',y='SON',width=width,ax=axes[1,1],kind='bar',color='black',label = 'Sep-Oct-Nov',alpha=0.50)

        
        for i,ax in enumerate(fig.axes):
            if calc == 'Seasonal Days With Precipitation':
                ax.set_ylabel('Days')
            else:
                ax.set_ylabel('Precipitation (in)')
                
            subtitle = ['Dec-Jan-Feb','Mar-Apr-May','Jun-Jul-Aug','Sep-Oct-Nov']
            temp_calc = ['DJF','MAM','JJA','SON']


            reg = reg_list[i].plot(ax=ax,color="black",linewidth="0.25",linestyle="dotted")
    
#            plot_format(ax,station,calc)

            plot_format(ax,station,temp_calc[i],year_range)
            ax.set_title(subtitle[i])

        savefig(station,supcalc)
        
        

    if calc == 'Days to Accumulate x in':
        ### TODO 
        ####### plot one standard deviation above and below each.
        
        print(df)
        fig,axes = plt.subplots(3, 2,constrained_layout=True,sharex=True)
        fig.suptitle('%s: %s'%(station,calc),fontsize=10)
        
        axes[0,0].plot(df['DATE'],df['0.5in'],color='blue')
      #  axes[0,0].fill_between(df['DATE'],df['Up 0.5in'],df['Low 0.5in'],alpha=0.35,color='black')

        axes[0,1].plot(df['DATE'],df['1.0in'],color='blue')
      #  axes[0,1].fill_between(df['DATE'],df['Up 1.0in'],df['Low 1.0in'],alpha=0.35,color='black')
        
        axes[1,0].plot(df['DATE'],df['2.0in'],color='blue')
      #  axes[1,0].fill_between(df['DATE'],df['Up 2.0in'],df['Low 2.0in'],alpha=0.35,color='black')
        
        axes[1,1].plot(df['DATE'],df['4.0in'],color='blue')
      #  axes[1,1].fill_between(df['DATE'],df['Up 4.0in'],df['Low 4.0in'],alpha=0.35,color='black')
        
        axes[2,0].plot(df['DATE'],df['10.0in'],color='blue')
      #  axes[2,0].fill_between(df['DATE'],df['Up 10.0in'],df['Low 10.0in'],alpha=0.35,color='black')
        
        axes[2,1].plot(df['DATE'],df['20.0in'],color='blue')
      #  axes[2,1].fill_between(df['DATE'],df['Up 20.0in'],df['Low 20.0in'],alpha=0.35,color='black')
        # fig,axes = plt.subplots(3, 2,constrained_layout=True)#,sharex=True)
        # fig.suptitle('%s: %s'%(station,calc),fontsize=10)
        
        # df.plot(x='DATE',y='0.5in',kind= 'line',ax=axes[0,0],color='blue')
        # df.fill_between('DATE','Up 0.5in','low 0.5in',ax=axes[0,0],alpha=0.35,linewidth=0,color='black')

        # df.plot(x='DATE',y='1.0in',kind= 'line',ax=axes[0,1],color='blue')        
        
        # df.plot(x='DATE',y='2.0in',kind= 'line',ax=axes[1,0],color='blue')
        
        # df.plot(x='DATE',y='4.0in',kind= 'line',ax=axes[1,1],color='blue')
        
        # df.plot(x='DATE',y='10.0in',kind= 'line',ax=axes[2,0],color='blue')
        
        # df.plot(x='DATE',y='20.0in',kind= 'line',ax=axes[2,1],color='blue')

        for i,ax in enumerate(fig.axes):
            calc = ['0.5in','1in','2in','4in','10in','20in']
            plot_format(ax,station,calc[i],year_range)
        savefig(station,calc)

    
    if calc == "Dry Intervals":             # Three separate plots
        fig,axes = plt.subplots(2,2,constrained_layout=True)
        depths =['0.50in','0.25in','0.00in']
        depths = ['0.00in','0.10in','0.25in','0.50in']
        cords = [(0,0),(0,1),(1,0),(1,1)]
        count =0
        fig.suptitle("%s: %s Distribution"%(station,calc))
        print(df)
        data = df.loc['1980-01-01':'2019-12-31']
        
        for i in df[depths]:
            bins=np.arange(int(np.nanmin(df[i])), int(np.nanmax(df[i])) + 1, 1)
            # print(i)
            # print(df[depths])

        # df.plot(x='DATE',y='0.50in',ax=ax,kind='hist',alpha=0.7,color = 'dimgray')
        # df.plot(x='DATE',y='0.25in',ax=ax,kind='hist',alpha=0.7,color = 'darkgray')
            df.plot(x='DATE',y=i,ax=axes[cords[count]],kind='hist',alpha=0.7,color = 'gray',bins= bins)
         #   data.plot(x='DATE',y=i,ax=axes[cords[count]],kind='hist',alpha=0.7,color = 'green',bins= bins)
            count +=1
        for i,ax in enumerate(fig.axes):
            ylim = ax.get_ylim()
            ymax = round_up(ylim[1],-2)
            ax.set_xlim(0,40)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(ymax/5))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(ymax/10))
            ax.set_ylabel("Number of Occurrences")

            ax.set_ylim(0,ymax)

        savefig(station,calc)

def plot_format(ax,station,calc,year_range):
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    print(year_range)
    # year_range = (1900,2020)
    # xlim = ax.get_xlim()
    # xmin = round_up(xlim[0],0)
    # xmax = round_up(xlim[1],0)
    # print(xmin,xmax)
    fmtr = ticker.IndexFormatter(range(year_range[0],year_range[1]))
    ax.xaxis.set_major_formatter(fmtr)   
    ylim = ax.get_ylim()
    ymax = round_up(ylim[1],-1)
    ymin = round_up(ylim[0],-1)-10
    ax.set_ylim(0,ymax)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=8)
    ax.set_title('%s: %s'%(station,calc))
    ax.tick_params(axis='both', which='major', labelsize=8) 


    if calc == 'Days Above Base (in)':    # sum of days above base by year
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
        ax.set_ylabel("Days")
    
    elif calc == 'Days With Precipitation':
        print(ylim)
        ymin = round_up(ylim[0],0)        
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))        
        ax.legend().set_visible(False)
        ax.set_ylabel("Days")
        print(ymin)
        if ymin < 0:
            ax.set_ylim([0,ymax])
        else:
            ax.set_ylim([ymin+10,ymax])
        ax.set_title('%s:%s ≥ 0.1in'%(station,calc))

    elif calc == 'Total Precipitation':        
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax.tick_params(axis='x',labelrotation=90)      
        ax.legend().set_visible(False)
        ax.set_ylabel("Precipitation (in)")
        ax.set_ylim([15,ymax])
      
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
    elif (calc == "DJF") or (calc == "MAM") or (calc == "JJA") or (calc == "SON"):
        if ymax <= 30:            
            ax.set_ylim([0,30])
            ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        else:
            ax.set_ylim([0,40])
            ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
        
        ax.set_xticklabels(labels=range(1945,2020,5),rotation=90)
        ax.legend().set_visible(False)
        ax.set_title('%s'%calc)
   
        
        
    elif (calc == '0.5in') or (calc =='1in') or (calc == '2in') or (calc =='4in') or (calc =='10in') or (calc =='20in'):#,'40in']
        dates = []        
        for m in range(1,367):
            m = '04'+str(int(m))
            m = datetime.strptime(m,'%y%j')
            m = m.strftime('%b %d')
            dates.append(m)            
        
        
        tick_calc = round_up((ymax-ymin)/5,0)
        minor_TC= tick_calc/4
        if ymin < 0:
            ymin = 0
        ax.set_ylim(ymin,ymax)
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_calc))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_TC))  
        
        ax.set_title('%s'%calc,fontsize=8)
        ax.legend().set_visible(False)
        ax.set_ylabel('Days',fontsize=8)
        
        ax.set_xticklabels(dates[0::20])
        ax.set_xticks(range(1,365,20))
        ax.margins(x=0)
          
        plt.setp(ax.get_xticklabels(), rotation=90)
        ax.tick_params(axis='x', which='minor', bottom=False)
        ax.tick_params(axis='both',labelsize = 7 )
        
    ax.xaxis.label.set_visible(False)    

def statistics(df,stat_calc,station,calc,year_range):

        x=df['DATE'].values

        reg_list = []
        slope_list = []
        reg_df = pd.DataFrame(x)
        total_years = len(reg_df.index)
        reg_df=reg_df.set_index(x,inplace=True,drop=True)
        stat_list = []
        count= 0
        count2=31
        start_year = year_range[0]
        end_year = year_range[1]
        print(df[stat_calc])
        for i in range(1,total_years-29):
            lin_m,lin_b,r_value,p_value,stderr = linregress(x[count:count2],df[stat_calc][count:count2])
            kTau,p_value = stats.kendalltau(x[count:count2],df[stat_calc][count:count2])           # Different way of showing significance.
            
            regress = lin_m*x[count:count2] + lin_b
            slope = float('{:.2f}'.format(lin_m))
            pval = float('{:.2f}'.format(p_value))      # The two-sided p-value for a hypothesis test whose null hypothesis is an absence of association, tau = 0.
            kTau = float('{:.2f}'.format(kTau))         # Kendall's tau-b significance test
            stderr = '{:.2f}'.format(round(stderr,2))

            
            slope_df = pd.DataFrame(regress,x[count:count2])            
            stat_list.append(slope_df)
            year_str = str(start_year) + "-" + str(start_year+30)
            reg_list.append([year_str,slope,kTau,pval,stderr])
            slope_list.append([x[count:count2],regress])
            
            count += 1
            count2 += 1
            start_year += 1
            
        stats_df = pd.DataFrame(reg_list, columns = ["Year","Slope","kTau","P-value","Std Error"])
        stats_df.columns = ['Year','Slope',"Kendall's Tau-b",'P-value','Std Error']
        stats_df = stats_df.sort_values(by="Slope",ascending=False,ignore_index=True)           
        stats_df['Slope'] = stats_df['Slope'].map('{:.2f}'.format)
        

        stats_save = calc       
        reg_df = pd.concat(stat_list,axis=1)
        reg_df.columns = range(reg_df.shape[1])
        fig2, ax3 =plt.subplots(1)
        ax3.axis('tight')
        ax3.axis('off')        
        stat_table = ax3.table(cellText=stats_df.values,colLabels=stats_df.columns,loc='center')
        for f in stats_df["Year"]:  
            if int(f[0:4]) >= 1980:     # Highlighting most recent 10 years in yellow.
                row = stats_df[stats_df['Year']==f].index.item()
                stat_table[row+1,0].set_facecolor('#FFFF00')
                stat_table[row+1,1].set_facecolor('#FFFF00')
                stat_table[row+1,2].set_facecolor('#FFFF00')
                stat_table[row+1,3].set_facecolor('#FFFF00')
                stat_table[row+1,4].set_facecolor('#FFFF00')


        for g in stats_df['P-value']:                   # Highlighting level of p-value significance in shades of red.
            if g <= 0.01:
                sig = stats_df[stats_df['P-value'] == g].index.tolist()
                for r in range(len(sig)):
                    stat_table[sig[r]+1,3].set_facecolor('#8B0000')     
            elif (g <= 0.05) and (g > 0.01):
                sig = stats_df[stats_df['P-value'] == g].index.tolist()
                for r in range(len(sig)):
                    stat_table[sig[r]+1,3].set_facecolor('#FF0000')
                    
        savetable(station,stats_save,stat_calc)
        
        return reg_df
            



def month_to_season_LUT(df,station,calc):
    df['Year'] = pd.DatetimeIndex(df['DATE']).year
    df['Month'] = pd.DatetimeIndex(df['DATE']).month
    df['Year'] = np.where(df['Month'] == 12, df['Year'] +1,df['Year'])
    df=df.set_index('DATE')
    month_to_season_lu = np.array([
    None,
    'DJF', 'DJF',
    'MAM', 'MAM', 'MAM',
    'JJA', 'JJA', 'JJA',
    'SON', 'SON', 'SON',
    'DJF'
])
    

    grp_ary = month_to_season_lu[df.index.month]            # currently groups by same year so December xx00 is not in Seasonal xx01.
 #   print(grp_ary)
    if calc == 'Total Precipitation':
        season = df.groupby([df['Year'],grp_ary])['PRCP'].sum()
        calc = "Seasonal Precipitation Totals"
        
    elif calc == 'Days With Precipitiation':
        season = df.groupby([df['Year'],grp_ary])['≥ 0.10'].sum()
        calc = "Seasonal Days With Precipitation"


    unstack = season.unstack()
#    unstack = season.reset_index()
    unstack.index.names = ['DATE']
    unstack = unstack[1:-1]
    print(unstack)
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
    print("Saving Plot...",calc)  
    plt.draw()
#    plt.savefig("E:\\School\\RutgersWork\\DegreeDayAnalysis\\Plots\\%s\\%s%s%s.svg" %(time,time,base,method),format='svg')  # Need to vary this formatting between graphics.
    plt.savefig("E:\\School\\RutgersWork\\DEP_Precip\\Figures\\%s\\%s.jpg"%(station,calc),format='jpg',dpi=600,bbox_inches='tight')    
    plt.savefig("E:\\School\\RutgersWork\\DEP_Precip\\Figures\\%s\\%s.tif"%(station,calc),format='tif',dpi=600,bbox_inches='tight')    
    plt.show()
    print("Plot Saved!")

def savetable(station,calc,stat_calc):
    print("Saving Table...",calc)
    plt.draw()
    if calc == "Seasonal Days With Precipitation" or calc == "Seasonal Precipitation Totals":
        plt.savefig("E:\\School\\RutgersWork\\DEP_Precip\\Figures\\%s\\Tables\\Seasonal\\%s%s.jpg"%(station,stat_calc,calc),format='jpg',dpi=600,bbox_inches='tight')   
    else:
        plt.savefig("E:\\School\\RutgersWork\\DEP_Precip\\Figures\\%s\\Tables\\%s.jpg"%(station,calc),format='jpg',dpi=600,bbox_inches='tight')   
def main():
#    station_list = ['New Brunswick']
#    station_list = ['Coastal South','North West','Central','North East','Coastal North','South West']    
    station_list = ['South West']
    for station in station_list:
        print(station)
        data = read_file(station)
        data_analysis(data,station)

    
if __name__ == "__main__":
    main()  