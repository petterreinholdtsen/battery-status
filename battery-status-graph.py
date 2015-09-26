#!/usr/bin/python

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as md
import pylab
import time
import datetime

def parse_csv_np():
    data = np.genfromtxt('/var/log/hjemmenett-battery-status.log',
                         delimiter=',', names=True,
                         filling_values = 0.0)
    # convert timestamp to datetime, but also select only relevant
    # fields to avoid having to specify all
    # XXX: it seems that datetime is not what plot expects, so stick
    # with float and we convert later    
    #return data.astype([('timestamp', 'datetime64[s]'),
    #                    ('energy_full', 'f'),
    #                    ('energy_full_design', 'f'),
    #                    ('energy_now', 'f')])
    return data

def plot():
    data = parse_csv_np()
    # create vectorized converter (can take list-like objects as arguments)
    dateconv = np.vectorize(datetime.datetime.fromtimestamp)
    dates = dateconv(data['timestamp'])
    # XXX: can't seem to plot all at once...
    #plt.plot(dates, data['energy_now'], '-b', data['energy_full'], '-r')
    # ... but once at a time seems to do the result i am looking for
    plt.plot(dates, data['energy_full_design'] , '-k')
    plt.plot(dates, data['energy_now'], '-b')
    plt.plot(dates, data['energy_full'], '-r')
    plt.show()

plot()
