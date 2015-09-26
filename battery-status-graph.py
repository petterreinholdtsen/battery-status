#!/usr/bin/python

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.ticker import FuncFormatter
import pylab
import sys
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

def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] == True:
        return s + r'$\%$'
    else:
        return s + '%'

def plot():
    data = parse_csv_np()
    # create vectorized converter (can take list-like objects as arguments)
    dateconv = np.vectorize(datetime.datetime.fromtimestamp)
    dates = dateconv(data['timestamp'])

    fig, ax = plt.subplots()

    # XXX: can't seem to plot all at once...
    #plt.plot(dates, data['energy_now'], '-b', data['energy_full'], '-r')
    # ... but once at a time seems to do the result i am looking for
    plt.plot(dates, data['energy_full_design'] / data['energy_full_design'] , '-k')
    plt.plot(dates, data['energy_now']  / data['energy_full_design'], '-b')
    plt.plot(dates, data['energy_full'] / data['energy_full_design'], '-r')

    # Tell matplotlib to interpret the x-axis values as dates
    ax.xaxis_date()
    # Make space for and rotate the x-axis tick labels
    fig.autofmt_xdate()

    # Create the formatter using the function to_percent. This multiplies all the
    # dfault labels by 100, making them all percentages
    formatter = FuncFormatter(to_percent)

    # Set the formatter
    plt.gca().yaxis.set_major_formatter(formatter)

    if sys.stdout.isatty():
        print "drawing on tty"
        plt.show()
    else:
        image = 'battery-graph.png'
        print "writing to image %s" % image
        plt.savefig(image, bbox_inches='tight')

plot()
