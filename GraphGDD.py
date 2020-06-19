import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates


def read_file(stations,time,base,method):
    print(time)
    print(base)
    print(method)
    filelist = []
    try:   
        for station in stations:
            print(station)            
            open("E:\School\RutgersWork\DegreeDayAnalysis\%s\Outputs\%s\%s_%sGDD%s_B%s.txt" %(station,time,station,time,method,base))
            filelist.append("E:\School\RutgersWork\DegreeDayAnalysis\%s\Outputs\%s\%s_%sGDD%s_B%s.txt" %(station,time,station,time,method,base))
      #  print(filelist)
        return filelist
    except FileNotFoundError:
        print("file doesn't exist")
    
def daily_plt(filelist):
    y_list = []
    y=[]
    fname_lst = []
    plt.figure(figsize=(20,10))
    for fname in filelist:
        try:
    #        data=np.loadtxt(fname,skiprows=1)
            df = pd.read_fwf(fname,names = ['station','type','Datestring','Year','Month','Day','Julian','GDD'])
            df['Date'] = pd.to_datetime(df['Datestring'],format='%Y%m%d')
            print(df)
          #  plt.title(header)
            x = df['Date']
            y_temp = df['GDD']
            y_list.append(y_temp)
            plt.plot(x,y_temp)
            plt.legend()
      #      plt.plot(x,y,label=fname[35:39])
        except IOError:
            continue 

def daily_avg(filelist,time,base,stations,method):
    y_list = []
    y=[]
    fname_lst = []
    plot_df = pd.DataFrame(dtype=int)
    plt.figure(figsize=(20,10))
    for fname in filelist:
        try:
    #        data=np.loadtxt(fname,skiprows=1)
            df = pd.read_fwf(fname,names = ['station','type','Datestring','Year','Month','Day','Julian','GDD'])
            df['Date'] = pd.to_datetime(df['Datestring'],format='%Y%m%d')
            davg = df.drop(['station','type','Datestring','Year','Month','Day','Julian'],axis=1)
            davg = davg.set_index('Date')
            davg = davg.groupby(davg.index.dayofyear).mean()
            print(davg)
            davg.reset_index(level=0,inplace=True)
            #  plt.title(header)
            x = davg['Date']
            y = davg['GDD']
            
            plot_df=plot_df.append(y)

        except IOError:
            continue
  #  plot_df = pd.DataFrame(x,y_list)
    max_df = plot_df.max().max()    
    plot_df =plot_df.append(x)
    m_list = []
    for m in x:
        m = '00'+str(m)
        m = datetime.strptime(m,'%y%j')
    #    m = m.strftime('%b %d')
        m_list.append(m)
        
    plot_df=plot_df.transpose()
    plot_df['Date'] = m_list
        
    plot_df['Date'] = plot_df['Date'].dt.strftime('%b %d')
    plot_df = plot_df.set_index('Date')    
    
    plot_df.columns = stations
    plot_df.reset_index(level=0,inplace=True)
    
    ax = plot_df.plot(x='Date',kind="line",xlim=(0,366),xticks=range(0,366,25),yticks=range(0,5000,500),rot=45,fontsize=9,linewidth=1.0)
    ax.legend(loc= 'upper left')
    ax.grid()
    if method == "BE":
        ax.set_title("Average Daily Growing Degree Days at Base %s °C \n Baskerville-Emin" %(base))
    elif method == "MOD":
        ax.set_title("Average Daily Growing Degree Days at Base %s °C \n Modified Growing Degree Days" %(base))        
    savefig(time,base,method)
    print(plot_df)
    
def seasonal_avg(filelist,time,base,stations,method):
    y_list = []
    y=[]
    fname_lst = []
   # plt.figure(figsize=(20,10))
    seasons = [[1,91],[92,182],[183,274],[274,366]]
    count = 0
    fig,axes =  plt.subplots(2, 2, figsize=(20,20),constrained_layout=False)
    for i in seasons:
            season_plt(filelist,time,base,stations,method,i,count,axes)
            count += 1
    plt.show()

