import time
import math
import busio
import board
import adafruit_amg88xx
import matplotlib as cm
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D

vmax = 80
vmin = 63
plt.ion()
i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
fig = plt.figure(num='AMG8833 Thermal Scanner');
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:256j, 0:7:256j]

ax = fig.add_subplot(111, projection='3d')
angle = 0
while True:
    pixels = np.fliplr(np.rot90(np.asarray(amg.pixels), k=3)).flatten()
    pixels_f = (9/5)*pixels+32
    grid_0 = griddata(points, pixels_f, (grid_x, grid_y), method='cubic')
    ax.clear()
    surf = ax.plot_surface(grid_x, grid_y, grid_0, cmap="jet", linewidth=0, antialiased=False)
    ax.view_init(80, angle)
    fig.canvas.draw()

plt.show()
