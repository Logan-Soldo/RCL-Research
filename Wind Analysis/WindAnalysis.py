import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import math


def read_csv_EWR():
  #  data = pd.read_csv('Newark_wind.csv',skiprows=1,parse_dates=[['Date', 'HrMn']],infer_datetime_format=True)
    data = pd.read_csv('Newark_wind.csv',skiprows=1,low_memory=False)
    data = data[data["Type"] == "FM-15"]
    data['Date'] = pd.to_datetime(data['Date'],format="%Y%m%d")
    data['HrMn']= data['HrMn'].astype(str)
    data['HrMn']=data['HrMn'].str.pad(width=4,side='left',fillchar='0')
    
    data['HrMn'] = pd.to_datetime(data['HrMn'],format='%H%M',exact=False)
    data['HrMn'] = data['HrMn'].dt.time
    data['Date'] = data['Date'].dt.date
    data['Date'] = pd.to_datetime(data['Date'].apply(str)+' '+data['HrMn'].apply(str))
    data = data.drop(['HrMn','Temp','Slp','Q','Q.1','Q.2','Q.3','Q.4','I.1','I'],axis=1)
    data = data.rename(columns = {"Spd.1":"Gust Speed"})
    data = data.set_index('Date')
    ASOS = data.loc['1997-01-01':'2019-12-31'].copy()

    ASOS.replace(999.9,np.nan,inplace=True)
    
    ASOS['V_east'] = ASOS['Spd'] * np.sin(ASOS['Dir']*np.pi/180)
    ASOS['V_north'] = ASOS['Spd'] * np.cos(ASOS['Dir']*np.pi/180)    
    ASOS['Mean_WD']  = np.arctan2(ASOS['V_east'],ASOS['V_north'])*180/np.pi
    ASOS['Mean_WD'] = (360 + ASOS['Mean_WD'])%360
    

    ASOS['Spd'] = ASOS['Spd'] * 2.2369362921                # Converting from m/s to mph
    ASOS['Gust Speed'] = ASOS['Gust Speed'] * 2.2369362921  # Converting from m/s to mph

    ASOS = ASOS.drop(['V_east','V_north'],axis=1)
    return ASOS
   
def read_csv_ACY():
    data = pd.read_csv('ACY_wind.csv',skiprows=0,low_memory=False)
    data = data[data["Type"] == "FM-15"]
    HrMn= data['Date'].str.split("T",expand=True)
    data["Date"] = HrMn[0]
    data["HrMn"] = HrMn[1]    
    data['Date'] = pd.to_datetime(data['Date'],format="%Y-%m-%d")
    data['HrMn'] = pd.to_datetime(data['HrMn'],format='%H:%M',exact=False)
    data['HrMn'] = data['HrMn'].dt.time
    data['Date'] = data['Date'].dt.date
    data['Date'] = pd.to_datetime(data['Date'].apply(str)+' '+data['HrMn'].apply(str))    
    data = data.drop(['HrMn','Name','Source'],axis=1)
    data = data.rename(columns = {"Spd.1":"Gust Speed"})

    data = data.set_index('Date')
    ASOS = data.loc['1997-01-01':'2019-12-31'].copy()

# Cleaning Dataset to be used universally
    ASOS.replace(999.9,np.nan,inplace=True)
    ASOS.replace("VRB",np.nan,inplace=True)
    ASOS['Spd']= ASOS['Spd'].str.split("s",expand=True)
    ASOS['Gust Speed']= ASOS['Gust Speed'].str.split("s",expand=True)
    
    ASOS['Spd'] = ASOS['Spd'].astype(float)
    ASOS['Dir'] = ASOS['Dir'].astype(float)
    ASOS['Gust Speed'] = ASOS['Gust Speed'].astype(float)
    print(ASOS.dtypes)
    
    ASOS['V_east'] = ASOS['Spd'] * np.sin(ASOS['Dir']*np.pi/180)
    ASOS['V_north'] = ASOS['Spd'] * np.cos(ASOS['Dir']*np.pi/180)    
    ASOS['Mean_WD']  = np.arctan2(ASOS['V_east'],ASOS['V_north'])*180/np.pi
    ASOS['Mean_WD'] = (360 + ASOS['Mean_WD'])%360
    

    ASOS['Spd'] = ASOS['Spd'] * 2.2369362921                # Converting from m/s to mph
    ASOS['Gust Speed'] = ASOS['Gust Speed'] * 2.2369362921  # Converting from m/s to mph

    ASOS = ASOS.drop(['V_east','V_north'],axis=1)
    return ASOS   


    
