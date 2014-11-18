from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph
import httplib
import csv
import numpy
from datetime import datetime


def seconds(dt):
  return int((dt-datetime(1970, 1, 1)).total_seconds())


def fetch_data(start=0):
  conn = httplib.HTTPConnection('api.bitcoincharts.com')
  url = '/v1/trades.csv?symbol=bitstampUSD'
  if start > 0:
    url += '&start=' + str(int(start))
  print 'Fetching', url, '...'
  conn.request('GET', url)
  res = conn.getresponse()
  data = res.read()
  lines = data.splitlines(True)
  data = []
  for row in csv.reader(lines):
    data.append([int(row[0]), float(row[1])])
  print 'Fetched', len(data), 'data points'
  print data[0], data[-1]
  return numpy.array(data)


def fetch_all():
  conn = httplib.HTTPConnection('api.bitcoincharts.com')
  url = '/v1/csv/bitstampUSD.csv.gz'
  print 'Fetching', url, '...'
  conn.request('GET', url)
  res = conn.getresponse()
  data = res.read()
  # TODO: decode gzip (33MB)
  print data
  # data = []
  # for row in csv.reader(lines):
  #   data.append([int(row[0]), float(row[1])])
  # print 'Fetched', len(data), 'data points'
  # return numpy.array(data)

  # data = fetch_data(seconds(datetime.now()))
  # print data
  # last = data[len(data)-1][0]
  # while last > seconds(since):
  #   cur = fetch_data(last)
  #   print cur
  #   data = numpy.concatenate((data, cur), axis=0)
  #   last = data[len(data)-1][0]
  # return data


def segment(data, duration):
  last = data[0][0]
  segments = []
  seg = []
  for i in range(len(data)):
    stamp = data[i][0]
    price = data[i][1]
    seg.append(price)
    if abs(stamp - last) > duration:
      segments.append([stamp, sum(seg)/len(seg)])
      seg = []
      last = stamp
  return numpy.array(segments)


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

  btc_plot = p.plot()
  seg_plot = p.plot(pen=pyqtgraph.mkPen('fff', width=2))

  def update(btc_plot, seg_plot):
    # TODO: calculate in separate thread
    # data = fetch_data(1416075331)
    data = fetch_data(1410000000)
    temp = fetch_data(1415912984)
    data = numpy.concatenate((data, temp), axis=0)
    temp = fetch_data(1416046133)
    data = numpy.concatenate((data, temp), axis=0)
    temp = fetch_data(1416246762)
    data = numpy.concatenate((data, temp), axis=0)
    temp = fetch_data(1416275152)  # ..
    data = numpy.concatenate((data, temp), axis=0)
    # TODO: -> fetch_all
    # segments = segment(data, 1800)
    btc_plot.setData(data)
    # seg_plot.setData(segments)

  # timer = QtCore.QTimer()
  # timer.timeout.connect(lambda: update(btc_plot, seg_plot))
  # timer.start(10000)
  update(btc_plot, seg_plot)

  QtGui.QApplication.instance().exec_()
