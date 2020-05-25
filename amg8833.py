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
import cv2

vmax = 80
vmin = 63
plt.ion()
collecting_body_temps = False
face_in_frame = False
body_temp_array = []
room_temp_array = []
body_temp = 98.6
room_temp = 65.0
peak_height_body = 80
i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('/home/pi/Scripts/therm/haarcascade_frontalface_default.xml')

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:128j, 0:7:128j]

def draw_label(img, text, pos, bg_color):
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    color = (0, 0, 0)
    thickness = cv2.FILLED
    margin = 2
    txt_size = cv2.getTextSize(text, font_face, scale, thickness)
    end_x = pos[0] + txt_size[0][0] + margin
    end_y = pos[1] - txt_size[0][1] - margin
    start_x = pos[0] - margin
    start_y = pos[1] + margin
    cv2.rectangle(img, (start_x, start_y), (end_x, end_y), bg_color, thickness)
    cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)

while True:
    ret, img = cap.read()
    img  = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
    face_sizes = []
    pixels = np.fliplr(np.rot90(np.asarray(amg.pixels), k=3)).flatten()
    pixels_f = (9/5)*pixels+32
    grid_0 = griddata(points, pixels_f, (grid_x, grid_y), method='cubic')
    flat_grid = grid_0.flatten()
    hist, bin_edges = np.histogram(flat_grid, bins=256)
    human_flat_grid = flat_grid[flat_grid > 70.0]
    human_flat_grid = human_flat_grid[human_flat_grid < 85.0]
    room_flat_grid = flat_grid[flat_grid > 50.0]
    room_flat_grid = room_flat_grid[room_flat_grid < 72.0]
    for (x, y, w, h) in faces:
        face_sizes.append(w*h)
        cv2.rectangle(img, (x-5, y-5), (x+w+5, y+h+5), (255, 255, 255), 2)
    
    if len(face_sizes) > 0:
        (x, y, w, h) = faces[np.argmax(face_sizes)]
        tx = int(x+w/2-150)
        ty = int(y+h/2-150)
        if tx < 0: tx = 0
        if ty < 0: ty = 0
        bx = tx + 300
        by = ty + 300
        if bx > 480:
            tx = tx - (bx-480)
            bx = tx + 300 
        img = img[ty:ty+300, tx:bx]
        faces = faces[np.argmax(face_sizes):np.argmax(face_sizes)+1]
        if len(faces) > 0 : #found a face in the frame 
            if not face_in_frame: #there was no face before but there is now
                body_temp_array = []
                face_in_frame = True
            if len(human_flat_grid) > 0:
                hist, bin_edges = np.histogram(human_flat_grid, bins=256)
                bin_width = bin_edges[0] - bin_edges[1]
                peaks, _ = find_peaks(hist, height=46)
                #while len(peaks) != 1:
                #    if len(peaks) > 1:
                #        peak_height_body = peak_height_body + 1
                #    if len(peaks) == 0:
                #        peak_height_body = peak_height_body - 1
                #    peaks, _ = find_peaks(hist, height=peak_height_body)
                #    print(peak_height_body)
                if len(peaks) > 0:
                    if collecting_body_temps:
                       if np.std(body_temp_array) > 0.50:
                            body_temp_array = body_temp_array[1:]
                    human_temp = np.amax(bin_edges[peaks]) + bin_width / 2
                    body_temp_array.append(human_temp)
                    collecting_body_temps = True
                    print("Human Temp: {0:.1f} - alpha: {1:.4f} - len() - {2}".format(np.average(body_temp_array), np.std(body_temp_array), len(body_temp_array)))
            else:
                collecting_body_temps = False
                body_temp_array = []
        else:
            if face_in_frame: #There was a face in the previous frame. but not now.
                x = 1 # we can send the twilio messages here.
                face_in_frame = False
            hist, bin_edges = np.histogram(room_flat_grid, bins=256)
            bin_width = bin_edges[0] - bin_edges[1]
            peaks, _ = find_peaks(hist, height=80)
            
            if len(peaks) > 0:
                if np.std(room_temp_array) >0.50 or len(room_temp_array) >= 64:
                    room_temp_array = room_temp_array[1:]
                room_temp = np.amax(bin_edges[peaks]) + bin_width / 2
                room_temp_array.append(room_temp)
                print("Room Temp: {0:.1f} - alpha: {1:.4f} - len() - {2}".format(np.average(room_temp_array), np.std(room_temp_array), len(room_temp_array)))

    else:
        tx = int(img.shape[1]/2 - 150)
        ty = int(img.shape[0]/2 - 150)
        img = img[ty:ty+300, tx:tx+300]
    
    cv2.imshow('therm', img)
    #out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
#out.release()
cv2.destroyAllWindows()