def extract_data(ASOS):    
    
    ASOS_yearMean = ASOS.groupby(ASOS.index.year).mean()   

    
    ASOS_yearMean.columns = ['DirMean','SpdMean','GustMean','DirUV_Mean']    
    print(ASOS_yearMean)
        
    ASOS_yearMedian = ASOS.groupby(ASOS.index.year).median()
    ASOS_yearMedian.columns = ['DirMedian','SpdMedian','GustMedian','DirUV_Median']
    print(ASOS_yearMedian)
    
    ASOS_year = pd.merge(ASOS_yearMean,ASOS_yearMedian,left_index=True,right_index=True)

    ASOS_monthMean = ASOS.groupby(ASOS.index.month).mean()
    ASOS_monthMean.columns = ['DirMean','SpdMean','GustMean','DirUV_Mean']
    ASOS_monthMedian = ASOS.groupby(ASOS.index.month).median()
    ASOS_monthMedian.columns = ['DirMedian','SpdMedian','GustMedian','DirUV_Median']
    
    ASOS_month = pd.merge(ASOS_monthMean,ASOS_monthMedian,left_index=True,right_index=True)
    
    ASOS_season = month_to_seaon_LUT(ASOS)
    
    figname1="Annual Mean and Median"
    figname3="Monthly Mean and Median"
    figname4="SeasonMean"

    print(ASOS_year)
    return ASOS_year,ASOS_month,figname1,figname3,figname4

def spd_calc(df):
    
    df['spd_miss'] = np.where((df['Spd'].isnull()),1,0)
    df['spd>=5'] = np.where(df['Spd'] >= 5.0,1,0)     # flags as 1 if the row value meets the condition.
    df['spd>=10'] = np.where(df['Spd'] >= 10.0,1,0)
    df['spd>=15'] = np.where(df['Spd'] >= 15.0,1,0)
    df['>=20'] = np.where(df['Spd'] >= 20.0,1,0)    
  #  print(df)
    df = df.drop(['Dir','Gust Speed','Spd'],axis = 1 )
    
    Wind_speed = df.groupby(df.index.year).sum()
 #   print(Wind_speed)
    return Wind_speed

def spd_between(df):
    df['Missing'] = np.where((df['Spd'].isnull()),1,0)
    df['0->5'] = np.where((df['Spd'] >= 0)&(df['Spd']<5),1,0)     # flags as 1 if the row value meets the condition.
    df['5->10'] = np.where((df['Spd'] >= 5)&(df['Spd']<10),1,0)     # flags as 1 if the row value meets the condition.
    df['10->15'] = np.where((df['Spd'] >= 10)&(df['Spd']<15),1,0)     # flags as 1 if the row value meets the condition.
    df['15->20'] = np.where((df['Spd'] >= 15)&(df['Spd']<20),1,0)     # flags as 1 if the row value meets the condition.
    
   # print(df)
    df = df.drop(['Dir','Gust Speed','Spd'],axis = 1 )

    Between_speed = df.groupby(df.index.year).sum()
  #  print(Between_speed)
    return Between_speed

    
    
def month_to_seaon_LUT(df):
    month_to_season_lu = np.array([
    None,
    'DJF', 'DJF',
    'MAM', 'MAM', 'MAM',
    'JJA', 'JJA', 'JJA',
    'SON', 'SON', 'SON',
    'DJF'
])
    grp_ary = month_to_season_lu[df.index.month]
    
    ASOS_season = df.groupby(grp_ary).mean()


    
