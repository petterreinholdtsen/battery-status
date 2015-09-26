#!/usr/bin/python

import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sys
import time
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('logfile', nargs='?', type=argparse.FileType('r'),
                    default=sys.stdin,
                    help='logfile to read (default: stdin)')
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                    default=sys.stdout,
                    help='image to write (default to terminal if available, otherwise stdout)')
args = parser.parse_args()

def parse_csv_np():
    data = np.genfromtxt(args.logfile,
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

def parse_csv(fields = ['timestamp', 'energy_full', 'energy_full_design', 'energy_now']):
    import csv
    log = csv.DictReader(args.logfile)
    data = []
    for row in log:
        l = tuple([ row[f] for f in fields ])
        data.append(l)
    return np.array(data, dtype=zip(fields, 'f'*len(fields)))

def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling
    # the default tick locations.
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex']:
        return s + r'$\%$'
    else:
        return s + '%'

def plot():
    data = parse_csv()
    # create vectorized converter (can take list-like objects as
    # arguments)
    dateconv = np.vectorize(datetime.datetime.fromtimestamp)
    dates = dateconv(data['timestamp'])

    fig, ax = plt.subplots()

    # XXX: can't seem to plot all at once...
    #plt.plot(dates, data['energy_now'], '-b', data['energy_full'], '-r')
    # ... but once at a time seems to do the result i am looking for
    ax.plot(dates, data['energy_full_design'] / data['energy_full_design'],
             linestyle = '-',
             color = 'black',
             label='design')
    ax.plot(dates, data['energy_now'] / data['energy_full_design'],
             linestyle = '-',
             color='grey',
             label='current')
    ax.plot(dates, data['energy_full'] / data['energy_full_design'],
             linestyle = '-',
             color = 'red',
             label='effective')

    # legend and labels
    ax.legend(loc='lower left')
    ax.set_xlabel('time')
    ax.set_ylabel('percent')
    ax.set_title('Battery capacity statistics')

    # Tell matplotlib to interpret the x-axis values as dates
    ax.xaxis_date()
    # Make space for and rotate the x-axis tick labels
    fig.autofmt_xdate()

    # Create the formatter using the function to_percent. This
    # multiplies all the dfault labels by 100, making them all
    # percentages
    formatter = FuncFormatter(to_percent)

    # Set the formatter
    ax.yaxis.set_major_formatter(formatter)

    if sys.stdout.isatty() and args.outfile == sys.stdout:
        print "drawing on tty"
        plt.show()
    else:
        plt.savefig(args.outfile, bbox_inches='tight')

plot()
