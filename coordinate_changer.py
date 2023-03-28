import numpy as np
import math
import os

#adapted from https://github.com/nicolas-van/egm96-universal

NUM_ROWS = 721
NUM_COLS = 1440

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "WW15MGH.DAC"), "rb") as file:
    dt = np.dtype(np.int16)
    dt = dt.newbyteorder(">")
    x = np.frombuffer(file.read(), dt)
    
    
def _getData(index):
    h=x[index]
    return h

def _getValue(row,col):
    k = row * NUM_COLS + col
    return _getData(k)/100

def _degreesToRadians(degrees):
  return degrees * (math.pi/ 180)

INTERVAL = _degreesToRadians(15 / 60)

def _normalizeRadians(rads, center = 0):
  return rads - (2 * math.pi) * math.floor((rads + math.pi - center) / (2 * math.pi))

def _linearInterpolation(a, b, prop):
  return a + ((b - a) * prop)

def _bilinearInterpolation(topLeft, bottomLeft, bottomRight, topRight, x, y):
  top = _linearInterpolation(topLeft, topRight, x)
  bottom = _linearInterpolation(bottomLeft, bottomRight, x)

  return _linearInterpolation(top, bottom, y)


def meanSeaLevel(latitude, longitude):
  lat = _normalizeRadians(_degreesToRadians(latitude))
  if (lat > math.pi or lat < -math.pi):
    print('Invalid latitude')
  
  lon = _normalizeRadians(_degreesToRadians(longitude))

  topRow = math.floor(((math.pi / 2) - lat) / INTERVAL)

  
  bottomRow = topRow + 1

  leftCol = math.floor(_normalizeRadians(lon, math.pi) / INTERVAL)
  rightCol = (leftCol + 1) % NUM_COLS

  topLeft = _getValue(topRow, leftCol)
  bottomLeft = _getValue(bottomRow, leftCol)
  bottomRight = _getValue(bottomRow, rightCol)
  topRight = _getValue(topRow, rightCol)

  lonLeft = _normalizeRadians(leftCol * INTERVAL)
  latTop = (math.pi / 2) - (topRow * INTERVAL)

  leftProp = (lon - lonLeft) / INTERVAL
  topProp = (latTop - lat) / INTERVAL

  return _bilinearInterpolation(topLeft, bottomLeft, bottomRight, topRight, leftProp, topProp)


def ellipsoidToEgm96(latitude, longitude, altitude):
  ms = meanSeaLevel(latitude, longitude)
  return latitude, longitude, altitude - ms

def egm96ToEllipsoid(latitude, longitude, altitude):
  ms = meanSeaLevel(latitude, longitude)
  return latitude, longitude, altitude + ms


