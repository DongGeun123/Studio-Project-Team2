import os
import time
import signal
import subprocess

import asyncio
import kasa
from itertools import cycle
import colorsys
import time

bulb = kasa.SmartBulb("172.26.174.229")

def listen(t=10):
    spchcat_start = ['spchcat --language=en_US']

    fd_open = subprocess.Popen(spchcat_start, stdout=subprocess.PIPE,
                                text=True, shell=True, preexec_fn=os.setsid)
    time.sleep(t)
    os.killpg(os.getpgid(fd_open.pid), signal.SIGTERM)

    user_input = fd_open.stdout.read().strip()
    print(user_input)

    return user_input

async def bulb_color_control(color):
    # bulb2 = kasa.SmartBulb("172.26.174.228")

    if color == 'blue':
        r, g, b = 0, 0, 1
    elif color == 'red':
        r, g, b = 1, 0, 0
    elif color == 'green':
        r, g, b = 0, 1, 0
    elif color == 'yellow':
        r, g, b = 1, 1, 0

    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = int(h * 360)
    s = int(s * 100)
    v = int(v * 100)

    async def main():
        bulb = kasa.SmartBulb("172.26.174.229")
        try:
            await bulb.update()
            await bulb.turn_on()
            await bulb.set_hsv(h, s, 10)
        except asyncio.CancelledError:
            print("Cancelled")
    
    # asyncio.run(main())
    task = asyncio.create_task(main())
    await asyncio.sleep(1)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass


if __name__ == '__main__':
    # print(listen())
    # asyncio.run(bulb_color_control('blue'))
    # asyncio.run(bulb_color_control('yellow'))
    asyncio.run(bulb_color_control('yellow'))
    asyncio.run(bulb_color_control('red'))
