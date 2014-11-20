from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph
import httplib
import json
import numpy
from datetime import datetime


class Exchange(object):
  BITSTAMP = 'Bitstamp'


class Currency(object):
  USD = 'usd'


class Term(object):
  MIN10 = '10min'
  HOUR = '1h'
  DAY = '24h'
  WEEK = '1w'
  MONTH = '1m'
  MONTH3 = '3m'
  MONTH6 = '6m'
  YEAR = '1y'
  YEAR2 = '2y'


def fetch_data(exchange=Exchange.BITSTAMP,
               currency=Currency.USD,
               term=Term.WEEK):
  conn = httplib.HTTPConnection('bitcoinstat.org')
  url = '/api_v3/chart/' + \
        '?exchange=' + exchange + \
        '&currency=' + currency + \
        '&term=' + term
  print 'Fetching', url, '...'
  conn.request('GET', url)
  res = conn.getresponse()
  data = json.load(res)
  return data['data']

"""
DATA from bitcoinstat.org
{
  "request": "chart",
  "code": 200,
  "status": "Success",
  "data": {
    "currency": "usd",
    "source": "trades",
    "exchange": "Bitstamp",
    "info": {
      "sell": "377.26",
      "volume": "9372.43",
      "updated": "2014-11-19 22:22:11",
      "buy": "376.49",
      "last": "377.26",
      "timestamp": "1416435731",
      "high": "453.92",
      "low": "369",
      "change": "-43.32"
    },
    "chart": [
      {
        "high": 386.39,
        "timestamp": 1416435824,
        "price": 377.26,
        "low": 371.7,
        "market": 0
      },
      ...
    ]
  }
}
"""


def get_prices(data):
  return [val['price'] for val in data['chart']]


def get_timestamps(data):
  return [val['timestamp'] for val in data['chart']]


def sma(data, window=20):
  averages = []
  for i in reversed(range(len(data))):
    if i >= window:
      averages.insert(0, sum(data[i-window:i])/window)
    else:
      averages.insert(0, averages[0])
  return averages


class DateAxis(pyqtgraph.AxisItem):
  def tickStrings(self, values, scale, spacing):
    ticks = []
    if values:
      rng = max(values)-min(values)
      if rng < 3600:  # < hour
        format = '%H:%M:%S'
      elif rng < 3600*24:  # < day
        format = '%H:%M'
      elif rng < 3600*24*30:  # < month
        format = '%d'
      elif rng < 3600*24*30*24:  # < year
        format = '%b'
      elif rng >= 3600*24*30*24:  # > year
        format = '%Y'
      for x in values:
        try:
          ticks.append(datetime.fromtimestamp(x).strftime(format))
        except ValueError:
          ticks.append('')
    return ticks


def plot_preset_month(p):
  data = fetch_data(term=Term.MONTH)
  timestamps = get_timestamps(data)
  prices = get_prices(data)
  p.plot(timestamps, prices, name='prices',
         pen={'color': 'a0a0a0', 'width': 2})
  p.plot(timestamps, sma(prices, window=15), name='sma15',
         pen={'color': 'ff0000', 'width': 2})
  p.plot(timestamps, sma(prices, window=50), name='sma50',
         pen={'color': 'ffff00', 'width': 2})
  p.plot(timestamps, sma(prices, window=100), name='sma100',
         pen={'color': '00ff00', 'width': 2})


def plot_preset_week(p):
  data = fetch_data(term=Term.WEEK)
  timestamps = get_timestamps(data)
  prices = get_prices(data)
  p.plot(timestamps, prices, name='prices',
         pen={'color': 'a0a0a0', 'width': 2})
  p.plot(timestamps, sma(prices, window=5), name='sma5',
         pen={'color': 'ff0000', 'width': 2})
  p.plot(timestamps, sma(prices, window=20), name='sma20',
         pen={'color': 'ffff00', 'width': 2})
  p.plot(timestamps, sma(prices, window=50), name='sma50',
         pen={'color': '00ff00', 'width': 2})


def plot_preset_day(p):
  data = fetch_data(term=Term.DAY)
  timestamps = get_timestamps(data)
  prices = get_prices(data)
  p.plot(timestamps, prices, name='prices',
         pen={'color': 'a0a0a0', 'width': 2})
  p.plot(timestamps, sma(prices, window=15), name='sma15',
         pen={'color': 'ff0000', 'width': 2})
  p.plot(timestamps, sma(prices, window=50), name='sma50',
         pen={'color': 'ffff00', 'width': 2})
  p.plot(timestamps, sma(prices, window=100), name='sma100',
         pen={'color': '00ff00', 'width': 2})


if __name__ == '__main__':
  # Enable antialiasing for prettier plots
  pyqtgraph.setConfigOptions(antialias=True)

  app = pyqtgraph.mkQApp()
  axis = DateAxis(orientation='bottom')
  vb = pyqtgraph.ViewBox()
  p = pyqtgraph.PlotWidget(viewBox=vb, axisItems={'bottom': axis})
  p.show()
  p.resize(1000, 600)
  p.setWindowTitle('Bitstamp market data')
  p.addLegend(offset=(800, 30))

  plot_preset_month(p)

  # timer = QtCore.QTimer()
  # timer.timeout.connect(lambda: update(btc_plot, seg_plot))
  # timer.start(10000)
  QtGui.QApplication.instance().exec_()
