import time
import math
import busio
import board
import adafruit_amg88xx
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.signal import find_peaks

vmax = 80
vmin = 63
plt.ion()
collecting_body_temps = False
body_temp_array = []
room_temp_array = []
collecting_room_temps = False
body_temp = 98.6
room_temp = 65.0
i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
#fig = plt.figure(num='AMG8833 Thermal Scanner');

#ax = fig.add_subplot(121)
#ax.set_yticklabels([])
#ax.set_xticklabels([])
#im = ax.imshow(amg.pixels, cmap='jet', vmin=vmin, vmax=vmax)
#fig.colorbar(im, ax=ax)
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:256j, 0:7:256j]

#ax2 = fig.add_subplot(122)

while True:
    #ax.set_title("Max Temp Found: {0:.1f}F".format(np.amax((9/5)*np.amax(amg.pixels)+32)))
    pixels = np.fliplr(np.rot90(np.asarray(amg.pixels), k=3)).flatten()
    pixels_f = (9/5)*pixels+32
    #ax.set_title("Max Temp Found: {0:.1f}F".format(np.amax(pixels_f )))
    grid_0 = griddata(points, pixels_f, (grid_x, grid_y), method='cubic')
    #im.set_data(grid_0)
    #ax2.clear()
    flat_grid = grid_0.flatten()
    hist, bin_edges = np.histogram(flat_grid, bins=256)
    #bar = ax2.bar(bin_edges[:-1], hist, width = 0.1, color='#0504aa',alpha=0.7)
    human_flat_grid = flat_grid[flat_grid > 70.0]
    human_flat_grid = human_flat_grid[human_flat_grid < 85.0]
    room_flat_grid = flat_grid[flat_grid > 50.0]
    room_flat_grid = room_flat_grid[room_flat_grid < 72.0]
    if len(room_flat_grid) > 0:
        hist, bin_edges = np.histogram(room_flat_grid, bins=256)
        bin_width = bin_edges[0] - bin_edges[1]
        peaks, _ = find_peaks(hist, height=150)
        if len(peaks) > 0:
            if collecting_room_temps:
                if np.std(room_temp_array) >0.1:
                    room_temp_array = room_temp_array[1:]
            room_temp = np.amax(bin_edges[peaks]) + bin_width / 2
            print("Room Temp: {0:.1f} - alpha: {1:.4f} - len() - {2}".format(np.average(room_temp), np.std(room_temp_array), len(room_temp_array)))

        
    if len(human_flat_grid) > 0:
        hist, bin_edges = np.histogram(human_flat_grid, bins=256)
        bin_width = bin_edges[0] - bin_edges[1]
        peaks, _ = find_peaks(hist, height=150)
        if len(peaks) > 0:
            if collecting_body_temps:
               if np.std(body_temp_array) > 1.0:
                    body_temp_array = body_temp_array[1:]
            human_temp = np.amax(bin_edges[peaks]) + bin_width / 2
            body_temp_array.append(human_temp)
            collecting_body_temps = True
            print("Human Temp: {0:.1f} - alpha: {1:.4f} - len() - {2}".format(np.average(human_temp), np.std(body_temp_array), len(body_temp_array)))
    else:
        collecting_body_temps = False
        body_temp_array = []
    #fig.canvas.draw()
