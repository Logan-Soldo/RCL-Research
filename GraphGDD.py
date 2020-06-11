import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime



def read_file(stations,time,base):
    print(time)
    print(base)
    filelist = []
    try:   
        for station in stations:
            print(station)            
            open("E:\School\RutgersWork\DegreeDayAnalysis\%s\Outputs\%s\%s_%sGDD_B%s.txt" %(station,time,station,time,base))
            filelist.append("E:\School\RutgersWork\DegreeDayAnalysis\%s\Outputs\%s\%s_%sGDD_B%s.txt" %(station,time,station,time,base))
       # print(file,filelist)
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

def daily_avg(filelist,time,base,stations):
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
            # y_list.append(y)
            # y_list = np.array(y_list).tolist()
            # ax = plt.plot(x,y)
            # ax.grid()
            # ax.set_title("Average Daily Growing Degree Days at Base %s °C" %(base))
            # ax.legend(labels=stations)
      #      plt.plot(x,y,label=fname[35:39])
        except IOError:
            continue
  #  plot_df = pd.DataFrame(x,y_list)
    # plot_df =plot_df.append(x)
    m_list = []
    for m in x:
        m = '00'+str(m)
        m = datetime.strptime(m,'%y%j')
        m = m.strftime('%b %d')
        m_list.append(m)
        
    plot_df=plot_df.transpose()
    plot_df['Date'] = m_list
  #  plot_df = plot_df.astype({"Date":int})
    plot_df = plot_df.set_index('Date')    
    
    plot_df.columns = stations
    plot_df.reset_index(level=0,inplace=True)
    

    
    
    ax = plot_df.plot(x='Date',kind="line")
    ax.grid()
    ax.set_xlim(1,366)
  #  ax.set_xticks(range(1,366,20))
    ax.set_title("Average Daily Growing Degree Days at Base %s °C" %(base))    
    print(plot_df)
    
def main():
    station_list = ['CreamRidge','Howell','SeaGirt','Wall']
    base = float(input("Select a Base Temperature [2,4,5,7,10]:   "))
    time = input("Daily or Annual Outputs?: ")
    if time == "Daily":
        filelist = read_file(station_list,time,base)
       # daily_plt(filelist)
        daily_avg(filelist,time,base,station_list)
    elif time == "Annual":
        time = "Ann"
        read_file(station_list,time,base)

if __name__ == "__main__":
    main()        
