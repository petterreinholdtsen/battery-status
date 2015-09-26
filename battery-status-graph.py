#!/usr/bin/python

import numpy as np
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import pylab
import time
import datetime

#plt.plot([1,3,4,5], [1,2,3,4])
#plt.ylabel('some numbers')
#plt.show()

dconverter=pylab.strpdate2num('%s')

def tconvert(t):
    return time.localtime(int(t))

def npconverter(t):
    return np.datetime64('1970-01-01') + np.timedelta64(int(t), 's')

def nullconverter(t):
    return t

def parse_csv_np():
    data = np.genfromtxt('/var/log/hjemmenett-battery-status.log',
                         delimiter=',', names=True,
                         filling_values = 0.0)
    # convert timestamp to datetime, but also select only relevant
    # fields to avoid having to specify all
    #return data.astype([('timestamp', 'datetime64[s]'),
    #                    ('energy_full', 'f'),
    #                    ('energy_full_design', 'f'),
    #                    ('energy_now', 'f')])
    return data

def parse_csv():
    import csv
    with open('/var/log/hjemmenett-battery-status.log', 'rb') as csvfile:
        log = csv.DictReader(csvfile)
        for row in log:
            row['timestamp'] = time.localtime(int(row['timestamp']))
            print time.strftime('%Y-%m-%d %H:%M:%S', row['timestamp']), row['energy_full'], row['energy_full_design'], row['energy_now']

def plot():
    #parse_csv()
    data = parse_csv_np()
    print data['timestamp']
    #plt.gca().xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d'))
    #plt.gca().xaxis.set_major_locator(md.DayLocator())
    #plt.xkcd()
    # create vectorized converter (can take list-like objects as arguments)
    dateconv = np.vectorize(datetime.datetime.fromtimestamp)
    dates = dateconv(data['timestamp'])
    #plt.plot(dates, data['energy_now'], '-b', data['energy_full'], '-r')
    plt.plot(dates, data['energy_full_design'], '-k')
    plt.plot(dates, data['energy_now'], '-b')
    plt.plot(dates, data['energy_full'], '-r')
    #plt.tight_layout()
    plt.show()

plot()
