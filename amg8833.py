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

ax = fig.add_subplot(121)
ax.set_yticklabels([])
ax.set_xticklabels([])
im = ax.imshow(amg.pixels, cmap='jet', vmin=vmin, vmax=vmax)
fig.colorbar(im, ax=ax)
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:256j, 0:7:256j]

ax2 = fig.add_subplot(122)

while True:
    ax.set_title("Max Temp Found: {0:.1f}F".format(np.amax((9/5)*np.amax(amg.pixels)+32)))
    pixels = np.fliplr(np.rot90(np.asarray(amg.pixels), k=3)).flatten()
    pixels_f = (9/5)*pixels+32
    ax.set_title("Max Temp Found: {0:.1f}F".format(np.amax(pixels_f )))
    grid_0 = griddata(points, pixels_f, (grid_x, grid_y), method='cubic')
    im.set_data(grid_0)
    ax2.clear()
    hist = ax2.hist(grid_0, bins = 2)
    #hist.set_data(grid_0)
    fig.canvas.draw()
    
    ax = fig.add_subplot(111, projection='3d')
    xi = np.linspace(0, 256)
    yi = np.linspace(0, 256)
    X, Y = np.meshgrid(xi, yi)
    Z = griddata(x, y, z, xi, yi)
    surf = ax.plot_surface(X, Y, Z, rstride=6, cstride=6, cmap=cm.jet,
            linewidth=0)

ax.set_zlim3d(min(z), max(z))

ax.w_zaxis.set_major_locator(LinearLocator(10))
ax.w_zaxis.set_major_formatter(FormatStrFormatter('%.03f'))

fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()
