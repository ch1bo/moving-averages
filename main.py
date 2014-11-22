from pyqtgraph.Qt import QtGui
import pyqtgraph
import httplib
import json
from datetime import datetime
import operator

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

def fetch_chart(exchange=Exchange.BITSTAMP,
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

def chart_prices(data):
  return [val['price'] for val in data['chart']]

def chart_timestamps(data):
  return [val['timestamp'] for val in data['chart']]

def fetch_trades(exchange=Exchange.BITSTAMP,
                 currency=Currency.USD,
                 since=1416000000):
  conn = httplib.HTTPConnection('bitcoinstat.org')
  url = '/api_v3/trades/' + \
        '?exchanges=' + exchange + \
        '&currency=' + currency + \
        '&since=' + str(since)
  print 'Fetching', url, '...'
  conn.request('GET', url)
  res = conn.getresponse()
  data = json.load(res)
  return data['trades']

MAX_TRADES = 5000

def fetch_all_trades(exchange=Exchange.BITSTAMP,
                     currency=Currency.USD,
                     since=1416000000):
  data = fetch_trades(exchange, currency, since)
  i = 1
  while len(data) == MAX_TRADES*1:
    last = int(data[-1]['timestamp'])
    data = fetch_trades(exchange, currency, last) + data
    i += 1
    print len(data), data[0]['timestamp'], data[-1]['timestamp']
  return data

"""
TRADES DATA
{
    "count": "5000",
    "status": "Success",
    "code": 200,
    "last": "1416515624",
    "request": "trades",
    "trades": [
      {
          "currency": "usd",
          "price": "354.95",
          "amount": "0.028173",
          "timestamp": "1416482199",
          "exchange": "Bitstamp"
      },
      ...
    ]
}
"""

def trade_timestamps(data):
  return [int(val['timestamp']) for val in data]

def trade_prices(data):
  return [float(val['price']) for val in data]


def sma(data, window=20):
  averages = []
  for i in reversed(range(len(data))):
    if i >= window:
      averages.insert(0, sum(data[i-window:i])/window)
    else:
      averages.insert(0, averages[0])
  return averages

def ema(data, window=20):
  averages = sma(data, window)
  if window > 1:
    mul = 2.0 / (window + 1)
    for i in range(len(averages)):
      if i >= window:
        averages[i] = data[i] * mul + averages[i-1] * (1-mul)
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
  data = fetch_chart(term=Term.MONTH)
  timestamps = chart_timestamps(data)
  prices = chart_prices(data)
  p.plot(timestamps, prices, name='prices',
         pen={'color': 'a0a0a0', 'width': 2})
  p.plot(timestamps, sma(prices, window=15), name='sma15',
         pen={'color': 'ff0000', 'width': 2})
  p.plot(timestamps, sma(prices, window=50), name='sma50',
         pen={'color': 'ffff00', 'width': 2})
  p.plot(timestamps, sma(prices, window=100), name='sma100',
         pen={'color': '00ff00', 'width': 2})
  return timestamps, prices

def plot_preset_week(p):
  data = fetch_chart(term=Term.WEEK)
  timestamps = chart_timestamps(data)
  prices = chart_prices(data)

  ema12 = ema(prices, window=12)
  ema26 = ema(prices, window=26)

  p.plot(timestamps, prices, name='prices',
         pen={'color': 'a0a0a0', 'width': 2})
  p.plot(timestamps, ema12, name='ema12',
         pen={'color': 'ff0000', 'width': 2})
  p.plot(timestamps, ema26, name='ema26',
         pen={'color': 'ffff00', 'width': 2})
  p.plot(timestamps, sma(prices, window=50), name='sma50',
         pen={'color': '00ff00', 'width': 2})
  return timestamps, prices

def plot_preset_day(p):
  data = fetch_chart(term=Term.DAY)
  timestamps = chart_timestamps(data)
  prices = chart_prices(data)
  p.plot(timestamps, prices, name='prices',
         pen={'color': 'a0a0a0', 'width': 2})
  p.plot(timestamps, sma(prices, window=15), name='sma15',
         pen={'color': 'ff0000', 'width': 2})
  p.plot(timestamps, sma(prices, window=30), name='sma30',
         pen={'color': 'ffff00', 'width': 2})
  p.plot(timestamps, sma(prices, window=100), name='sma100',
         pen={'color': '00ff00', 'width': 2})
  return timestamps, prices

def plot_macd(p, timestamps, prices):
  ema12 = ema(prices, window=12)
  ema26 = ema(prices, window=26)
  macd1 = map(operator.sub, ema12, ema26)
  macd2 = ema(macd1, window=9)
  p.plot(timestamps, macd1, name='macd',
         pen={'color': 'c0c0c0', 'width': 2})
  p.plot(timestamps, macd2, name='macd_trigger',
         pen={'color': 'ffff00', 'width': 2})

if __name__ == '__main__':
  # Enable antialiasing for prettier plots
  pyqtgraph.setConfigOptions(antialias=True)

  win = pyqtgraph.GraphicsWindow(title="Bitstamp market analysis")
  win.resize(1000, 800)

  axis = DateAxis(orientation='bottom')
  p = win.addPlot(axisItems={'bottom': axis})
  p.show()
  p.addLegend(offset=(800, 30))
  timestamps, prices = plot_preset_week(p)

  win.nextRow()

  axis2 = DateAxis(orientation='bottom')
  p2 = win.addPlot(axisItems={'bottom': axis2})
  p2.show()
  plot_macd(p2, timestamps, prices)


  # - Fetch raw data
  # data = fetch_all_trades()
  # timestamps = trade_timestamps(data)
  # prices = trade_prices(data)
  # p.plot(timestamps, prices, name='prices',
  #        pen={'color': 'a0a0a0', 'width': 2})

  # - Register an update timer
  # timer = QtCore.QTimer()
  # timer.timeout.connect(lambda: update(btc_plot, seg_plot))
  # timer.start(10000)
  QtGui.QApplication.instance().exec_()
