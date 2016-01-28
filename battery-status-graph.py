#!/usr/bin/python

import argparse
import logging
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
parser.add_argument('--death', type=int, default=5,
                    help='percentage of battery when it is considered dead (default: %(default)s)')
args = parser.parse_args()

def parse_csv_np():
    logging.debug('loading CSV file %s with NumPy', args.logfile)
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

def parse_csv_builtin(fields = ['timestamp', 'energy_full', 'energy_full_design', 'energy_now']):
    import csv
    logging.debug('loading CSV file %s with builtin CSV module', args.logfile)
    log = csv.DictReader(args.logfile)
    data = []
    try:
        for row in log:
            l = tuple([ row[f] for f in fields ])
            data.append(l)
    except csv.Error as e:
        logging.warning('CSV file is corrupt, skipping remaining entries: %s', e)
    logging.debug('building data array')
    return np.array(data, dtype=zip(fields, 'f'*len(fields)))

# the builtin CSV parser above is faster, we went from 8 to 2 seconds
# on our test data here there are probably other ways of making this
# even faster, see:
#
# http://stackoverflow.com/a/25508739/1174784
# http://softwarerecs.stackexchange.com/a/7510/506
#
# TL;DR: performance is currently fine, it could be improved with
# Numpy.fromfile(), Numpy.load() or pandas.read_csv() which should
# apparently all outperform the above code by an order of magnitude
parse_csv = parse_csv_builtin

def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling
    # the default tick locations.
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex']:
        return s + r'$\%$'
    else:
        return s + '%'

def build_graph(data):
    logging.debug('building graph')
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
             linewidth = 0.1,
             color='grey',
             label='current')
    ax.plot(dates, data['energy_full'] / data['energy_full_design'],
             linestyle = '-',
             color = 'red',
             label='effective')

    # legend and labels
    ax.legend(loc='upper right')
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
    
def render_graph():
    if sys.stdout.isatty() and args.outfile == sys.stdout:
        logging.info("drawing on tty")
        plt.show()
    else:
        logging.info('drawing to file %s', args.outfile)
        plt.savefig(args.outfile, bbox_inches='tight')

def guess_expiry(x, y, zero = 0):
    fit = np.polyfit(data['energy_full'], data['timestamp'], 1)
    #print "fit: %s" % fit

    fit_fn = np.poly1d(fit)
    #print "fit_fn: %s" % fit_fn
    return datetime.datetime.fromtimestamp(fit_fn(zero))

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    data = parse_csv()

    # XXX: this doesn't work because it counts all charge/discharge
    # cycles, we'd need to reprocess the CSV to keep only the last
    # continuous states
    #death = guess_expiry(data['energy_now'], data['timestamp'])
    #logging.info("this battery will be depleted in %s, on %s",
    #             death - datetime.datetime.now(), death)

    # actual energy at which the battery is considered dead
    # we compute the mean design capacity, then take the given percentage out of that
    logging.debug('guessing expiry')
    zero = args.death * np.mean(data['energy_full_design']) / 100
    death = guess_expiry(data['energy_full'], data['timestamp'], zero)
    logging.info("this battery will reach end of life (%s%%) in %s, on %s",
                 args.death, death - datetime.datetime.now(), death)

    build_graph(data)
    render_graph()
