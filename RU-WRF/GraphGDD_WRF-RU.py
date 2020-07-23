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
    plt.figure(figsize=(10,10),dpi=600)
    for fname in filelist:
        try:
    #        data=np.loadtxt(fname,skiprows=1)
            df = pd.read_fwf(fname,names = ['station','type','Datestring','Year','Month','Day','Julian','GDD'])
            df['Date'] = pd.to_datetime(df['Datestring'],format='%Y%m%d')
           # print(df.loc[[365]])
            davg = df.drop(['station','type','Datestring','Year','Month','Day'],axis=1)
            davg = davg.set_index('Julian')
            davg = davg.groupby('Julian').mean()
            print(davg)
            davg.reset_index(level=0,inplace=True)
            #  plt.title(header)
            x = davg['Julian']
            y = davg['GDD']
            
            plot_df=plot_df.append(y)

        except IOError:
            continue
  #  plot_df = pd.DataFrame(x,y_list)
    max_df = round(plot_df.max().max(),-3)+1000
    print(max_df)
    interval = int(max_df)/10    
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
    plot_df = plot_df.drop(['Julian'],axis=1)    

    plot_df.columns = stations
    plot_df.reset_index(level=0,inplace=True)
    
    ax = plot_df.plot(x='Date',kind="line",xlim=(0,366),xticks=range(0,366,25),yticks=range(0,int(max_df)+1,int(interval)),rot=45,fontsize=9,linewidth=1.0)
    ax.set_ylabel("Accumulated GDDs")
    ax.xaxis.label.set_visible(False)
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
    seasons = [[1,91],[92,182],[183,274],[275,366]]
    count = 0
    fig,axes =  plt.subplots(2, 2, figsize=(10,10),constrained_layout=True)
    for i in seasons:
            handles,labels,df_plot=season_plt(filelist,time,base,stations,method,i,count,axes)
            count += 1
    degree_sign= u'\N{DEGREE SIGN}'
    if method == "BE":
        fig.suptitle("Average Daily Growing Degree Days by Season \n at Base %s %sC: \n Baskerville-Emin"%(base,degree_sign),fontsize=18)
    elif method == "MOD":
        fig.suptitle("Average Daily Growing Degree Days by Season \n at Base %s %sC: \n Modified Growing Degree Days"%(base,degree_sign),fontsize=18)
          
    fig.legend(handles,labels,fontsize=10)
   # print(fig)        
  #  plt.show()
    time = "Season"
    savefig(time,base,method)
def season_plt(filelist,time,base,stations,method,i,count,axes):
  sub = [(0,0),(0,1),(1,0),(1,1)]
  yticks_min = [0,25,615,1760]
  plot_df = pd.DataFrame(dtype=int)  
#  print(i)
  for fname in filelist:
      try:
          #        data=np.loadtxt(fname,skiprows=1)
          df = pd.read_fwf(fname,names = ['station','type','Datestring','Year','Month','Day','Julian','GDD'])
          df['Date'] = pd.to_datetime(df['Datestring'],format='%Y%m%d')
          davg = df.drop(['station','type','Datestring','Year','Month','Day'],axis=1)
          davg = davg.set_index('Julian')
          davg = davg.groupby('Julian').mean()
          
          davg.reset_index(level=0,inplace=True)
          davg = davg[davg['Julian'].between(i[0],i[1])]            
          print(davg)
          davg.reset_index(level=0,inplace=True)
          #  plt.title(header)
          x = davg['Julian']
          y = davg['GDD']
          
          plot_df=plot_df.append(y)
      
      except IOError:
          continue
#  plot_df = pd.DataFrame(x,y_list)
  max_df = int(plot_df.max().max())
  min_df = int(plot_df.min().min())
  interval = int((max_df-yticks_min[count])/6)    
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
  plot_df = plot_df.drop(['Julian'],axis=1)    
  
  plot_df.columns = stations
  plot_df.reset_index(level=0,inplace=True)

  c = color_select()
  for i in range(len(c)):
      r,g,b = c[i]
      c[i] = (r / 255., g / 255., b / 255.)
  color = [c[count]]


  
  #print(sub[count])
  df_plot = plot_df.plot(x='Date',kind="line",xlim=(0,91),xticks=range(0,91,10),
                         yticks=range(yticks_min[count],max_df,interval),rot=45,
                         fontsize=14,linewidth=2.0,ax=axes[sub[count]],
                         grid=True,legend=False,color=c)
  
  df_plot.yaxis.set_label_text("Growing Degree Days",fontsize=16)
  df_plot.xaxis.label.set_visible(False)

  if count == 0:
      axes[sub[count]].set_title("Jan-Feb-Mar",fontsize=16)
  elif count == 1:
      axes[sub[count]].set_title("Apr-May-Jun",fontsize=16)
  elif count == 2:
      axes[sub[count]].set_title("Jul-Aug-Sep",fontsize=16)    
  elif count == 3:
      axes[sub[count]].set_title("Oct-Nov-Dec",fontsize=16)
      
  handles, labels = df_plot.get_legend_handles_labels()
  return handles,labels,df_plot
#  df_plot.legend(loc= 'upper left')
# axes.grid()

  savefig(time,base,method)
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
    return color_blind
    
def savefig(time,base,method):    
    print("Saving Plot...")
#    plt.savefig("E:\\School\\RutgersWork\\DegreeDayAnalysis\\Plots\\%s\\%s%s%s.svg" %(time,time,base,method),format='svg')  # Need to vary this formatting between graphics.
    plt.savefig("E:\\School\\RutgersWork\\DegreeDayAnalysis\\Plots\\%s\\%s%s%s.jpg" %(time,time,base,method),format='jpg',dpi=600)    
    plt.savefig("E:\\School\\RutgersWork\\DegreeDayAnalysis\\Plots\\%s\\%s%s%s.tif" %(time,time,base,method),format='tif',dpi=600)    
    plt.show()
    print("Plot Saved!")     
    
def main():
    pd.set_option("display.max_rows", 40)   
    pd.set_option("display.min_rows",20) 
    pd.set_option('display.max_columns', None)  
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('max_colwidth', None) 
    station_list = ['CreamRidge','Howell','SeaGirt','Wall']
 #   base = float(input("Select a Base Temperature [2,4,5,7,10]:   "))
    time = input("Daily, Annual, or Seasonal Outputs?: ")
    for base in [5,10]:
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
