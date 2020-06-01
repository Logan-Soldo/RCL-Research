import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


def read_csv():
  #  data = pd.read_csv('Newark_wind.csv',skiprows=1,parse_dates=[['Date', 'HrMn']],infer_datetime_format=True)
    data = pd.read_csv('Newark_wind.csv',skiprows=1,low_memory=False)
    data['Date'] = pd.to_datetime(data['Date'],format="%Y%m%d")
    data['HrMn']= data['HrMn'].astype(str)
   # data['HrMn']=data['HrMn'].str.pad(width=3,side='right',fillchar='0')
    data['HrMn']=data['HrMn'].str.pad(width=4,side='left',fillchar='0')
  #  data['HrMn']=data.HrMn[[0:2] + ':'+ [2:4]]
  #  data['HrMn'].datetime.strptime('%H%M')
    
    #data['Date'] = pd.to_datetime(data.Date) + data['HrMn'].datetime.strftime('%H%M')
    
    data['HrMn'] = pd.to_datetime(data['HrMn'],format='%H%M',exact=False)
    data['HrMn'] = data['HrMn'].dt.time
    data['Date'] = data['Date'].dt.date
    data['Date'] = pd.to_datetime(data['Date'].apply(str)+' '+data['HrMn'].apply(str))
    data = data.drop(['HrMn','Temp','Slp','Q','Q.1','Q.2','Q.3','Q.4','I.1','I'],axis=1)
    data = data.rename(columns = {"Spd.1":"Gust Speed"})

    data = data.set_index('Date')
    ASOS = data.loc['1997-01-01':'2019-12-31']


    ASOS.replace(999.9,np.nan,inplace=True)
    ASOS['Spd'] = ASOS['Spd'] * 2.2369362921                # Converting from m/s to mph
    ASOS['Gust Speed'] = ASOS['Gust Speed'] * 2.2369362921  # Converting from m/s to mph
    print(ASOS)
    
    ASOS_year = ASOS.groupby(ASOS.index.year).mean()
    ASOS_year2 = ASOS.groupby(ASOS.index.year).median()

    ASOS_month = ASOS.groupby(ASOS.index.month).mean()
    ASOS_season = month_to_seaon_LUT(ASOS)
    # print(ASOS_year)
    # print(ASOS_year2)
    # print(ASOS_month)
    return ASOS, ASOS_year,ASOS_month

def spd_calc(df):
    
    df['spd_miss'] = np.where((df['Spd'].isnull()),1,0)
    df['spd>=5'] = np.where(df['Spd'] >= 5.0,1,0)     # flags as 1 if the row value meets the condition.
    df['spd>=10'] = np.where(df['Spd'] >= 10.0,1,0)
    df['spd>=15'] = np.where(df['Spd'] >= 15.0,1,0)
    df['spd>=20'] = np.where(df['Spd'] >= 20.0,1,0)    
    print(df)
    df = df.drop(['Dir','Gust Speed','Spd'],axis = 1 )
    
    Wind_speed = df.groupby(df.index.year).sum()
    print(Wind_speed)

def spd_between(df):
    df['spd_miss'] = np.where((df['Spd'].isnull()),1,0)
    df['spd_0->5'] = np.where((df['Spd'] >= 0)&(df['Spd']<5),1,0)     # flags as 1 if the row value meets the condition.
    df['spd_5->10'] = np.where((df['Spd'] > 5)&(df['Spd']<=10),1,0)     # flags as 1 if the row value meets the condition.
    df['spd_10->15'] = np.where((df['Spd'] > 10)&(df['Spd']<=15),1,0)     # flags as 1 if the row value meets the condition.
    df['spd_15->20'] = np.where((df['Spd'] > 15)&(df['Spd']<=20),1,0)     # flags as 1 if the row value meets the condition.
        
    print(df)
    df = df.drop(['Dir','Gust Speed','Spd'],axis = 1 )

    Between_speed = df.groupby(df.index.year).sum()
    print(Between_speed)

    
    
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
   # print(ASOS_season)


    
def plot_dir(df):
    fig, ax = plt.subplots(figsize=(10, 10))  
    ax.plot(df.index.values,df['Dir'])
    ax.set_ylim(0,360)
#    plt.xticks(np.arrange(min(x)+1))
    plt.show()
    
pd.set_option("display.max_rows", 20)    
pd.set_option('display.max_columns', None)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)    


ASOS,ASOS_year,ASOS_month = read_csv()


#spd_calc(ASOS)
spd_between(ASOS)
plot_dir(ASOS_year)
plot_dir(ASOS_month)