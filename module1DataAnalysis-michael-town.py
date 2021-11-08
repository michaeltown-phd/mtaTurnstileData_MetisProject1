#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 14:26:51 2021

@author: michaeltown
"""

## beginning of module 1 MVP data analysis

import numpy as np
import pandas as pd
import os as os
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns


## filter functions

# from year to year each SCP jumps a lot
def filterLargeDiff(x):
    if (x < 2500) & (x > 0):
        return x;
    else:
        return np.nan;

def weekdayfilter(x):
    return x.DOW < 5;

dataFileLoc = '/home/michaeltown/work/metis/modules/exploratoryDataAnalysis/data/mtaDataAprils2015-2019.csv';

mtaData = pd.read_csv(dataFileLoc);

# convert date time
mtaData['DATETIME'] = pd.to_datetime(mtaData.DATE + ' ' +mtaData.TIME);
mtaData['HOUR'] = mtaData.DATETIME.dt.hour

# group data by unit (test one unit first), but loop through units later, x-check with locations of starbucks

hourlyBins = [0,4,8,12,16,20,24];
hourlyLabels= ['0-4','4-8','8-12','12-16','16-20','20-24'];

# test case 
stationNames = ['BROOKLYN BRIDGE', 'CITY HALL'];

#for station in mtaData.STATION.unique():  #used this to loop through all data in exploratory analysis
for station in stationNames:
    
    mtaDataBB = mtaData[(mtaData.STATION == station)].loc[:,['DATE', 'UNIT','SCP','TIME','HOUR','DATETIME','STATION','ENTRIES','EXITS']];
    mtaDataBB = mtaDataBB.sort_values(by=['UNIT','SCP']);
    mtaDataBB['NEXT_ENTRIES'] = mtaDataBB.ENTRIES.shift(-1);
    mtaDataBB['NEXT_EXITS'] = mtaDataBB.EXITS.shift(-1);
    mtaDataBB['DOW'] = mtaDataBB.DATETIME.dt.dayofweek;
    mtaDataBB['WKDAY'] = mtaDataBB.DOW < 5;
    mtaDataBB['WKEND'] = mtaDataBB.DOW > 4;
    wkdayid = lambda x : 'WKDAY' if x < 5 else 'WKEND';
    mtaDataBB['WKDAYID'] = mtaDataBB.DOW.apply(wkdayid);
    
    mtaDataBB.dropna();
    
    # find the entries and exits each 4 hour time period, 
    mtaDataBB['ENTRIES_4HR'] = mtaDataBB.NEXT_ENTRIES-mtaDataBB.ENTRIES;
    mtaDataBB['EXITS_4HR'] = mtaDataBB.NEXT_EXITS-mtaDataBB.EXITS;
    
    # filter for the year-to-year jumps
    mtaDataBB.ENTRIES_4HR = mtaDataBB.ENTRIES_4HR.apply(filterLargeDiff);
    mtaDataBB.EXITS_4HR = mtaDataBB.EXITS_4HR.apply(filterLargeDiff);
    
    mtaDataBB['hourlyBins'] = pd.cut(mtaDataBB.HOUR,bins = hourlyBins, labels = hourlyLabels, right = False, include_lowest = True);
    
    
    # group the data and sum over each 4-hourly bin for all days of the week
    gMtaDataBBsum = mtaDataBB.groupby(['hourlyBins'])['ENTRIES_4HR','EXITS_4HR'].sum();
    gMtaDataBBmean = mtaDataBB.groupby(['hourlyBins'])['ENTRIES_4HR','EXITS_4HR'].mean();
    gMtaDataBBstd = mtaDataBB.groupby(['hourlyBins'])['ENTRIES_4HR','EXITS_4HR'].agg(np.std);

    # for weekdays and weekends
    gMtaDataBB_WKDAYsum = mtaDataBB.groupby(['hourlyBins','WKDAYID'])['ENTRIES_4HR','EXITS_4HR'].sum();    
    gMtaDataBB_WKDAYmean = mtaDataBB.groupby(['hourlyBins','WKDAYID'])['ENTRIES_4HR','EXITS_4HR'].mean();
    gMtaDataBB_WKDAYstd = mtaDataBB.groupby(['hourlyBins','WKDAYID'])['ENTRIES_4HR','EXITS_4HR'].agg(np.std);

    # unstack data
    gMtaDataBB_WKDAYsum = gMtaDataBB_WKDAYsum.unstack(level= 1);     
    gMtaDataBB_WKDAYmean = gMtaDataBB_WKDAYmean.unstack(level = 1); 
    gMtaDataBB_WKDAYstd = gMtaDataBB_WKDAYstd.unstack(level = 1);
    
    # group by morning traffic and day of the week
    # group by weekend vs weekday traffic flow
    
    # sns attempt
    # fig1 = plt.figure();
    # sns.relplot(x='hourlyBins',y='EXITS_4HR', data = mtaDataBB, kind = 'line',hue = 'DOW')
    # plt.title(station+' sns plot separated by weekday');
    # plt.show();
    # this attempt did not produce believable confidence limits. need to learn more about what
    # sns is doing here before I use it.
    # sns did indicate not much difference across weekdays for Brooklyn Bridge, but difference
    # between weekday and weekend for Brooklyn Bridge
    
    
    # plot all the data
    fig1 = plt.figure();
    ax = fig1.add_subplot(111);
    lbEnt = gMtaDataBBmean.ENTRIES_4HR/4-gMtaDataBBstd.ENTRIES_4HR/4;
    ubEnt = gMtaDataBBmean.ENTRIES_4HR/4+gMtaDataBBstd.ENTRIES_4HR/4
    plt.plot([2,6,10,14,18,22],gMtaDataBBmean.ENTRIES_4HR/4,'b-');
    ax.fill_between([2,6,10,14,18,22],ubEnt,lbEnt, color='blue',alpha = 0.2);        
    lbExt = gMtaDataBBmean.EXITS_4HR/4-gMtaDataBBstd.EXITS_4HR/4;
    ubExt = gMtaDataBBmean.EXITS_4HR/4+gMtaDataBBstd.EXITS_4HR/4
    plt.plot([2,6,10,14,18,22],gMtaDataBBmean.EXITS_4HR/4,'k-.');
    ax.fill_between([2,6,10,14,18,22],ubExt,lbExt, color='black',alpha = 0.2);        

    plt.title('Entries/exits for ' + station + ' Station April, 2016-2019');
    plt.xlabel('hour of day');
    plt.ylabel('Entries/exits per hour');
    plt.ylim([-10,300]);
    plt.xlim([0,23]);
    plt.grid();
    plt.legend(['entries','exits'],loc = 'upper left');
    plt.show;
    os.chdir('/home/michaeltown/work/metis/modules/exploratoryDataAnalysis/figures')
    fig1.savefig(station.replace(' ','').replace('/','')+'timeSeries_April_2016-2019.jpg')


    # weekday and weekend plots
    fig2 = plt.figure();
    ax = fig2.add_subplot(111);
    lbEnt = gMtaDataBB_WKDAYmean.ENTRIES_4HR.WKDAY/4-gMtaDataBB_WKDAYstd.ENTRIES_4HR.WKDAY/4;
    ubEnt = gMtaDataBB_WKDAYmean.ENTRIES_4HR.WKDAY/4+gMtaDataBB_WKDAYstd.ENTRIES_4HR.WKDAY/4
    plt.plot([2,6,10,14,18,22],gMtaDataBB_WKDAYmean.ENTRIES_4HR.WKDAY/4,'-',color = 'deepskyblue');
    ax.fill_between([2,6,10,14,18,22],ubEnt,lbEnt, color='deepskyblue',alpha = 0.2);        
    lbExt = gMtaDataBB_WKDAYmean.EXITS_4HR.WKDAY/4-gMtaDataBB_WKDAYstd.EXITS_4HR.WKDAY/4;
    ubExt = gMtaDataBB_WKDAYmean.EXITS_4HR.WKDAY/4+gMtaDataBB_WKDAYstd.EXITS_4HR.WKDAY/4
    plt.plot([2,6,10,14,18,22],gMtaDataBB_WKDAYmean.EXITS_4HR.WKDAY/4,'-.',color='mediumseagreen');
    ax.fill_between([2,6,10,14,18,22],ubExt,lbExt, color='mediumseagreen',alpha = 0.2);        

    plt.title('WKDAY Ent/ext for ' + station + ' Station April, 2016-2019');
    plt.xlabel('hour of day');
    plt.ylabel('Entries/exits per hour');
    plt.ylim([-10,300]);
    plt.xlim([0,23]);
    plt.grid();
    plt.legend(['entries','exits'],loc = 'upper left');
    plt.show;
    os.chdir('/home/michaeltown/work/metis/modules/exploratoryDataAnalysis/figures')
    fig2.savefig(station.replace(' ','').replace('/','')+'-WKDAY-timeSeries_April_2016-2019.jpg')

    fig3 = plt.figure();
    ax = fig3.add_subplot(111);
    lbEnt = gMtaDataBB_WKDAYmean.ENTRIES_4HR.WKEND/4-gMtaDataBB_WKDAYstd.ENTRIES_4HR.WKEND/4;
    ubEnt = gMtaDataBB_WKDAYmean.ENTRIES_4HR.WKEND/4+gMtaDataBB_WKDAYstd.ENTRIES_4HR.WKEND/4
    plt.plot([2,6,10,14,18,22],gMtaDataBB_WKDAYmean.ENTRIES_4HR.WKEND/4,'m-');
    ax.fill_between([2,6,10,14,18,22],ubEnt,lbEnt, color='magenta',alpha = 0.2);        
    lbExt = gMtaDataBB_WKDAYmean.EXITS_4HR.WKEND/4-gMtaDataBB_WKDAYstd.EXITS_4HR.WKEND/4;
    ubExt = gMtaDataBB_WKDAYmean.EXITS_4HR.WKEND/4+gMtaDataBB_WKDAYstd.EXITS_4HR.WKEND/4
    plt.plot([2,6,10,14,18,22],gMtaDataBB_WKDAYmean.EXITS_4HR.WKEND/4,'-.',color = 'orange');
    ax.fill_between([2,6,10,14,18,22],ubExt,lbExt, color='orange',alpha = 0.2);        

    plt.title('WKEND Ent/ext for ' + station + ' Station April, 2016-2019');
    plt.xlabel('hour of day');
    plt.ylabel('Entries/exits per hour');
    plt.ylim([-10,300]);
    plt.xlim([0,23]);
    plt.grid();
    plt.legend(['entries','exits'],loc = 'upper left');
    plt.show;
    os.chdir('/home/michaeltown/work/metis/modules/exploratoryDataAnalysis/figures')
    fig3.savefig(station.replace(' ','').replace('/','')+'-WKEND-timeSeries_April_2016-2019.jpg')


    fig4 = plt.figure();
    plt.hist(mtaDataBB.ENTRIES_4HR,bins = range(0,2000,50),color = 'blue',alpha = 0.5);
    plt.hist(mtaDataBB.EXITS_4HR,bins = range(0,2000,50),color = 'black',alpha = 0.5);
    plt.xlim([-50,2050]);
    plt.ylim([-10,6000]);
    plt.title('Entries/Exits for ' + station + ', April 2016-2019');
    plt.ylabel('Counts');
    plt.legend(['Entries','Exits'])
    plt.xlabel('entries/exits every 4 hours');    
    os.chdir('/home/michaeltown/work/metis/modules/exploratoryDataAnalysis/figures')
    fig4.savefig(station.replace(' ','').replace('/','')+'histogram_April_2016-2019.jpg')
    

