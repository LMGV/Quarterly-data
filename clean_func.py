import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler as stdz
import os

def clean(dataset, save = False, name = None):
    data2 = dataset.drop(dataset.columns[range(0,8)], axis=1)
    data2 = dataset.drop(dataset.columns[range(0,8)], axis=1)
    data2 = data2.reset_index()
    data2 = data2.drop(range(0, 26), axis = 0)
    data2 = data2.reset_index()
    data2 = data2.drop(data2.columns[range(0,4)], axis=1)
    data2 = data2.drop(["Name", "Averages", "Current Price", "Currency", "EarningsRealeaseDate", "Overall_Mean"], 
                       axis=1)
    if data1["Beta"].value_counts().keys().size == 1:
        data2 = data2.drop(["Beta"], axis=1)
    
    # drop the rank columns
    data3 = pd.DataFrame()
    for i in range(0, len(data2.columns)):
        if data2.columns[i][0:4] != "Rank":
            data3[data2.columns[i]] = data2.iloc[:,i]
    
    # Drop companies that don't have F-Score
    data4 = data3[pd.isna(data3["F-Score"]) == False]

    # Drop companies that don't have z-Score
    data4 = data4[pd.isna(data4["Zscore"]) == False]
    
    # Now drop variables that have more than 25% of NaN values
    no_nan = [data4.iloc[:,i].isna().sum() for i in range(2, len(data4.columns))]

    drop = []
    for i in range(2,len(data4.columns)):
        if no_nan[i-2] > len(data4)/4:
            drop.append(i)

    data5 = data4.drop(data4.columns[drop], axis = 1)
    
    # drop all rows that contain NaN values
    data6 = data5.dropna().astype(float, errors="ignore")
    
    # check if there are any incorrectly coded industries
    if len(data6[data6['Industry Sector'].apply(lambda x: type(x)!=str)]) > 0:
        data6.drop(data6[data6['Industry Sector'].apply(lambda x: type(x)!=str)].index , inplace=True)
    
    # check for duplicates
    if sum(data6.duplicated()) > 0:
        data6.drop_duplicates(keep="first", inplace=True)
        
    # drop outliers (2.5%)
    data_q = data6.iloc[:,2:].quantile([0.025, 0.975])
    data7 = pd.concat([data6.iloc[:,:2], 
                       data6.iloc[:,2:].apply(lambda x: x[(x > data_q.loc[0.025,x.name]) & 
                                                          (x < data_q.loc[0.975,x.name])], 
                                              axis=0)], axis=1)
    data7.dropna(inplace=True)
    
    # standardize
    scaler = stdz(with_std=True, with_mean=True)

    scaler.fit(data7.iloc[:,2:])

    data8 = pd.DataFrame(scaler.transform(data7.iloc[:,2:].values), columns=data7.columns.values[2:])
    #data8 = pd.concat([data7.iloc[:,:2], data8], axis=1)
    
    if save == True:
        data8.to_excel(str(name) + ".xlsx", index = False)
    
    return data8
    
def draw_boxplots(dataset, save = False, name = None):
    fig, axes = plt.subplots(math.ceil(len(dataset.columns)/6),6,figsize = (15,3.83*math.ceil(len(dataset.columns)/6)))
    k = 0
    for i in range(0, math.ceil(len(dataset.columns)/6)):
        for j in range(0, 6):
            axes[i,j].boxplot(dataset[str(dataset.columns.values[k])])
            axes[i,j].set_title(dataset.columns.values[k])
            k += 1
            if k == len(dataset.columns): break
                
    if len(dataset.columns) % 6 != 0:
        for a in range(len(dataset.columns) % 6, 6):
            fig.delaxes(axes[math.ceil(len(dataset.columns)/6)-1,a])
    
    if name != None:
        fig.suptitle("Boxplots for cleaned, standardized dataset without outliers (" + name + ")", fontsize=14)
    else: fig.suptitle("Boxplots for cleaned, standardized dataset without outliers", fontsize=14)
        
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    
    if save == True:
        plt.savefig(str(name) + ".png")
        
    plt.show()