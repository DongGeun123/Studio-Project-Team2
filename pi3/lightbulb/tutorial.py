import asyncio
import kasa
from itertools import cycle
import colorsys
from time import sleep

bulb = kasa.SmartBulb("172.26.174.229")

r, g, b = 0.2, 0.4, 0.4
h, s, v = colorsys.rgb_to_hsv(r, g, b)

async def main():
    for i in cycle(range(0,360,30)):
        print(i)
        await bulb.update()
        # await bulb.turn_on()
        await bulb.set_hsv(i+1, 100, 1)
        await asyncio.sleep(1)
        print(i)
#asyncio.run(bulb.turn_off())
#sleep(1)
#asyncio.run(bulb.turn_on())
#sleep(1)
#asyncio.run(bulb.update())
#sleep(1)
#print(bulb.is_on)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