def plot_dir(df,figname):
    '''
    Plotting function for direction.

    Parameters
    ----------
    df : Dataframe called in to be plotted based on parameters.

    Returns
    -------
    None.

    '''
    df.reset_index(level=0,inplace=True)

    plt.rc('font', family='serif')  
    plt.rc('xtick', labelsize='x-small')
    plt.rc('ytick', labelsize='x-small')
    
   # fig, ax = plt.subplots(dpi=2000)  
    ax = df.plot(x='Date',y=["DirMean","DirMedian"],kind="line")
    ax.set_ylim(0,360)
    ax.set_title('Wind Direction: Mean and Median')
    ax.grid()
#    plt.xticks(np.arrange(min(x)+1))
 #   plt.show()
    figname = figname + "_dir"
    savefig(figname)
    
def plot_spd(df):
    df.reset_index(level=0,inplace=True)
    print(df)

    plt.rc('font', family='serif')  
    plt.rc('xtick', labelsize='x-small')
    plt.rc('ytick', labelsize='x-small')    

   # fig, ax = plt.subplots(dpi=2000)  

    ax = df.plot(x='Date',y=["Missing","0->5","5->10","10->15","15->20",">=20"],kind="line")
    ax.set_title('Sum of Hours Between Wind Speed: EWR')
    ax.grid()
    ax.set_xlim(1997,2019)
    ax.set_xticks(range(1997,2019,1))
    ax.set_xticklabels(range(1997,2019,1),rotation=45)
    ax.set_ylim([0,4500])
    ax.set_yticks(range(0,4500,500))
    ax.set_ylabel("Sum of Hours")
    ax.legend(fontsize=8,labelspacing = 0.1)

    figname = "WindSpeed"
    savefig(figname)
   # ax.get_legend().remove()
  #  ax.set_ylim(0,max(df))

def plot_gust(df):
    Gust_max = df.groupby(df.index.year).mean()
    Gust_max = Gust_max.drop(['spd_miss','spd>=5','spd>=10','spd>=15','>=20','Missing','0->5','5->10','10->15','15->20'],axis=1)
    Gust_max.reset_index(level=0,inplace=True)
    
    ax = Gust_max.plot(x='Date',y=['Gust Speed'],kind='line')
    print(Gust_max)




def color_pick():
    c = color_select()
    for i in range(len(c)):
        r,g,b = c[i]
        c[i] = (r / 255., g / 255., b / 255.)

    return c

def color_select():
    '''
    This function is called to generate colors for graphing.
    Color maps can be found here: 
    https://tableaufriction.blogspot.com/2012/11/finally-you-can-use-tableau-data-colors.html
    '''
    
    tableau20blind = [(0, 107, 164), (255, 128, 14), (171, 171, 171), (89, 89, 89),
             (95, 158, 209), (200, 82, 0), (137, 137, 137), (163, 200, 236),
             (255, 188, 121), (207, 207, 207)]
    color_blind = [(215,25,28),(253,174,97),(145,191,219),(44,123,182)]
    return color_blind

def savefig(figname):    
    plt.savefig("E:\\School\\RutgersWork\\WindAnalysis\\figures\\%s.jpg" %(figname),dpi=2000)  # Need to vary this formatting between graphics.
    plt.show()       


def main():    
    pd.set_option("display.max_rows", 40)   
    pd.set_option("display.min_rows",20) 
    pd.set_option('display.max_columns', None)  
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('max_colwidth', None)    
    
    prompt = input("Select a station (ACY,EWR): ")
    if prompt.lower() == "ewr":
        ASOS = read_csv_EWR()
    elif prompt.lower() == "acy":
        ASOS = read_csv_ACY()
        
    ASOS_year,ASOS_month,figname1,figname3,figname4 = extract_data(ASOS)
    
    
    #spd_calc(ASOS)
    Wind_speed = spd_calc(ASOS)
    Between_speed = spd_between(ASOS)
    
    plot_dir(ASOS_year,figname1)
    #plot_dir(ASOS_year,figname2)
    
    plot_dir(ASOS_month,figname3)
    
    plot_spd(Between_speed)
    #plot_gust(ASOS)
if __name__ == "__main__": 
    main() 