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
import seaborn as sns

#vmax = 80
#vmin = 63
#plt.ion()
i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
#fig = plt.figure(num='AMG8833 Thermal Scanner', figsize=(8.0, 4.0));
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:512j, 0:7:512j]
#ax = fig.add_subplot(121, projection='3d')
#ax.set_axis_off()
#angle = 0
#ax1 = fig.add_subplot(122)
#angle = 0
while True:
    pixels = np.fliplr(np.rot90(np.asarray(amg.pixels), k=3)).flatten()
    pixels_f = (9/5)*pixels+32
    grid_z = griddata(points, pixels_f, (grid_x, grid_y), method='cubic')
    #ax.clear()
    #surf = ax.plot_surface(grid_x, grid_y, grid_z, cmap="jet", linewidth=0, antialiased=False)
    #ax.view_init(80, angle)
    #ax.set_axis_off()
    
    flat_grid = grid_z.flatten()
    flat_grid = flat_grid[flat_grid >=65]
    flat_grid = flat_grid[flat_grid <=95]
    hist, bin_edges = np.histogram(flat_grid, bins=16)
    grid_z[grid_z < bin_edges[len(bin_edges) - 4]] = 0
    #ax1.clear()
    flat_grid = grid_z.flatten()
    filtered_flat_grid = flat_grid[flat_grid > 0]
    hist, bins = np.histogram(filtered_flat_grid, bins=16)
    #temp_hist = ax1.hist(bins[:-1], bins, weights=hist)
    temp = "{:.2f}".format(np.average(bins[:-1], weights = hist))
    std = "{:.2f}".format(np.std(filtered_flat_grid))
    count = "{:,.0f}".format(np.sum(filtered_flat_grid))
    if np.std(filtered_flat_grid) >= 0.5 and np.sum(filtered_flat_grid) >= 300000:
        print("Body temp found: {}".format(temp))
    #print(temp, std, count)        
     
    #fig.tight_layout()
    #fig.canvas.draw()

#plt.show()
