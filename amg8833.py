import time
import math
import busio
import board
import adafruit_amg88xx
import matplotlib as cm
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D

i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:512j, 0:7:512j]

while True:
    pixels = np.fliplr(np.rot90(np.asarray(amg.pixels), k=3)).flatten()
    pixels_f = (9/5)*pixels+32
    grid_z = griddata(points, pixels_f, (grid_x, grid_y), method='cubic')
    flat_grid = grid_z.flatten()
    flat_grid = flat_grid[flat_grid >=65]
    flat_grid = flat_grid[flat_grid <=95]
    hist, bin_edges = np.histogram(flat_grid, bins=16)
    grid_z[grid_z < bin_edges[len(bin_edges) - 4]] = 0
    flat_grid = grid_z.flatten()
    filtered_flat_grid = flat_grid[flat_grid > 0]
    hist, bins = np.histogram(filtered_flat_grid, bins=16)
    temp = "{:.2f}".format(np.average(bins[:-1], weights = hist))
    #std = "{:.2f}".format(np.std(filtered_flat_grid))
    #count = "{:,.0f}".format(np.sum(filtered_flat_grid))
    if np.std(filtered_flat_grid) >= 0.75 and np.sum(filtered_flat_grid) >= 300000:
        print("Body temp found: {}".format(temp))
    #print(temp, std, count)
