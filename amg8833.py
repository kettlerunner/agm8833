import time
import math
import busio
import board
import adafruit_amg88xx
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

vmax = 80
vmin = 63
plt.ion()
i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
fig = plt.figure(num='AMG8833 Thermal Scanner');
fig = plt.figure()

ax = fig.add_subplot(111)
ax.set_yticklabels([])
ax.set_xticklabels([])
im = ax.imshow(amg.pixels, cmap='jet', vmin=vmin, vmax=vmax)
fig.colorbar(im, ax=ax)
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:512j, 0:7:512j]

ax2 = fig.add_subplot(222)
hist = ax2.hist(amg.pixels, bins = int(180/5))

while True:
    ax.set_title("Max Temp Found: {0:.1f}F".format(np.amax((9/5)*np.amax(amg.pixels)+32)))
    pixels = np.fliplr(np.rot90(np.asarray(amg.pixels), k=3)).flatten()
    pixels_f = (9/5)*pixels+32
    ax.set_title("Max Temp Found: {0:.1f}F".format(np.amax(pixels_f )))
    grid_0 = griddata(points, pixels_f, (grid_x, grid_y), method='cubic')
    im.set_data(grid_0)
    #hist.set_data(grid_0)
    fig.canvas.draw()
