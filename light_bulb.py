import asyncio
import kasa
from itertools import cycle
import colorsys
import audioop
import pyaudio
import numpy as np
from time import sleep
import wave
##### CONFIGURATION #####

# Set up led configuration

RED_PIN   = 17
GREEN_PIN = 22
BLUE_PIN  = 24

SLEEP_TIME = 1.0

# Determine brightness and whether to switch direction
BRIGHTNESS_MULT = 1.0
TRANSITION_BRIGHTNESS = 1.0
LAST_DIR = "up"
UPDATE_BRIGHT = 0
COLOR_EFFECT = 3

# MODE VARIABLES
LISTEN = True
STATIC_LEVEL = 0.2
STATIC_SPEED = 0.02

# Tracks level history
LEVEL_HISTORY = []
LAST_LEVEL = 0.5

# Current color values
r = 255.0
g = 0.0
b = 0.0

CHANGE_SPEED = 3.0
LOWEST_BRIGHTNESS = 0.3

# scale      = 30    # Change if too dim/bright
scale      = 3    # Change if too dim/bright
# exponent   = 5     # Change if too little/too much difference between loud and quiet sounds
exponent   = 25     # Change if too little/too much difference between loud and quiet sounds

abort = False

# Set up audio configuration

CHUNK = 1024 * 16
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
DEVICE_INDEX = 0

#######

bulb = kasa.SmartBulb("172.26.174.229")

h, s, v = colorsys.rgb_to_hsv(r, g, b)

p = pyaudio.PyAudio()

file = 'sample.wav'
wf = wave.open(file, 'rb')

# input_stream = p.open(format=FORMAT,
#                       channels=CHANNELS,
#                       rate=RATE,
#                       input=True,
#                       frames_per_buffer=CHUNK,
#                       input_device_index=DEVICE_INDEX)
# input_stream = p.open(
#             format = p.get_format_from_width(wf.getsampwidth()),
#             channels = wf.getnchannels(),
#             rate = wf.getframerate(),
#             input = True,
#             frames_per_buffer=CHUNK,
# )
output_stream = p.open(
            format = p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)

### update level
def updateLevel(rms):
   global LEVEL_HISTORY, LAST_LEVEL, scale, exponent

   if len(LEVEL_HISTORY) < 50:
      LEVEL_HISTORY.append(rms)
      level = min(rms / (2.0 ** 16) * scale, 1.0)
      level = level**exponent
   else:
      avg = np.mean(LEVEL_HISTORY)
      if rms > avg:
         diff = rms-avg
         level = LAST_LEVEL + min(diff / (2.0 ** 16) * scale, (1.0-LAST_LEVEL))
      elif rms < avg:
         diff = avg-rms
         level = LAST_LEVEL - min(diff / (2.0 ** 16) * scale, (1.0-LAST_LEVEL))
      else:
         level = LAST_LEVEL
      LEVEL_HISTORY.pop(0)
      LEVEL_HISTORY.append(rms)
   return level

### update brightness
def updateBright(new_brightness):
   global BRIGHTNESS_MULT, TRANSITION_BRIGHTNESS, LAST_DIR, UPDATE_BRIGHT

   if new_brightness >= BRIGHTNESS_MULT:
      if LAST_DIR == "up" and UPDATE_BRIGHT == 0:
         TRANSITION_BRIGHTNESS = new_brightness
      LAST_DIR = "up"
      BRIGHTNESS_MULT = min(BRIGHTNESS_MULT + ((TRANSITION_BRIGHTNESS - BRIGHTNESS_MULT) / 3.0), 1.0)
   else:
      if LAST_DIR == "down" and UPDATE_BRIGHT == 0:
         TRANSITION_BRIGHTNESS = new_brightness
      LAST_DIR = "down"
      BRIGHTNESS_MULT = max(BRIGHTNESS_MULT - ((BRIGHTNESS_MULT - TRANSITION_BRIGHTNESS) / 3.0), 0.0)

   UPDATE_BRIGHT = UPDATE_BRIGHT - 1
   if UPDATE_BRIGHT < 0:
      UPDATE_BRIGHT = 3

def updateColors(level):
   global r, g, b, CHANGE_SPEED, COLOR_EFFECT

   amount = CHANGE_SPEED
   if level == 1.0:
      amount = amount + (amount*level)*COLOR_EFFECT
   elif level > 0.7:
      amount = amount + (amount*level)*2
   else:
      amount = amount - (amount*level)

   if r > 0 and b == 0:
      if r > amount:
         r -= amount
      else:
         r = 0.0
      if g < (255-amount):
         g += amount
      else:
         g = 255
   elif g > 0 and r == 0:
      if g > amount:
         g -= amount
      else:
         g = 0.0
      if b < (255-amount):
         b += amount
      else:
         b = 255
   else:
      if b > amount:
         b -= amount
      else:
         b = 0.0
      if r < (255-amount):
         r += amount
      else:
         r = 255

asyncio.run(bulb.turn_on())


count = 0

while True:
    if LISTEN:
        # Read data from device
        # if input_stream.is_stopped():
        #  input_stream.start_stream()

        data = wf.readframes(CHUNK)
        if data == b'':
            print("No data")
            break

        # input_stream.stop_stream()
        output_stream.write(data)
        print(count)
        count+=1


        rms = audioop.rms(data, 2)
        #
        level = updateLevel(rms)
        # # updateScale(level)
        #
        if level < LOWEST_BRIGHTNESS:
            level = LOWEST_BRIGHTNESS
        #
        updateBright(level)
        # updateColors(level)
        # # asyncio.run(bulb.turn_off())
        # # asyncio.run(bulb.turn_on())
        #
        # # normalize r,g,b in range 0-1
        # r_, g_, b_ = r/255., g/255., b/255.
        # print(f'R: {r_}, G: {g_}, B: {b_}')
        # h, s, v = colorsys.rgb_to_hsv(r_, g_, b_)
        # h, s, v = int(h*360), int(s*100), int(v*100)
        # print(f'HSV: {h}, {s}, {v}')
        #
        # asyncio.run(bulb.update())
        # asyncio.run(bulb.set_hsv(h, s, v))
        # print(f'Brightness: {BRIGHTNESS_MULT}')
        # asyncio.run(bulb.set_brightness(int(BRIGHTNESS_MULT*100)))
        # asyncio.run(bulb.set_brightness(0))


        if count % 2 == 0:
            asyncio.run(bulb.turn_on())
        else:
            asyncio.run(bulb.turn_off())

    else:
        print("========== Listening disabled ==========")
        updateColors(STATIC_LEVEL)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        h, s, v = int(h * 360), int(s * 100), int(v * 100)
        asyncio.run(bulb.update())
        asyncio.run(bulb.set_hsv(h, s, v))

        sleep(STATIC_SPEED)


asyncio.run(bulb.turn_off())