def season_plt(filelist,time,base,stations,method,i,count,axes):
      sub = [(0,0),(0,1),(1,0),(1,1)]

      plot_df = pd.DataFrame(dtype=int)  
    #  print(i)
      for fname in filelist:
          try:
      #        data=np.loadtxt(fname,skiprows=1)
              df = pd.read_fwf(fname,names = ['station','type','Datestring','Year','Month','Day','Julian','GDD'])
              df['Date'] = pd.to_datetime(df['Datestring'],format='%Y%m%d')
              davg = df.drop(['station','type','Datestring','Year','Month','Day','Julian'],axis=1)
              davg = davg.set_index('Date')
        #      davg = month_to_season_LUT(davg)
              davg = davg.groupby(davg.index.dayofyear).mean()
              davg.reset_index(level=0,inplace=True)
              davg = davg[davg['Date'].between(i[0],i[1])]            
              print(davg)
              davg.reset_index(level=0,inplace=True)
              #  plt.title(header)
              x = davg['Date']
              y = davg['GDD']
              
              plot_df=plot_df.append(y)
      
          except IOError:
              continue
    #  plot_df = pd.DataFrame(x,y_list)
      max_df = int(plot_df.max().max())
      min_df = int(plot_df.min().min())
      interval = int((max_df-min_df)/6)    
      plot_df =plot_df.append(x)
      m_list = []
      for m in x:
          m = '00'+str(m)
          m = datetime.strptime(m,'%y%j')
      #    m = m.strftime('%b %d')
          m_list.append(m)
          
      plot_df=plot_df.transpose()
      plot_df['Date'] = m_list
          
      plot_df['Date'] = plot_df['Date'].dt.strftime('%b %d')
      plot_df = plot_df.set_index('Date')    
      
      plot_df.columns = stations
      plot_df.reset_index(level=0,inplace=True)
      
      print(sub[count])
      df_plot = plot_df.plot(x='Date',kind="line",xlim=(0,91),xticks=range(0,91,10),yticks=range(min_df,max_df,interval),rot=45,fontsize=10,linewidth=1.0,ax=axes[sub[count]],grid=True)
    #  df_plot.legend(loc= 'upper left')
        # axes.grid()
        # if method == "BE":
        #     ax.set_title("Average Daily Growing Degree Days at Base %s °C \n Baskerville-Emin" %(base))
        # elif method == "MOD":
        #     ax.set_title("Average Daily Growing Degree Days at Base %s °C \n Modified Growing Degree Days" %(base))        
     #   savefig(time,base,method)
      print(plot_df)   
    
def month_to_season_LUT(df):
    month_to_season_lu = np.array([
    None,
    'DJF', 'DJF',
    'MAM', 'MAM', 'MAM',
    'JJA', 'JJA', 'JJA',
    'SON', 'SON', 'SON',
    'DJF'
])
    grp_ary = month_to_season_lu[df.index.month]
    
    season_df = df.groupby(grp_ary).mean()
    return season_df
    
def savefig(time,base,method):    
    plt.savefig("E:\\School\\RutgersWork\\DegreeDayAnalysis\\Plots\\%s\\%s%s%s.jpg" %(time,time,base,method),dpi=2000)  # Need to vary this formatting between graphics.
    plt.show()     
    
def main():
    station_list = ['CreamRidge','Howell','SeaGirt','Wall']
 #   base = float(input("Select a Base Temperature [2,4,5,7,10]:   "))
    time = input("Daily, Annual, or Seasonal Outputs?: ")
    for base in [2,4,5,7,10]:
        base = float(base)
        if time == "Daily":
            filelist = read_file(station_list,time,base,'BE')
            daily_avg(filelist,time,base,station_list,'BE')
            
            filelist2 = read_file(station_list,time,base,'MOD')
            daily_avg(filelist2,time,base,station_list,'MOD')
            
        elif time == "Annual":
            time = "Ann"
            read_file(station_list,time,base,'BE')
        elif time == "Seasonal":
            time = "Daily"
            filelist = read_file(station_list,time,base,'BE')
            seasonal_avg(filelist,time,base,station_list,'BE')
            
            filelist2 = read_file(station_list,time,base,'MOD')
            seasonal_avg(filelist2,time,base,station_list,'MOD')
            time = "Seasonal"            

if __name__ == "__main__":
    main()        
