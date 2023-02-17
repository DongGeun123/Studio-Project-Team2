import asyncio
import gc

async def detect_ghost_loop():
    loops = 0
    for obj in gc.get_objects():
        if isinstance(obj, asyncio.AbstractEventLoop):
            loops += 1

    if loops > 1:
        print(f"Detected {loops} event loops, expected only 1.")

# Run this function periodically or when you suspect a ghost event loop
async def main():
    await detect_ghost_loop()

if __name__ == '__main__':
    asyncio.run(main())